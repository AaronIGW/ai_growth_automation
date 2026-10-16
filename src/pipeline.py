"""Ingestion and qualification pipeline for marketing campaigns and B2B leads."""

import json
import sqlite3
from datetime import datetime

DB_PATH = "growth_marketing.db"
SCHEMA_PATH = "sql/schema.sql"
CAMPAIGNS_PATH = "data/raw_campaigns.json"
LEADS_PATH = "data/raw_leads.json"

def init_database(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Initializes SQLite database using DDL schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database schema initialized.")

def ingest_campaigns(campaigns_path=CAMPAIGNS_PATH, db_path=DB_PATH):
    """Loads acquisition campaigns into dim_campaigns."""
    with open(campaigns_path, "r", encoding="utf-8") as f:
        campaigns = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    records = [
        (
            c["campaign_id"],
            c["campaign_name"],
            c["channel"],
            c["budget_allocated_usd"],
            c["spend_to_date_usd"],
            c["target_vertical"]
        )
        for c in campaigns
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO dim_campaigns (
            campaign_id, campaign_name, channel,
            budget_allocated_usd, spend_to_date_usd, target_vertical
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        records
    )
    conn.commit()
    conn.close()
    print(f"Loaded {len(records)} campaigns into dim_campaigns.")

def calculate_lead_score(employee_count, monthly_budget, urgency_level):
    """Calculates a deterministic 0-100 sales qualification score and priority tier."""
    score = 0

    # Seat scale weighting (max 40 pts)
    if employee_count >= 100:
        score += 40
    elif employee_count >= 40:
        score += 30
    elif employee_count >= 15:
        score += 20
    else:
        score += 10

    # Monthly recurring revenue budget potential (max 35 pts)
    if monthly_budget >= 15000:
        score += 35
    elif monthly_budget >= 6000:
        score += 25
    elif monthly_budget >= 2500:
        score += 15
    else:
        score += 5

    # Timeline urgency weighting (max 25 pts)
    if urgency_level == "Critical":
        score += 25
    elif urgency_level == "Medium":
        score += 15
    else:
        score += 5

    # Triage tier assignment
    if score >= 75:
        tier = "High-Priority"
    elif score >= 50:
        tier = "Warm"
    else:
        tier = "Cold"

    return score, tier

def process_leads(leads_path=LEADS_PATH, db_path=DB_PATH):
    """Ingests, validates, scores, and stages inbound B2B sales inquiries."""
    with open(leads_path, "r", encoding="utf-8") as f:
        leads = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Cache valid campaign IDs to ensure referential integrity
    cursor.execute("SELECT campaign_id FROM dim_campaigns;")
    valid_campaign_ids = {row[0] for row in cursor.fetchall()}

    valid_leads = []
    quarantined = []

    for l in leads:
        lead_id = l.get("lead_id")
        camp_id = l.get("campaign_id")
        ts_str = l.get("submission_timestamp")
        company = l.get("company_name")
        employees = l.get("employee_count")
        budget = l.get("stated_budget_monthly_usd")
        urgency = l.get("urgency_level")
        need = l.get("primary_need")
        notes = l.get("unstructured_notes", "")
        raw_dump = json.dumps(l)

        # Rule 1: Missing primary key or timestamp
        if not lead_id or not ts_str:
            quarantined.append((raw_dump, "Missing lead_id or submission_timestamp"))
            continue

        # Rule 2: Campaign foreign key validity
        if camp_id not in valid_campaign_ids:
            quarantined.append((raw_dump, f"Orphaned lead: campaign_id '{camp_id}' not found"))
            continue

        # Rule 3: Valid seat count
        if employees is None or employees <= 0:
            quarantined.append((raw_dump, f"Invalid employee_count: {employees}"))
            continue

        # Rule 4: Non-negative monthly budget
        if budget is None or budget <= 0:
            quarantined.append((raw_dump, f"Invalid stated_budget_monthly_usd: {budget}"))
            continue

        score, tier = calculate_lead_score(employees, budget, urgency)
        submission_date = ts_str[:10]

        valid_leads.append((
            lead_id,
            camp_id,
            ts_str,
            submission_date,
            company,
            employees,
            budget,
            urgency,
            need,
            notes,
            score,
            tier
        ))

    # Stage qualified records
    if valid_leads:
        cursor.executemany(
            """
            INSERT OR IGNORE INTO fact_leads (
                lead_id, campaign_id, submission_timestamp,
                submission_date, company_name, employee_count,
                stated_budget_monthly_usd, urgency_level,
                primary_need, unstructured_notes,
                lead_score, qualification_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            valid_leads
        )

    # Stage invalid records to quarantine
    if quarantined:
        cursor.executemany(
            "INSERT INTO lead_quarantine (raw_payload, rejection_reason) VALUES (?, ?);",
            quarantined
        )

    conn.commit()
    conn.close()

    print("\n--- Pipeline Execution Summary ---")
    print(f"Total Raw Leads Ingested   : {len(leads)}")
    print(f"Valid Leads Staged         : {len(valid_leads)}")
    print(f"Quarantined Anomalies      : {len(quarantined)}")

if __name__ == "__main__":
    init_database()
    ingest_campaigns()
    process_leads()