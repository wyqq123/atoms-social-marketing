from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "scripts" / "realtime_probe"
sys.path.insert(0, str(PROBE_DIR))

from adapters import reddit_probe, web_search_probe, youtube_probe
from cache_store import cache_key, is_fresh
from models import PlatformQuery, contains_forbidden_fields
from query_planner import plan_queries
from models import AdapterResult
from run_realtime_probe import main as run_main
from summarize_opportunity_brief import summarize
from validate_probe_output import validate_brief, validate_item

FIXTURES = ROOT / "tests" / "fixtures" / "platform_intel"


class RealtimeProbeTests(unittest.TestCase):
    def load_fixture(self, name: str):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_query_planner_caps_and_variants(self):
        probes = self.load_fixture("demand_probe_pack_saas_founder.json")
        queries = plan_queries("reddit", probes, 3)
        self.assertLessEqual(len(queries), 3)
        self.assertTrue(any(q["variant_type"] == "platform_native" for q in queries))
        self.assertFalse(any(q["query"].lower() in {"atoms", "runtime"} for q in queries))

    def test_normalizers_emit_evidence_items(self):
        yt_query = PlatformQuery(platform="youtube", probe_id="p02", query="x", surface="youtube_search")
        yt_items = youtube_probe.normalize([{
            "query": yt_query,
            "video": {
                "id": "abc123",
                "snippet": {"title": "Shopify seller product page conversion tutorial", "description": "Improve product page conversion", "publishedAt": "2026-07-20T00:00:00Z", "channelTitle": "Demo", "channelId": "c1"},
                "statistics": {"viewCount": "1000", "likeCount": "50", "commentCount": "4"},
                "contentDetails": {"duration": "PT2M10S"}
            }
        }])
        self.assertEqual(yt_items[0]["source_type"], "official_api")
        reddit_query = PlatformQuery(platform="reddit", probe_id="p01", query="x", surface="subreddit_search")
        reddit_items = reddit_probe.normalize([{
            "query": reddit_query,
            "post": {"title": "Shopify seller product page traffic no sales", "selftext": "Need help", "subreddit": "ecommerce", "score": 12, "num_comments": 5, "created_utc": 1784592000, "permalink": "/r/ecommerce/comments/x/test"}
        }])
        self.assertEqual(reddit_items[0]["platform"], "reddit")
        web_query = PlatformQuery(platform="web_search", probe_id="p01", query="site:reddit.com/r x", surface="public_search_result")
        web_items = web_search_probe.normalize([{
            "query": web_query,
            "result": {"title": "Shopify seller traffic no sales", "snippet": "product page traffic no sales", "link": "https://www.reddit.com/r/ecommerce/test"}
        }])
        self.assertEqual(web_items[0]["source_type"], "authorized_search_connector")

    def test_missing_credentials_preflight(self):
        self.assertFalse(youtube_probe.preflight({}).can_run)
        self.assertFalse(reddit_probe.preflight({}).can_run)
        self.assertFalse(web_search_probe.preflight({}).can_run)

    def test_summarize_and_validate_degrades_single_ref(self):
        probes = self.load_fixture("demand_probe_pack_saas_founder.json")
        items = [{
            "evidence_id": "reddit:p01:r01", "platform": "reddit", "probe_id": "p01", "surface": "subreddit_search",
            "title": "Shopify seller product page traffic no sales", "url": "https://reddit.com/r/ecommerce/test",
            "published_at": "2026-07-26T00:00:00Z", "text_excerpt": "Shopify seller has product page traffic no sales",
            "metrics": {"score": 1, "comments": 0}, "source_type": "official_api", "known_biases": ["search_result_bias"]
        }]
        brief = summarize(items, probes, "reddit")
        self.assertEqual(brief["status"], "weak")
        self.assertEqual(validate_brief(brief), [])
        brief["fit_score"] = 99
        self.assertTrue(validate_brief(brief))
        self.assertEqual(contains_forbidden_fields(brief), ["fit_score"])

    def test_validate_item_policy(self):
        item = {"evidence_id": "x", "source_type": "bad", "text_excerpt": "x" * 10}
        self.assertTrue(validate_item(item))

    def test_cache_key_and_freshness(self):
        key = cache_key("reddit", "US", "en", "Shopify Seller", "traffic no sales", "2026-W31")
        self.assertIn("|", key)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = Path(tmp.name)
        try:
            self.assertTrue(is_fresh(path, 24))
        finally:
            path.unlink(missing_ok=True)


    def test_runner_mixed_mock_results(self):
        import run_realtime_probe as runner
        app_icp = self.load_fixture("app_icp_saas_founder.json")
        probes = self.load_fixture("demand_probe_pack_saas_founder.json")
        registry = json.loads((ROOT / "data" / "platform_registry.json").read_text(encoding="utf-8"))

        def fake_run_adapter(platform, queries, args, registry_payload):
            report = {"platform": platform, "status": "success", "started_at": "2026-07-27T00:00:00Z", "latency_ms": 1, "queries_attempted": len(queries), "items_fetched": 2, "items_after_dedupe": 2, "errors": [], "capability": {"runtime_access_mode": "realtime_api"}}
            if platform == "reddit":
                report["status"] = "skipped"
                report["items_fetched"] = 0
                report["items_after_dedupe"] = 0
                report["errors"] = ["missing_REDDIT_CLIENT_ID"]
                return AdapterResult(platform, "skipped", [], report, ["missing_REDDIT_CLIENT_ID"])
            if platform == "youtube":
                items = [
                    {"evidence_id": "youtube:p02:v01", "platform": "youtube", "probe_id": "p02", "surface": "youtube_search", "title": "Shopify seller improve product page conversion tutorial", "url": "https://youtube.com/watch?v=1", "published_at": "2026-07-26T00:00:00Z", "text_excerpt": "Shopify seller improve product page conversion", "metrics": {"views": 2000, "comments": 4}, "source_type": "official_api", "known_biases": ["youtube_search_ranking_bias"]},
                    {"evidence_id": "youtube:p02:v02", "platform": "youtube", "probe_id": "p02", "surface": "youtube_search", "title": "Product page traffic no sales Shopify seller", "url": "https://youtube.com/watch?v=2", "published_at": "2026-07-25T00:00:00Z", "text_excerpt": "product page traffic no sales", "metrics": {"views": 1000, "comments": 2}, "source_type": "official_api", "known_biases": ["youtube_search_ranking_bias"]}
                ]
                return AdapterResult(platform, "success", items, report, [])
            items = [
                {"evidence_id": "web_search:p01:w01", "platform": "web_search", "probe_id": "p01", "surface": "public_search_result", "title": "Shopify seller product page traffic no sales", "url": "https://reddit.com/r/ecommerce/a", "observed_at": "2026-07-27T00:00:00Z", "text_excerpt": "Shopify seller product page traffic no sales", "metrics": {}, "source_type": "authorized_search_connector", "known_biases": ["snippet_only"]},
                {"evidence_id": "web_search:p01:w02", "platform": "web_search", "probe_id": "p01", "surface": "public_search_result", "title": "Product page traffic no sales Shopify", "url": "https://reddit.com/r/shopify/b", "observed_at": "2026-07-27T00:00:00Z", "text_excerpt": "product page traffic no sales", "metrics": {}, "source_type": "authorized_search_connector", "known_biases": ["snippet_only"]}
            ]
            return AdapterResult(platform, "success", items, report, [])

        args = type("Args", (), {
            "platform_registry": str(ROOT / "data" / "platform_registry.json"),
            "app_icp": str(FIXTURES / "app_icp_saas_founder.json"),
            "demand_probes": str(FIXTURES / "demand_probe_pack_saas_founder.json"),
            "platform_scope": ["reddit", "youtube"],
            "max_platforms": 3,
            "timeout_ms": 8000,
            "per_platform_timeout_ms": 2500,
            "queries_per_platform": 3,
            "results_per_query": 6,
            "fresh_cache_max_age_hours": 24,
            "cache_file": None,
            "cache_root": None,
            "write_raw_cache": False,
            "web_provider": "google_cse",
            "no_network": False,
        })()
        with patch.object(runner, "_run_adapter", side_effect=fake_run_adapter):
            payload = runner.run(args)
        statuses = {brief["platform"]: brief["status"] for brief in payload["briefs"]}
        self.assertEqual(statuses["reddit"], "skipped")
        self.assertEqual(statuses["youtube"], "usable")
        self.assertIn(statuses["web_search"], {"usable", "weak"})
        for brief in payload["briefs"]:
            self.assertEqual(validate_brief(brief), [])

    def test_runner_no_network_outputs_valid(self):
        app_icp = FIXTURES / "app_icp_saas_founder.json"
        probes = FIXTURES / "demand_probe_pack_saas_founder.json"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "briefs.json"
            old_argv = sys.argv
            sys.argv = ["run_realtime_probe.py", "--app-icp", str(app_icp), "--demand-probes", str(probes), "--platform-registry", str(ROOT / "data" / "platform_registry.json"), "--platform-scope", "reddit", "youtube", "--no-network", "--output", str(output)]
            try:
                run_main()
            finally:
                sys.argv = old_argv
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(payload["briefs"]), 2)
            for brief in payload["briefs"]:
                self.assertEqual(validate_brief(brief), [])


if __name__ == "__main__":
    unittest.main()
