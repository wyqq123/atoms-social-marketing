from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "scripts" / "positioning_intake"
FIXTURES = ROOT / "tests" / "fixtures" / "positioning_intake"
sys.path.insert(0, str(INTAKE_DIR))

from state_machine import answer, start


class PositioningIntakeTests(unittest.TestCase):
    def fixture(self, name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8-sig"))

    def test_complete_prompt_requires_user_confirmation(self):
        session = start(self.fixture("complete_prompt.json"), session_id="s1")
        self.assertEqual(session["route"], "quick_confirm")
        self.assertIsNone(session["handoff"])
        completed = answer(session, {"action": "confirm_all_candidates"})
        self.assertEqual(completed["route"], "ready")
        self.assertEqual(completed["handoff"]["positioning"]["target_audience"], "Shopify independent sellers")

    def test_missing_audience_is_first_clarification(self):
        session = start(self.fixture("missing_audience.json"))
        self.assertEqual(session["route"], "clarify")
        self.assertEqual(session["next_field"], "target_audience")
        self.assertEqual(session["question"]["field"], "target_audience")

    def test_builder_identity_never_qualifies_for_quick_confirmation(self):
        session = start(self.fixture("builder_identity_conflict.json"))
        self.assertEqual(session["route"], "clarify")
        self.assertEqual(session["next_field"], "target_audience")

    def test_custom_values_complete_conversation_and_keep_user_source(self):
        session = start(self.fixture("missing_audience.json"))
        session = answer(session, {"action": "submit_custom", "field": "target_audience", "text": "Shopify sellers with low-converting product pages"})
        self.assertEqual(session["next_field"], "promo_goal")
        session = answer(session, {"action": "confirm_candidate", "field": "promo_goal"})
        session = answer(session, {"action": "confirm_candidate", "field": "key_selling_point"})
        self.assertEqual(session["route"], "ready")
        self.assertEqual(session["handoff"]["intake_meta"]["field_sources"]["target_audience"], "user_custom")

    def test_form_switch_preserves_prefill_and_form_submission_is_ready(self):
        session = start(self.fixture("missing_audience.json"))
        switched = answer(session, {"action": "switch_to_form"})
        self.assertEqual(switched["route"], "form_fallback")
        self.assertEqual(switched["form_prefill"]["promo_goal"], "Get 100 week-one signups")
        completed = answer(switched, {"action": "submit_form", "positioning": {
            "promo_goal": "Get 100 week-one signups", "target_audience": "Shopify independent sellers",
            "key_selling_point": "Generate product-page copy from product details"
        }})
        self.assertEqual(completed["route"], "ready")
        self.assertEqual(completed["handoff"]["intake_meta"]["mode"], "hil_form")

    def test_two_invalid_answers_fall_back_to_form(self):
        session = start(self.fixture("missing_audience.json"))
        session = answer(session, {"action": "submit_custom", "field": "target_audience", "text": "x"})
        session = answer(session, {"action": "submit_custom", "field": "target_audience", "text": "y"})
        self.assertEqual(session["route"], "form_fallback")
        self.assertEqual(session["reason"], "clarification_attempt_limit_reached")

    def test_option_selection_supports_two_audiences(self):
        session = start(self.fixture("missing_audience.json"), {"target_audience": [
            {"id": "a1", "label": "Shopify sellers"}, {"id": "a2", "label": "Small ecommerce teams"}
        ]})
        selected = answer(session, {"action": "select_options", "field": "target_audience", "option_ids": ["a1", "a2"]})
        self.assertTrue(selected["fields"]["target_audience"]["user_confirmed"])
        self.assertIn("Shopify sellers", selected["fields"]["target_audience"]["value"])

    def test_cli_round_trip_returns_quick_confirmation(self):
        request = {"action": "start", "candidate_extraction": self.fixture("complete_prompt.json"), "session_id": "cli"}
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            output_path = Path(tmp) / "output.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            subprocess.run([sys.executable, str(INTAKE_DIR / "run_positioning_intake.py"), "--request", str(request_path), "--output", str(output_path)], check=True, cwd=ROOT)
            session = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(session["route"], "quick_confirm")
            request_path.write_text(json.dumps({
                "action": "answer", "session": session,
                "operation": {"action": "confirm_all_candidates"}
            }), encoding="utf-8")
            subprocess.run([sys.executable, str(INTAKE_DIR / "run_positioning_intake.py"), "--request", str(request_path), "--output", str(output_path)], check=True, cwd=ROOT)
            completed = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(completed["route"], "ready")
            self.assertTrue(completed["handoff"]["positioning"]["promo_goal"])


if __name__ == "__main__":
    unittest.main()
