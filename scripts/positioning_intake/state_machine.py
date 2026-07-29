"""Deterministic routing and confirmation for conversation/form positioning intake."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from intake_models import FIELDS, copy_positioning, empty_field, normalize_candidate

EXPLICIT_SOURCES = {"user_prompt", "app_context"}
MAX_CLARIFICATION_ATTEMPTS = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _valid_text(field: str, value: Any) -> str | None:
    text = str(value or "").strip()
    if len(text) < 3:
        return f"{field}_must_contain_at_least_3_characters"
    if len(text) > 500:
        return f"{field}_must_not_exceed_500_characters"
    return None


def _candidate_can_quick_confirm(field: dict[str, Any]) -> bool:
    return bool(
        field.get("value")
        and field.get("source") in EXPLICIT_SOURCES
        and field.get("confidence") == "high"
    )


def _all_confirmed(session: dict[str, Any]) -> bool:
    return all(session["fields"][field].get("user_confirmed") for field in FIELDS)


def _first_unconfirmed(session: dict[str, Any]) -> str | None:
    for field in ("target_audience", "promo_goal", "key_selling_point"):
        if not session["fields"][field].get("user_confirmed"):
            return field
    return None


def _option_list(field: str, session: dict[str, Any]) -> list[dict[str, str]]:
    options = list((session.get("suggested_options") or {}).get(field) or [])
    candidate = session["fields"][field]
    if candidate.get("value") and not any(item.get("label") == candidate["value"] for item in options if isinstance(item, dict)):
        options.insert(0, {
            "id": "candidate",
            "label": candidate["value"],
            "reason": "Extracted from supplied app context; requires your confirmation.",
            "source": candidate["source"],
        })
    normalized: list[dict[str, str]] = []
    for index, option in enumerate(options[:5], start=1):
        if not isinstance(option, dict):
            continue
        label = str(option.get("label") or "").strip()
        if not label:
            continue
        normalized.append({
            "id": str(option.get("id") or f"{field}_{index}"),
            "label": label[:240],
            "reason": str(option.get("reason") or "Suggested from the supplied context.")[:240],
            "source": str(option.get("source") or "unknown"),
        })
    return normalized


def _question(session: dict[str, Any]) -> dict[str, Any] | None:
    route = session["route"]
    if route == "ready":
        return None
    if route == "quick_confirm":
        return {
            "kind": "confirm_all",
            "summary": copy_positioning(session["fields"]),
            "allow_edit": True,
            "allow_switch_to_form": True,
        }
    if route == "form_fallback":
        return {"kind": "form", "form_prefill": session["form_prefill"], "reason": session.get("reason"), "allow_switch_back": True}
    field = session["next_field"]
    return {
        "kind": "field_clarification",
        "field": field,
        "allow_multi_select": field == "target_audience",
        "max_selections": 2 if field == "target_audience" else 1,
        "options": _option_list(field, session),
        "allow_custom": True,
        "allow_switch_to_form": True,
    }


def _refresh(session: dict[str, Any]) -> dict[str, Any]:
    if _all_confirmed(session):
        session["route"] = "ready"
        session["next_field"] = None
        session["handoff"] = {
            "positioning": copy_positioning(session["fields"]),
            "intake_meta": {
                "mode": "conversation_clarifier" if session["mode"] != "form" else "hil_form",
                "field_sources": {field: session["fields"][field]["source"] for field in FIELDS},
                "user_confirmed_at": _utc_now(),
            },
        }
    elif any(session["clarification_attempts"][field] >= MAX_CLARIFICATION_ATTEMPTS for field in FIELDS):
        session["route"] = "form_fallback"
        session["next_field"] = None
        session["handoff"] = None
        session["reason"] = "clarification_attempt_limit_reached"
    else:
        session["route"] = "clarify"
        session["next_field"] = _first_unconfirmed(session)
        session["handoff"] = None
    session["form_prefill"] = copy_positioning(session["fields"])
    session["question"] = _question(session)
    return session


def start(candidate_extraction: dict[str, Any], suggested_options: dict[str, list[dict[str, Any]]] | None = None, session_id: str | None = None) -> dict[str, Any]:
    candidates = candidate_extraction if isinstance(candidate_extraction, dict) else {}
    fields = {field: normalize_candidate(candidates.get(field)) for field in FIELDS}
    session: dict[str, Any] = {
        "schema_version": "0.3.0",
        "session_id": session_id,
        "mode": "auto",
        "route": "clarify",
        "next_field": None,
        "fields": fields,
        "clarification_attempts": {field: 0 for field in FIELDS},
        "suggested_options": suggested_options or {},
        "form_prefill": copy_positioning(fields),
        "question": None,
        "handoff": None,
    }
    if all(_candidate_can_quick_confirm(fields[field]) for field in FIELDS):
        session["route"] = "quick_confirm"
        session["question"] = _question(session)
        return session
    return _refresh(session)


def switch_to_form(session: dict[str, Any]) -> dict[str, Any]:
    session = dict(session)
    session["mode"] = "form"
    session["route"] = "form_fallback"
    session["next_field"] = None
    session["handoff"] = None
    session["reason"] = "user_requested_form"
    session["form_prefill"] = copy_positioning(session["fields"])
    session["question"] = _question(session)
    return session


def submit_form(session: dict[str, Any], positioning: dict[str, Any]) -> dict[str, Any]:
    session = dict(session)
    errors = {field: _valid_text(field, (positioning or {}).get(field)) for field in FIELDS}
    errors = {field: error for field, error in errors.items() if error}
    if errors:
        session["route"] = "form_fallback"
        session["reason"] = "invalid_form_submission"
        session["validation_errors"] = errors
        session["question"] = _question(session)
        return session
    for field in FIELDS:
        session["fields"][field] = {
            "value": str(positioning[field]).strip(), "source": "form", "evidence_excerpt": None,
            "confidence": "high", "status": "confirmed", "user_confirmed": True,
        }
    session["mode"] = "form"
    return _refresh(session)


def _invalid_answer(session: dict[str, Any], field: str, reason: str) -> dict[str, Any]:
    session["clarification_attempts"][field] += 1
    session["fields"][field]["status"] = "invalid"
    session["reason"] = reason
    return _refresh(session)


def answer(session: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    session = dict(session)
    operation = operation if isinstance(operation, dict) else {}
    action = operation.get("action")
    if action == "switch_to_form":
        return switch_to_form(session)
    if action == "submit_form":
        return submit_form(session, operation.get("positioning") or {})
    if action == "confirm_all_candidates":
        if session.get("route") != "quick_confirm":
            return session
        for field in FIELDS:
            session["fields"][field]["status"] = "confirmed"
            session["fields"][field]["user_confirmed"] = True
        return _refresh(session)
    field = operation.get("field")
    if field not in FIELDS:
        return session
    if action == "confirm_candidate":
        candidate = session["fields"][field]
        if not candidate.get("value"):
            return _invalid_answer(session, field, "missing_candidate")
        candidate["status"] = "confirmed"
        candidate["user_confirmed"] = True
        return _refresh(session)
    if action == "submit_custom":
        text = operation.get("text")
        error = _valid_text(field, text)
        if error:
            return _invalid_answer(session, field, error)
        session["fields"][field] = {
            "value": str(text).strip(), "source": "user_custom", "evidence_excerpt": None,
            "confidence": "high", "status": "confirmed", "user_confirmed": True,
        }
        return _refresh(session)
    if action == "select_options":
        selected = [str(value) for value in operation.get("option_ids") or []]
        choices = {item["id"]: item for item in _option_list(field, session)}
        max_count = 2 if field == "target_audience" else 1
        if not selected or len(selected) > max_count or any(value not in choices for value in selected):
            return _invalid_answer(session, field, "invalid_option_selection")
        value = "; ".join(choices[item]["label"] for item in selected)
        session["fields"][field] = {
            "value": value, "source": "user_selected", "evidence_excerpt": None,
            "confidence": "high", "status": "confirmed", "user_confirmed": True,
        }
        return _refresh(session)
    return _invalid_answer(session, field, "unsupported_operation")
