"""Generates structured AI executive briefings and discovery call scripts for high-priority leads."""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "growth_marketing.db"

def select_package_and_pricing(employee_count, primary_need, budget):
    """Determines recommended service tier and calculated MRR based on client profile."""
    if primary_need == "Cybersecurity":
        package = "Security Shield"
        per_user_rate = 175.0
    elif primary_need in ["Cloud_Migration", "VoIP"]:
        package = "Enterprise Managed IT"
        per_user_rate = 195.0
    else:
        package = "Core Care"
        per_user_rate = 135.0

    calculated_mrr = round(employee_count * per_user_rate, 2)
    # Reconcile against client's stated budget
    projected_mrr = min(calculated_mrr, budget) if budget > 0 else calculated_mrr
    return package, projected_mrr

def generate_briefing_narrative(company_name, employees, need, urgency, notes, package, mrr):
    """Produces executive summary and structured sales discovery playbook."""
    exec_summary = (
        f"{company_name} ({employees} seats) submitted a {urgency.lower()}-urgency inquiry "
        f"regarding {need.replace('_', ' ')}. Primary client pain point: '{notes}'. "
        f"Recommended fit is the {package} tier with an estimated recurring value of ${mrr:,.2f}/month."
    )

    discovery_strategy = (
        f"1. Open call addressing immediate bottleneck: '{notes}'. "
        f"2. Validate compliance exposure and hardware lifecycle across {employees} endpoints. "
        f"3. Frame {package} as an operational risk reduction rather than an overhead cost. "
        f"4. Propose standard 14-day network and security assessment to substantiate proposal."
    )

    return exec_summary, discovery_strategy

def run_ai_briefing_engine(db_path=DB_PATH, min_score=75):
    """Extracts top-tier leads and generates persistent executive briefings."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch high-priority leads lacking existing briefings
    cursor.execute(
        """
        SELECT 
            fl.lead_id, fl.company_name, fl.employee_count, 
            fl.stated_budget_monthly_usd, fl.urgency_level, 
            fl.primary_need, fl.unstructured_notes
        FROM fact_leads fl
        LEFT JOIN fact_ai_briefings fb ON fl.lead_id = fb.lead_id
        WHERE fl.lead_score >= ? AND fb.briefing_id IS NULL;
        """,
        (min_score,)
    )
    high_priority_leads = cursor.fetchall()

    if not high_priority_leads:
        print("No new high-priority leads require briefing generation.")
        conn.close()
        return

    briefings = []
    generated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for lead in high_priority_leads:
        lead_id, company, employees, budget, urgency, need, notes = lead
        package, projected_mrr = select_package_and_pricing(employees, need, budget)
        
        exec_summary, discovery_strategy = generate_briefing_narrative(
            company, employees, need, urgency, notes, package, projected_mrr
        )

        briefing_id = f"brf_{uuid.uuid4().hex[:10]}"
        briefings.append((
            briefing_id,
            lead_id,
            generated_timestamp,
            package,
            projected_mrr,
            exec_summary,
            discovery_strategy
        ))

    # Stage generated briefings to relational database
    cursor.executemany(
        """
        INSERT INTO fact_ai_briefings (
            briefing_id, lead_id, generated_at,
            recommended_package, estimated_mrr_usd,
            executive_summary, discovery_call_strategy
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        briefings
    )

    conn.commit()
    conn.close()

    print("\n--- AI Briefing Engine Execution Summary ---")
    print(f"High-Priority Leads Evaluated : {len(high_priority_leads)}")
    print(f"Executive Briefings Staged    : {len(briefings)}")

if __name__ == "__main__":
    run_ai_briefing_engine()