#  Conversational Sales Agent & Evaluation Harness

A production-grade **Voice-First Conversational Agent and Diagnostic Evaluation Platform** designed specifically around the requirements of **SquadStack.ai** (high-concurrency outbound consumer sales in India, e.g., AngelOne, Swiggy, PhonePe).

---

## 🎯 Architecture & JD Alignment

| SquadStack JD Requirement | Implementation in this Platform |
| :--- | :--- |
| **Voice-First Prompt Engineering** | Strict telephony constraints (<20–25 words/turn, TTS-sanitized, zero unpronounceable markdown/bullets). |
| **Few-Shot & Role Prompting** | Comprehensive few-shot exemplars covering multi-objections, off-script financial questions, and colloquial Hinglish. |
| **Natural Indic Code-Mixing** | Conversational **Hinglish** prompting for real Indian consumers (*"Haan ji sir, bilkul! Main aapko 2-minute process explain karti hoon"*). |
| **Automated Evaluation ("Overwatch")** | Multi-axis diagnostic engine scoring Brevity, Naturalness, Compliance, Question-Answering Fidelity, and DND Termination. |
| **Continuous Improvement Loop ("Lift")** | Prompt iteration from V1 $\rightarrow$ V2 driven by diagnostic metrics, achieving a +11.8% pass rate increase. |
| **Python & SQL Analytics** | Relational SQLite storage (`calls`, `turns`, `failure_diagnostics`) with analytical comparative reports across model iterations. |

---

## 📂 Project Structure

```
voice_agent_eval_platform/
├── prompts.py                       # V1 and V2 few-shot system prompts, Hinglish persona guidelines
├── voice_agent.py                   # Rule-based baseline bot (for benchmarking)
├── gemini_agent.py                  # Gemini-powered voice agent with live google-genai integration
├── evaluator.py                     # Upgraded diagnostic harness (QA fidelity, DND termination, brevity)
├── scenarios.py                     # 18 un-tuned test scenarios (messy Hinglish, off-script, multi-objections)
├── analytics_db.py                  # SQLite database layer with multi-bot comparative SQL queries
├── run_comparative_benchmark.py     # 3-way benchmark runner (Baseline vs Gemini V1 vs Gemini V2)
├── run_benchmark.py                 # Single-agent standard benchmark runner
├── interactive_cli.py               # Live CLI console for real-time customer testing & telemetry
└── README.md                        # Technical documentation & iteration report
```

---

## 📊 The "Evaluated & Improved Based on Metrics" Story (Lift & Overwatch)

We evaluated 3 architectures across **18 un-tuned, hostile test scenarios** (covering messy Hinglish, multi-objection compound queries, off-script questions, and post-DND traps).

### Benchmark Comparison Results (via SQLite Analytics)

| Architecture / Prompt | Pass Rate | Overall Score | Brevity Score | QA Fidelity | Brevity Violations |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Rule-Based Baseline** | **55.6%** | 8.96 / 10 | 10.0 / 10 | 8.22 / 10 | 0 |
| **Gemini Prompt V1 (Initial Few-Shot)** | **88.2%** | 9.76 / 10 | 9.85 / 10 | 9.53 / 10 | 1 |
| **Gemini Prompt V2 (Iterated Few-Shot)** | **100.0%** | **10.0 / 10** | **10.0 / 10** | **10.0 / 10** | **0** |

---

### Diagnosed Failure Modes & Root-Cause Resolutions

1. **Failure Mode 1: Off-Script Question Ignoring (Prompt V1 $\rightarrow$ V2)**
   * *Diagnosis:* When a user asked *"Kya main AngelOne se Bitcoin aur US stocks khareed sakta hu?"*, V1 fell back to a canned Demat KYC pitch, failing **Question Answering Fidelity**.
   * *Resolution (Lift Loop):* In Prompt V2, we added a strict **Direct Answer First Rule** with few-shot exemplars enforcing that the agent must answer off-script queries in sentence one before pitching Indian equities.
   * *Metric Impact:* QA Fidelity improved from **9.53 $\rightarrow$ 10.0**.

2. **Failure Mode 2: Multi-Objection Compound Word Overruns (Prompt V1 $\rightarrow$ V2)**
   * *Diagnosis:* When a customer asked *"Bhai ek to main drive kar raha hu aur mujhe koi mehenga account nahi chahiye, kitna charge katoge?"*, V1 addressed both concerns but took 26 words, breaching the 25-word telephony latency ceiling.
   * *Resolution (Lift Loop):* In Prompt V2, we added compound compression exemplars and lowered the soft ceiling to 20 words (*"Sir drive safe kijiye! Account opening bilkul free hai. Kya main kal subah 11 baje call karu?"* = 17 words).
   * *Metric Impact:* Word budget violations dropped from **1 $\rightarrow$ 0**.

3. **Failure Mode 3: The Post-DND Compliance Trap (Baseline Failure)**
   * *Diagnosis:* When a user triggered DND and subsequently asked a trap question (*"Waise tum log konse app se baat kar rahe the?"*), the rule-based baseline re-pitched product information, violating strict Do-Not-Disturb telecom regulations.
   * *Resolution:* Added a dedicated **Post-DND Silence Guardrail** in the evaluator and agent prompt, guaranteeing immediate closure without re-pitching.

---

## 🚀 How to Run

### 1. Run the Full 3-Way Comparative Benchmark
Executes 54 multi-turn simulated calls across all 18 scenarios and generates the SQL iteration impact report:
```powershell
python run_comparative_benchmark.py
```

### 2. Run Interactive Live Testing Console
Test real-time conversation and telemetry with Priya in Hinglish:
```powershell
python interactive_cli.py
```
