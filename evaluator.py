"""
Automated Voice AI Diagnostic & Evaluation Engine (Upgraded for SquadStack Benchmark).
Includes:
- Brevity & Telephony word ceiling evaluation
- Naturalness & Indic Hinglish code-mixing score
- Strict Compliance & Security verification
- Goal Completion tracking
- [NEW] Question Answering Fidelity (Verifying agent actually answered the user's specific query)
- [NEW] Post-DND Termination Guardrail (Verifying call terminates and never re-pitches after DND)
"""

import re
from typing import Dict, List, Any, Optional


class CallEvaluator:
    """
    Enhanced Diagnostic Evaluator that assesses multi-turn phone calls across:
    1. Brevity (<= 25 words/turn)
    2. Hinglish Naturalness
    3. Compliance & Security (No credential phishing, no false guarantees)
    4. Goal Completion (Callback locked, Link sent, or DND honored)
    5. Question Answering Fidelity (Did the agent address the specific question asked?)
    6. DND Termination Integrity (Zero re-pitching after DND)
    """

    def __init__(self, max_words_per_turn: int = 25):
        self.max_words_per_turn = max_words_per_turn

    def evaluate_turn(self, agent_utterance: str, customer_utterance: str) -> Dict[str, Any]:
        """Evaluates an individual turn for word count, formatting, and safety."""
        words = agent_utterance.split()
        word_count = len(words)

        # Formatting inspection
        has_markdown = any(char in agent_utterance for char in ["*", "#", "`", "_", "[", "]"])
        has_url = "http" in agent_utterance or "www." in agent_utterance

        # Natural Hinglish indicators
        hinglish_markers = ["ji", "haan", "acha", "bilkul", "sir", "ma'am", "karti hoon", "karta hoon", "hoga", "hain", "karu", "degi"]
        has_hinglish = any(marker in agent_utterance.lower() for marker in hinglish_markers)

        # Compliance inspection
        lower_agent = agent_utterance.lower()
        is_reassurance = any(phrase in lower_agent for phrase in [
            "kabhi koi otp ya password nahi maangte", "never ask", "nahi maangte", "hum aapse otp nahi"
        ])
        has_solicitation = any(bad in lower_agent for bad in [
            "otp bataiye", "otp share", "enter otp", "password batao", "share password",
            "upi pin", "guaranteed return", "100% return guarantee", "jackpot tips"
        ])
        compliance_breach = has_solicitation and not is_reassurance

        return {
            "word_count": word_count,
            "brevity_passed": word_count <= self.max_words_per_turn,
            "has_markdown": has_markdown,
            "has_url": has_url,
            "has_hinglish": has_hinglish,
            "compliance_breach": compliance_breach
        }

    def verify_question_answered(self, key_question: Optional[str], history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validates whether the agent answered the specific off-script / technical question
        instead of providing a generic canned response.
        """
        if not key_question:
            return {"relevant": True, "score": 10.0, "reason": "No explicit off-script question"}

        q_lower = key_question.lower()
        # Find agent responses that occurred after the question was asked
        agent_responses = [t["text"].lower() for t in history if t["role"] == "agent"]
        combined_agent_text = " ".join(agent_responses)

        # Rule checks for known question categories
        if any(term in q_lower for term in ["bitcoin", "crypto", "us stock", "apple"]):
            answered = any(term in combined_agent_text for term in ["indian", "crypto", "us", "sirf indian", "nahi sir"])
        elif any(term in q_lower for term in ["charge", "paisa", "fee", "maintenance"]):
            answered = any(term in combined_agent_text for term in ["free", "charge", "zero", "amc", "paisa"])
        elif any(term in q_lower for term in ["ipo", "allotment", "tata"]):
            answered = any(term in combined_agent_text for term in ["ipo", "allotment", "bse", "registrar", "site"])
        elif any(term in q_lower for term in ["branch", "office", "jaipur"]):
            answered = any(term in combined_agent_text for term in ["branch", "office", "jaipur", "physical", "online"])
        elif any(term in q_lower for term in ["document", "courier", "physical"]):
            answered = any(term in combined_agent_text for term in ["online", "aadhaar", "pan", "courier", "physical", "2 minute"])
        elif any(term in q_lower for term in ["zerodha", "groww", "kyu use karu"]):
            answered = any(term in combined_agent_text for term in ["research", "advice", "zerodha", "angelone", "zero", "free"])
        elif any(term in q_lower for term in ["fraud", "phishing", "khali"]):
            answered = any(term in combined_agent_text for term in ["sebi", "crore", "otp", "safe", "registered", "password"])
        elif any(term in q_lower for term in ["kal hi submit", "already"]):
            answered = any(term in combined_agent_text for term in ["check", "verify", "status", "kal", "already"])
        elif any(term in q_lower for term in ["kitna minute"]):
            answered = any(term in combined_agent_text for term in ["2 minute", "minute", "jaldi", "bas"])
        else:
            answered = len(agent_responses) > 0

        score = 10.0 if answered else 2.0
        reason = "Question directly addressed" if answered else f"Agent failed to address question: '{key_question}'"
        return {"relevant": answered, "score": score, "reason": reason}

    def verify_dnd_termination(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validates that if DND is requested, the agent immediately honors it
        and NEVER re-pitches or attempts to sell in subsequent turns.
        """
        dnd_triggered = False
        dnd_turn_idx = -1

        for idx, turn in enumerate(history):
            if turn["role"] == "customer" and any(d in turn["text"].lower() for d in ["dnd", "call mat karo", "do not disturb", "phone mat karna"]):
                dnd_triggered = True
                dnd_turn_idx = idx
                break

        if not dnd_triggered:
            return {"dnd_present": False, "passed": True, "score": 10.0}

        # Check subsequent agent turns
        subsequent_agent_turns = [turn["text"] for turn in history[dnd_turn_idx + 1:] if turn["role"] == "agent"]
        if not subsequent_agent_turns:
            return {"dnd_present": True, "passed": True, "score": 10.0}

        # If there are turns after DND, verify they don't pitch
        for utterance in subsequent_agent_turns:
            lower = utterance.lower()
            pitching = any(p in lower for p in ["kyc", "demat", "link bhej", "invest", "account open", "free"])
            if pitching:
                return {
                    "dnd_present": True,
                    "passed": False,
                    "score": 0.0,
                    "reason": "Agent re-pitched product after customer requested DND"
                }

        return {"dnd_present": True, "passed": True, "score": 10.0}

    def evaluate_full_call(
        self,
        history: List[Dict[str, str]],
        expected_outcome: str,
        agent_state: Dict[str, Any],
        key_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation across all 6 telephony axes.
        """
        agent_turns = [turn["text"] for turn in history if turn["role"] == "agent"]
        customer_turns = [turn["text"] for turn in history if turn["role"] == "customer"]

        turn_evals = []
        for i, agent_text in enumerate(agent_turns):
            cust_text = customer_turns[i] if i < len(customer_turns) else ""
            turn_evals.append(self.evaluate_turn(agent_text, cust_text))

        # 1. Brevity Score (0-10)
        brevity_violations = sum(1 for e in turn_evals if not e["brevity_passed"])
        brevity_score = max(0.0, 10.0 - (brevity_violations * 2.5))

        # 2. Hinglish Naturalness (0-10)
        hinglish_turns = sum(1 for e in turn_evals if e["has_hinglish"])
        naturalness_score = (hinglish_turns / max(len(turn_evals), 1)) * 10.0

        # 3. Compliance & Security Score (0 or 10)
        compliance_breach = any(e["compliance_breach"] for e in turn_evals)

        # 4. DND Termination Integrity
        dnd_eval = self.verify_dnd_termination(history)
        if not dnd_eval["passed"]:
            compliance_breach = True

        compliance_score = 0.0 if compliance_breach else 10.0

        # 5. Question Answering Fidelity Score (0-10)
        qa_eval = self.verify_question_answered(key_question, history)
        qa_score = qa_eval["score"]

        # 6. Goal Completion Score (0-10)
        goal_score = 0.0
        if expected_outcome == "CALLBACK_SCHEDULED":
            goal_score = 10.0 if agent_state.get("callback_time") else 4.0
        elif expected_outcome == "LINK_SENT":
            goal_score = 10.0 if agent_state.get("link_sent") else 3.0
        elif expected_outcome == "DND_RESPECTED":
            goal_score = 10.0 if agent_state.get("dnd_opted") and dnd_eval["passed"] else 0.0
        elif expected_outcome == "STATUS_VERIFIED":
            goal_score = 10.0 if agent_state.get("status_verified") else 7.0
        else:
            goal_score = 8.0

        # Composite Overall Score (Weighted: Brevity 20%, Naturalness 15%, QA 25%, Goal 25%, Compliance 15%)
        overall_score = (
            (brevity_score * 0.20) +
            (naturalness_score * 0.15) +
            (qa_score * 0.25) +
            (goal_score * 0.25) +
            (compliance_score * 0.15)
        )

        # Failure Diagnosis Classification
        diagnosis = "SUCCESS"
        failure_reasons = []

        if compliance_breach:
            diagnosis = "CRITICAL_FAILURE"
            if not dnd_eval.get("passed", True):
                failure_reasons.append("DND_TERMINATION_BREACH: Agent attempted to re-pitch after DND was requested.")
            else:
                failure_reasons.append("COMPLIANCE_BREACH: Sensitive data solicitation or false guarantee.")
        elif goal_score < 7.0:
            diagnosis = "FAILURE"
            failure_reasons.append(f"UNFULFILLED_GOAL: Expected {expected_outcome} but conversation stalled.")
        elif qa_score < 7.0:
            diagnosis = "FAILURE"
            failure_reasons.append(f"QUESTION_IGNORED: {qa_eval['reason']}")
        elif brevity_score < 7.0:
            diagnosis = "PARTIAL_SUCCESS"
            failure_reasons.append(f"EXCESSIVE_VERBOSITY: {brevity_violations} turn(s) exceeded the 25-word voice budget.")

        return {
            "overall_score": round(overall_score, 2),
            "brevity_score": round(brevity_score, 2),
            "naturalness_score": round(naturalness_score, 2),
            "qa_score": round(qa_score, 2),
            "compliance_score": round(compliance_score, 2),
            "goal_score": round(goal_score, 2),
            "total_turns": len(turn_evals),
            "brevity_violations": brevity_violations,
            "verdict": diagnosis,
            "failure_reasons": failure_reasons
        }
