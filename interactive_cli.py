"""
Interactive CLI for testing and debugging SquadStack Voice AI Agent.
Powered by Live Google Gemini 2.5 Flash with Anti-Repetition & Stateful Multi-Turn Memory.
Allows real-time voice simulation in English or Hinglish with turn-by-turn telemetry.
"""

import sys
from gemini_agent import GeminiVoiceAgent
from voice_agent import VoiceAgent
from evaluator import CallEvaluator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    evaluator = CallEvaluator(max_words_per_turn=25)

    print("=" * 72)
    print("SQUADSTACK VOICE AI: LIVE INTERACTIVE AGENT CONSOLE")
    print("=" * 72)
    print("Select Engine:")
    print("  [1] Gemini 2.5 Flash (Live AI - Stateful & Dynamic) [DEFAULT]")
    print("  [2] Rule-Based Baseline (Static Rules)")
    choice = input("Enter choice (1/2, default 1): ").strip()

    if choice == "2":
        agent = VoiceAgent(agent_name="Priya", client_brand="AngelOne")
        engine_label = "Rule-Based Baseline (Static Rules)"
    else:
        agent = GeminiVoiceAgent(prompt_version="v2", agent_name="Priya")
        if agent.client:
            engine_label = "Live Google Gemini 2.5 Flash (Cloud Connected)"
        else:
            engine_label = "Gemini Simulation Engine (Local Prompt Modeled)"

    print("-" * 72)
    print(f"Active Engine: {engine_label}")
    print("Speak/type as a customer in English or Hinglish.")
    print("Type 'exit' or 'quit' to end call and inspect full session evaluation.")
    print("=" * 72)

    customer_name = input("\nEnter Customer Name (Default: Rahul): ").strip() or "Rahul"
    print(f"\n📞 [Outbound Call Connected to {customer_name}]...\n")

    # Initial Greeting
    resp0 = agent.generate_response(f"Hello, {customer_name} speaking.", customer_name=customer_name)
    print(f"📞 Priya: \"{resp0['response']}\"")
    print(f"   [Telemetry: {resp0['word_count']} words | Stage: {resp0['stage']}]\n")

    while True:
        try:
            user_input = input(f"👤 {customer_name}: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye", "hangup"]:
                break

            resp = agent.generate_response(user_input, customer_name=customer_name)
            turn_eval = evaluator.evaluate_turn(resp["response"], user_input)

            compliance_status = "✅ Compliant" if turn_eval["brevity_passed"] else "⚠️ >25 Words"
            print(f"\n📞 Priya: \"{resp['response']}\"")
            print(f"   [Telemetry: {resp['word_count']} words | {compliance_status} | Stage: {resp['stage']}]\n")

            if resp.get("dnd_opted"):
                print("🚫 [Call Terminated: Customer Opted Out / DND Confirmed]\n")
                break

        except (KeyboardInterrupt, EOFError):
            break

    # End of call evaluation
    print("=" * 72)
    print("CALL SESSION DIAGNOSTIC SUMMARY")
    print("=" * 72)
    agent_state = {
        "callback_time": getattr(agent, "callback_time", None),
        "link_sent": getattr(agent, "link_sent", False),
        "dnd_opted": getattr(agent, "dnd_opted", False),
        "status_verified": getattr(agent, "status_verified", False)
    }
    expected = "CALLBACK_SCHEDULED" if agent_state["callback_time"] else ("LINK_SENT" if agent_state["link_sent"] else ("DND_RESPECTED" if agent_state["dnd_opted"] else "GENERAL"))
    call_eval = evaluator.evaluate_full_call(agent.history, expected, agent_state)

    status_tag = "[PASS]" if call_eval["verdict"] == "SUCCESS" else "[FAIL]"
    print(f"Verdict              : {status_tag} {call_eval['verdict']}")
    print(f"Overall Quality Score: {call_eval['overall_score']} / 10.0")
    print(f"Brevity Score        : {call_eval['brevity_score']} / 10.0 (Violations: {call_eval['brevity_violations']})")
    print(f"Hinglish Naturalness : {call_eval['naturalness_score']} / 10.0")
    print(f"Compliance Score     : {call_eval['compliance_score']} / 10.0")
    print(f"Total Turns          : {call_eval['total_turns']}")
    if call_eval["failure_reasons"]:
        print(f"Flagged Issues       : {call_eval['failure_reasons']}")
    print("=" * 72)


if __name__ == "__main__":
    main()
