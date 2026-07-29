from __future__ import annotations

import unittest

from scripts.social_marketing_runtime.orchestrator import SocialMarketingRuntime
from scripts.social_marketing_runtime.tool_adapter import run_social_marketing


def completed_app() -> dict:
    return {
        "name": "CopyLift",
        "description": "CopyLift helps Shopify merchants turn raw product details into clear product-page copy designed for faster publishing and stronger conversion conversations.",
        "category": "saas",
        "status": "completed",
        "target_market": ["US"],
    }


class SocialMarketingRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = SocialMarketingRuntime()

    def test_missing_positioning_pauses_before_pipeline_execution(self):
        response = self.runtime.run({
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
        }, session_id="missing-positioning")

        self.assertEqual(response["status"], "needs_input")
        self.assertEqual(response["next_hil"]["field"], "target_audience")
        self.assertIsNone(response["result"])

    def test_completed_intake_runs_full_pipeline_and_returns_publishable_posts(self):
        response = self.runtime.run({
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
            "positioning": {
                "promo_goal": "Get 100 week-one signups from Shopify merchants",
                "target_audience": "Independent Shopify sellers with low-converting product pages",
                "key_selling_point": "Turn product details into conversion-focused product-page copy in minutes",
            },
            "positioning_confirmed": True,
            "probe_options": {"enable_realtime_probe": False, "no_network": True},
            "platform_scope": ["instagram", "youtube", "reddit"],
            "production_context": {"creator_constraints": {"weekly_content_capacity": "medium", "can_create_short_video": True}},
        }, session_id="complete-pack")

        self.assertEqual(response["status"], "completed")
        pack = response["result"]
        self.assertTrue(pack["publish_platforms"])
        self.assertGreaterEqual(len(pack["schedule"]["week_1"]), 3)
        for platform in pack["publish_platforms"]:
            posts = pack["deliverables"][platform]["posts"]
            self.assertTrue(posts)
            for post in posts:
                self.assertTrue(post["title"])
                self.assertTrue(post["body"])
                self.assertIn("discoverability", post)
                self.assertIn("creative", post)

    def test_no_network_pack_uses_evergreen_wording(self):
        response = self.runtime.run({
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
            "positioning": {
                "promo_goal": "Get early product feedback",
                "target_audience": "Shopify merchants who need clearer product-page copy",
                "key_selling_point": "Generate product-page copy from product details",
            },
            "positioning_confirmed": True,
            "probe_options": {"enable_realtime_probe": False, "no_network": True},
        }, session_id="evergreen-pack")

        self.assertEqual(response["status"], "completed")
        serialized = str(response["result"]).lower()
        self.assertNotIn("currently trending", serialized)
        self.assertNotIn("recently everyone", serialized)


    def test_usable_probe_is_routed_into_bounded_platform_adjustment(self):
        def fake_probe(stage_1, inputs):
            return {
                "platforms_attempted": ["reddit"],
                "briefs": [{
                    "platform": "reddit", "status": "usable", "freshness": "realtime",
                    "evidence_refs": ["reddit:p01:r01", "reddit:p02:r01"],
                }],
            }

        runtime = SocialMarketingRuntime(probe_runner=fake_probe)
        response = runtime.run({
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
            "positioning": {
                "promo_goal": "Get early product feedback",
                "target_audience": "Shopify merchants who need clearer product-page copy",
                "key_selling_point": "Generate product-page copy from product details",
            },
            "positioning_confirmed": True,
            "platform_scope": ["reddit"],
        }, session_id="probe-pack")

        self.assertEqual(response["status"], "completed")
        score = response["result"]["platform_fit"]["scores"]["reddit"]
        self.assertEqual(score["realtime_adjustment"], 4)
        self.assertEqual(response["result"]["_pipeline_meta"]["probe_meta"]["platforms_attempted"], ["reddit"])
    def test_default_probe_runner_executes_no_network_stage_2b(self):
        response = self.runtime.run({
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
            "positioning": {
                "promo_goal": "Get early product feedback",
                "target_audience": "Shopify merchants who need clearer product-page copy",
                "key_selling_point": "Generate product-page copy from product details",
            },
            "positioning_confirmed": True,
            "platform_scope": ["reddit"],
            "probe_options": {"enable_realtime_probe": True, "no_network": True},
        }, session_id="default-probe-pack")

        self.assertEqual(response["status"], "completed")
        self.assertEqual(response["result"]["_pipeline_meta"]["probe_meta"]["platforms_attempted"], ["reddit", "web_search"])
    def test_tool_adapter_preserves_hil_session_across_calls(self):
        session_id = "adapter-hil"
        common = {
            "app_context": completed_app(),
            "builder_prompt": "Build a focused copy assistant for Shopify merchants who need to publish better product pages without hiring a copywriter.",
            "positioning": {
                "promo_goal": "Get early product feedback",
                "target_audience": "Shopify merchants who need clearer product-page copy",
                "key_selling_point": "Generate product-page copy from product details",
            },
        }
        first = run_social_marketing(common, session_id=session_id)
        self.assertEqual(first["status"], "needs_input")
        self.assertEqual(first["next_hil"]["field"], "target_audience")

        second = run_social_marketing({"intake_operation": {"action": "confirm_candidate", "field": "target_audience"}}, session_id=session_id)
        self.assertEqual(second["status"], "needs_input")
        self.assertEqual(second["next_hil"]["field"], "promo_goal")
if __name__ == "__main__":
    unittest.main()
