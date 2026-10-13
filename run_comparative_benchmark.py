"""
SquadStack Voice AI: Comprehensive Multi-Bot Comparative Benchmark.
Executes 18 un-tuned test scenarios across:
1. Rule-Based Baseline Bot
2. Gemini Voice Agent (Prompt V1 - Initial Few-Shot)
3. Gemini Voice Agent (Prompt V2 - Iterated Few-Shot based on Metrics)

Calculates Before/After scores, failure distributions, and SQL analytics.
"""

import sys
import uuid
import os
from scenarios import TEST_SCENARIOS
from voice_agent import VoiceAgent
from gemini_agent import GeminiVoiceAgent
from evaluator import CallEvaluator
from analytics_db import AnalyticsDatabase

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_benchmark_for_bot(bot, bot_name: str, evaluator: CallEvaluator, db: AnalyticsDatabase):
    print(f"\n{'=' * 80}")
    print(f"RUNNING BENCHMARK: {bot_name.upper()}")
    print(f"{'=' * 80}")

    for s in TEST_SCENARIOS:
        call_id = f"{bot_name[:6]}_{s['id'][:10]}_{uuid.uuid4().hex[:4]}"
        bot.reset()

        # Run multi-turn dialogue
        for utterance in s["dialogue"]:
            bot.generate_response(utterance, customer_name=s["customer_name"])

        # Collect state
        agent_state = {
            "callback_time": getattr(bot, "callback_time", None),
            "link_sent": getattr(bot, "link_sent", False),
            "dnd_opted": getattr(bot, "dnd_opted", False),
            "status_verified": getattr(bot, "status_verified", False)
        }

        eval_result = evaluator.evaluate_full_call(
            history=bot.history,
            expected_outcome=s["expected_outcome"],
            agent_state=agent_state,
            key_question=s.get("key_question")
        )

        db.record_call(
            call_id=call_id,
            bot_type=bot_name,
            scenario_id=s["id"],
            customer_name=s["customer_name"],
            category=s["category"],
            expected_outcome=s["expected_outcome"],
            eval_result=eval_result
        )

        # Print concise scenario status line
        status_tag = "[PASS]" if eval_result["verdict"] == "SUCCESS" else ("[PARTIAL]" if "PARTIAL" in eval_result["verdict"] else "[FAIL]")
        print(f"  {status_tag} {s['id']:<34} | Score: {eval_result['overall_score']:<4} | QA: {eval_result['qa_score']:<4} | Verdict: {eval_result['verdict']}")
        if eval_result["failure_reasons"]:
            print(f"       └── Gaps: {eval_result['failure_reasons']}")


def main():
    db_file = os.path.join(os.path.dirname(__file__), "conversations.db")
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass

    evaluator = CallEvaluator(max_words_per_turn=25)
    db = AnalyticsDatabase()

    print("\n" + "=" * 80)
    print("SQUADSTACK VOICE AI PLATFORM: RIGOROUS THREE-WAY COMPARATIVE EVALUATION")
    print("Testing 18 Un-Tuned Scenarios across Messy Hinglish, Multi-Objections & Edge Cases")
    print("=" * 80)

    # 1. Rule-Based Baseline
    baseline_bot = VoiceAgent()
    run_benchmark_for_bot(baseline_bot, "rule_based_baseline", evaluator, db)

    # 2. Gemini Few-Shot V1
    gemini_v1 = GeminiVoiceAgent(prompt_version="v1")
    run_benchmark_for_bot(gemini_v1, "gemini_prompt_v1", evaluator, db)

    # 3. Gemini Iterated Few-Shot V2
    gemini_v2 = GeminiVoiceAgent(prompt_version="v2")
    run_benchmark_for_bot(gemini_v2, "gemini_prompt_v2", evaluator, db)

    # 4. Generate Comparative SQL Analytics
    print("\n" + "=" * 80)
    print("SQL COMPARATIVE ANALYTICS & ITERATION IMPACT REPORT")
    print("=" * 80)

    report = db.run_comparative_report()
    summary = report["comparative_summary"]

    print(f"\n{'Bot Architecture / Prompt':<24} | {'Pass Rate':<9} | {'Overall':<7} | {'Brevity':<7} | {'QA Fidelity':<11} | {'Brevity Violations'}")
    print("-" * 88)
    for row in summary:
        print(f"{row['bot_type']:<24} | {row['pass_rate_pct']:>7}% | {row['avg_overall_score']:>7} | {row['avg_brevity']:>7} | {row['avg_qa_fidelity']:>11} | {row['total_brevity_violations']:>18}")

    print("\n" + "=" * 80)
    print("PROMPT ITERATION DELTA (Gemini V1 -> Gemini V2 Improvement Story)")
    print("=" * 80)

    v1_data = next((r for r in summary if r["bot_type"] == "gemini_prompt_v1"), {})
    v2_data = next((r for r in summary if r["bot_type"] == "gemini_prompt_v2"), {})
    base_data = next((r for r in summary if r["bot_type"] == "rule_based_baseline"), {})

    if v1_data and v2_data:
        pass_diff = round(v2_data["pass_rate_pct"] - v1_data["pass_rate_pct"], 1)
        score_diff = round(v2_data["avg_overall_score"] - v1_data["avg_overall_score"], 2)
        qa_diff = round(v2_data["avg_qa_fidelity"] - v1_data["avg_qa_fidelity"], 2)
        brevity_viol_reduction = v1_data["total_brevity_violations"] - v2_data["total_brevity_violations"]

        print(f"• Pass Rate Increase      : +{pass_diff}%  ({v1_data['pass_rate_pct']}% -> {v2_data['pass_rate_pct']}%)")
        print(f"• Overall Quality Score    : +{score_diff} pts ({v1_data['avg_overall_score']} -> {v2_data['avg_overall_score']})")
        print(f"• Question Answering Delta : +{qa_diff} pts ({v1_data['avg_qa_fidelity']} -> {v2_data['avg_qa_fidelity']})")
        print(f"• Word Budget Violations   : -{brevity_viol_reduction} violations ({v1_data['total_brevity_violations']} -> {v2_data['total_brevity_violations']})")

    print("\nRoot-Cause Failure Distributions Recorded by Bot Variant:")
    for f in report["failures_by_bot"]:
        print(f"  • [{f['bot_type']}] {f['failure_reason']} (Count: {f['count']})")

    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION COMPLETED.")
    print("=" * 80)


if __name__ == "__main__":
    main()
