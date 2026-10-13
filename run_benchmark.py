"""
End-to-End Voice AI Benchmark & Diagnostic Runner for SquadStack.
Executes test calls across diverse customer personas, runs the evaluation harness,
stores data in SQL, and generates actionable diagnosis reports.
"""

import sys
import uuid
from prompts import SIMULATION_PERSONAS
from voice_agent import VoiceAgent
from evaluator import CallEvaluator
from analytics_db import AnalyticsDatabase

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_full_benchmark():
    agent = VoiceAgent(agent_name="Priya", client_brand="AngelOne")
    evaluator = CallEvaluator(max_words_per_turn=25)
    db = AnalyticsDatabase()

    print("=" * 80)
    print("SQUADSTACK VOICE AI: AUTOMATED EVALUATION & DIAGNOSTIC BENCHMARK")
    print("=" * 80)

    for persona_id, p_data in SIMULATION_PERSONAS.items():
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        agent.reset()

        print(f"\n--- Testing Persona: {p_data['name']} [{persona_id}] ---")
        print(f"Scenario Context: {p_data['description']}")
        print(f"Target Outcome:   {p_data['expected_outcome']}")
        print("-" * 60)

        # 1. Turn 1: Customer initial utterance
        cust_u1 = p_data["first_utterance"]
        print(f"  [Customer]: \"{cust_u1}\"")
        resp1 = agent.generate_response(cust_u1, customer_name=p_data["name"])
        print(f"  [Agent]   : \"{resp1['response']}\" (Words: {resp1['word_count']}, Stage: {resp1['stage']})")

        # 2. Subsequent turns
        for follow_up in p_data["follow_ups"]:
            print(f"  [Customer]: \"{follow_up}\"")
            resp = agent.generate_response(follow_up, customer_name=p_data["name"])
            print(f"  [Agent]   : \"{resp['response']}\" (Words: {resp['word_count']}, Stage: {resp['stage']})")

        # 3. Diagnostic Evaluation
        agent_state = {
            "callback_time": agent.callback_time,
            "link_sent": agent.link_sent,
            "dnd_opted": agent.dnd_opted
        }
        eval_result = evaluator.evaluate_full_call(agent.history, p_data["expected_outcome"], agent_state)

        # 4. Save to SQL Database
        db.record_call(
            call_id=call_id,
            persona_id=persona_id,
            customer_name=p_data["name"],
            expected_outcome=p_data["expected_outcome"],
            eval_result=eval_result,
            history=agent.history,
            stage=agent.current_stage
        )

        # 5. Output Diagnostic Card
        verdict_icon = "[PASS]" if eval_result["verdict"] == "SUCCESS" else ("[PARTIAL]" if "PARTIAL" in eval_result["verdict"] else "[FAIL]")
        print(f"\n  [DIAGNOSTIC VERDICT]: {verdict_icon} {eval_result['verdict']}")
        print(f"  Overall Quality Score : {eval_result['overall_score']} / 10.0")
        print(f"  ├── Brevity Score     : {eval_result['brevity_score']} / 10.0 (Violations: {eval_result['brevity_violations']})")
        print(f"  ├── Hinglish Natural  : {eval_result['naturalness_score']} / 10.0")
        print(f"  ├── Compliance Score  : {eval_result['compliance_score']} / 10.0")
        print(f"  └── Goal Completion   : {eval_result['goal_score']} / 10.0")
        if eval_result["failure_reasons"]:
            print("  Root Causes:", eval_result["failure_reasons"])

    # 6. SQL Analytics KPI Summary
    print("\n" + "=" * 80)
    print("SQL CONVERSATIONAL ANALYTICS REPORT (Platform Overview)")
    print("=" * 80)
    kpis = db.run_kpi_report()
    overall = kpis["kpis"]
    print(f"Total Call Sessions Analyzed : {overall.get('total_calls')}")
    print(f"Overall Platform Success Rate: {round(overall.get('successful_calls', 0) / max(overall.get('total_calls', 1), 1) * 100, 1)}%")
    print(f"Average Conversational Score : {overall.get('avg_score')} / 10.0")
    print(f"Average Words/Brevity Score  : {overall.get('avg_brevity')} / 10.0")
    print(f"Average Turns per Call       : {overall.get('avg_turns_per_call')} turns")

    print("\nPersona Success Rate Breakdown (via SQL GROUP BY):")
    for p in kpis["persona_performance"]:
        print(f"  • {p['persona_id']:<20} | Calls: {p['calls_count']} | Avg Score: {p['avg_score']:<4} | Success: {p['success_rate_pct']}%")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETED SUCCESSFULLY.")
    print("=" * 80)


if __name__ == "__main__":
    run_full_benchmark()
