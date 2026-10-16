"""Generates synthetic B2B marketing campaigns and inbound lead inquiry payloads."""

import json
import random
import uuid
from datetime import datetime, timedelta

CAMPAIGNS_OUTPUT = "data/raw_campaigns.json"
LEADS_OUTPUT = "data/raw_leads.json"

def generate_marketing_dataset(num_leads=400, start_date=datetime(2026, 8, 1, 8, 0, 0)):
    # Define acquisition channels and target industry verticals
    campaigns = [
        {"campaign_id": "cmp_gads_sec", "campaign_name": "Google Ads - Ransomware Defense", "channel": "Google_Ads", "budget_allocated_usd": 4500.0, "spend_to_date_usd": 3820.0, "target_vertical": "Healthcare"},
        {"campaign_id": "cmp_gads_mig", "campaign_name": "Google Ads - Azure Cloud Migration", "channel": "Google_Ads", "budget_allocated_usd": 3500.0, "spend_to_date_usd": 3100.0, "target_vertical": "Finance"},
        {"campaign_id": "cmp_seo_local", "campaign_name": "Organic SEO - South Jersey IT Support", "channel": "Organic_SEO", "budget_allocated_usd": 2000.0, "spend_to_date_usd": 1850.0, "target_vertical": "Legal"},
        {"campaign_id": "cmp_maps_phl", "campaign_name": "Google Business Profile - Metro Philly IT", "channel": "Local_Map_Pack", "budget_allocated_usd": 1200.0, "spend_to_date_usd": 950.0, "target_vertical": "Manufacturing"},
        {"campaign_id": "cmp_li_exec", "campaign_name": "LinkedIn Sponsored - Compliance & CMMC", "channel": "LinkedIn", "budget_allocated_usd": 5000.0, "spend_to_date_usd": 4400.0, "target_vertical": "Defense_Contracting"}
    ]

    company_prefixes = ["Keystone", "Delaware Valley", "Liberty", "Pine Barrens", "Tri-State", "Apex", "Horizon", "Franklin"]
    company_suffixes = ["Medical Partners", "Law Group", "Logistics LLC", "Manufacturing Co", "Accounting Group", "Dental Care", "Engineering Associates"]

    needs = [
        ("Cybersecurity", ["Current antivirus flagged ransomware threat.", "Need HIPAA compliance audit before quarter end.", "Phishing attacks increasing among staff."]),
        ("Cloud_Migration", ["Need to decommission aging on-premise Windows Server 2012.", "Migrating files and email to Microsoft 365 and SharePoint.", "Need hybrid cloud setup for remote staff."]),
        ("Managed_Helpdesk", ["Staff experiencing frequent workstation crashes and slow Wi-Fi.", "Current IT provider takes 48 hours to answer tickets.", "Need 24/7 endpoint monitoring and patch management."]),
        ("VoIP", ["Replacing old PBX phones with modern cloud calling.", "Need remote phone integration with Microsoft Teams.", "Poor call routing for front office intake."])
    ]

    urgencies = ["Low", "Medium", "Critical"]

    leads = []
    print(f"Generating {len(campaigns)} marketing campaigns and {num_leads} lead inquiries...")

    for i in range(num_leads):
        lead_id = f"lead_{uuid.uuid4().hex[:10]}"
        campaign = random.choice(campaigns)
        
        # Distribute submissions over a 75-day window
        submission_dt = start_date + timedelta(days=random.randint(0, 75), hours=random.randint(0, 10), minutes=random.randint(0, 59))
        company_name = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}"
        employee_count = random.randint(5, 250)
        
        # Monthly IT spend typically scales between $100 and $250 per user seat
        monthly_budget = round(employee_count * random.uniform(110.0, 220.0), -1)
        urgency = random.choice(urgencies)
        need_category, sample_notes = random.choice(needs)
        notes = random.choice(sample_notes)

        lead_record = {
            "lead_id": lead_id,
            "campaign_id": campaign["campaign_id"],
            "submission_timestamp": submission_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "company_name": company_name,
            "employee_count": employee_count,
            "stated_budget_monthly_usd": monthly_budget,
            "urgency_level": urgency,
            "primary_need": need_category,
            "unstructured_notes": notes
        }

        # Inject intentional data quality anomalies for validation handling
        if i % 70 == 0:
            lead_record["stated_budget_monthly_usd"] = -1500.0  # Corrupted negative budget
        elif i % 90 == 0:
            lead_record["employee_count"] = 0  # Invalid seat count
        elif i % 130 == 0:
            lead_record["campaign_id"] = "cmp_untracked_source"  # Orphaned foreign key

        leads.append(lead_record)

    # Save outputs to data directory
    with open(CAMPAIGNS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, indent=2)

    with open(LEADS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    print(f"Saved {len(campaigns)} campaigns to {CAMPAIGNS_OUTPUT}")
    print(f"Saved {len(leads)} leads to {LEADS_OUTPUT}")

if __name__ == "__main__":
    generate_marketing_dataset()