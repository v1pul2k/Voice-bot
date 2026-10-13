"""
Conversational Data Store & SQL Analytics Layer for SquadStack Voice AI.
Tracks multi-agent benchmark comparisons (Rule-Based Baseline vs Gemini V1 vs Gemini V2).
Includes comparative SQL queries for Before/After prompt iteration analysis.
"""

import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")


class AnalyticsDatabase:
    """Manages multi-model call benchmarking and comparative SQL queries."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Creates relational schema supporting multi-bot comparisons."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Calls Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                call_id TEXT PRIMARY KEY,
                bot_type TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                customer_name TEXT,
                category TEXT,
                expected_outcome TEXT,
                verdict TEXT,
                overall_score REAL,
                brevity_score REAL,
                qa_score REAL,
                goal_score REAL,
                naturalness_score REAL,
                compliance_score REAL,
                total_turns INTEGER,
                brevity_violations INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Failure Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT NOT NULL,
                bot_type TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                failure_reason TEXT NOT NULL,
                FOREIGN KEY (call_id) REFERENCES calls (call_id)
            )
            """)
            conn.commit()

    def record_call(
        self,
        call_id: str,
        bot_type: str,
        scenario_id: str,
        customer_name: str,
        category: str,
        expected_outcome: str,
        eval_result: Dict[str, Any]
    ):
        """Records a completed benchmark run for a specific bot variant."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            INSERT OR REPLACE INTO calls 
            (call_id, bot_type, scenario_id, customer_name, category, expected_outcome, verdict, 
             overall_score, brevity_score, qa_score, goal_score, naturalness_score, compliance_score, 
             total_turns, brevity_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                bot_type,
                scenario_id,
                customer_name,
                category,
                expected_outcome,
                eval_result["verdict"],
                eval_result["overall_score"],
                eval_result["brevity_score"],
                eval_result.get("qa_score", 10.0),
                eval_result["goal_score"],
                eval_result["naturalness_score"],
                eval_result["compliance_score"],
                eval_result["total_turns"],
                eval_result["brevity_violations"]
            ))

            for reason in eval_result.get("failure_reasons", []):
                cursor.execute("""
                INSERT INTO failure_diagnostics (call_id, bot_type, scenario_id, failure_reason)
                VALUES (?, ?, ?, ?)
                """, (call_id, bot_type, scenario_id, reason))

            conn.commit()

    def run_comparative_report(self) -> Dict[str, Any]:
        """
        Executes analytical SQL queries comparing:
        1. Rule-Based Baseline
        2. Gemini Few-Shot V1
        3. Gemini Iterated Few-Shot V2
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Comparative performance table
            cursor.execute("""
            SELECT 
                bot_type,
                COUNT(*) as total_scenarios,
                SUM(CASE WHEN verdict = 'SUCCESS' THEN 1 ELSE 0 END) as passed_scenarios,
                ROUND(SUM(CASE WHEN verdict = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pass_rate_pct,
                ROUND(AVG(overall_score), 2) as avg_overall_score,
                ROUND(AVG(brevity_score), 2) as avg_brevity,
                ROUND(AVG(qa_score), 2) as avg_qa_fidelity,
                ROUND(AVG(goal_score), 2) as avg_goal_completion,
                SUM(brevity_violations) as total_brevity_violations
            FROM calls
            GROUP BY bot_type
            ORDER BY avg_overall_score ASC
            """)
            comparative_summary = [dict(r) for r in cursor.fetchall()]

            # Category-wise breakdown
            cursor.execute("""
            SELECT 
                category,
                bot_type,
                ROUND(AVG(overall_score), 2) as avg_score,
                SUM(CASE WHEN verdict = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pass_rate
            FROM calls
            GROUP BY category, bot_type
            ORDER BY category, bot_type
            """)
            category_performance = [dict(r) for r in cursor.fetchall()]

            # Top failure reasons per bot
            cursor.execute("""
            SELECT 
                bot_type,
                failure_reason,
                COUNT(*) as count
            FROM failure_diagnostics
            GROUP BY bot_type, failure_reason
            ORDER BY bot_type, count DESC
            """)
            failures_by_bot = [dict(r) for r in cursor.fetchall()]

            return {
                "comparative_summary": comparative_summary,
                "category_performance": category_performance,
                "failures_by_bot": failures_by_bot
            }
