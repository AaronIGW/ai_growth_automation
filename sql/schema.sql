-- Marketing campaigns tracking acquisition channels, ad spend, and impressions.
CREATE TABLE IF NOT EXISTS dim_campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    channel TEXT NOT NULL,              -- 'Google_Ads', 'Organic_SEO', 'LinkedIn', 'Local_Map_Pack'
    budget_allocated_usd REAL NOT NULL,
    spend_to_date_usd REAL NOT NULL,
    target_vertical TEXT NOT NULL       -- 'Healthcare', 'Legal', 'Manufacturing', 'Finance'
);

-- Inbound sales leads and customer inquiry profiles.
CREATE TABLE IF NOT EXISTS fact_leads (
    lead_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    submission_timestamp TIMESTAMP NOT NULL,
    submission_date DATE NOT NULL,
    company_name TEXT NOT NULL,
    employee_count INTEGER NOT NULL,
    stated_budget_monthly_usd REAL NOT NULL,
    urgency_level TEXT NOT NULL,        -- 'Low', 'Medium', 'Critical'
    primary_need TEXT NOT NULL,         -- 'Cybersecurity', 'Cloud_Migration', 'Managed_Helpdesk', 'VoIP'
    unstructured_notes TEXT NOT NULL,
    lead_score INTEGER,                 -- Deterministic score: 0 to 100
    qualification_tier TEXT,            -- 'Cold', 'Warm', 'High-Priority'
    FOREIGN KEY (campaign_id) REFERENCES dim_campaigns(campaign_id)
);

-- AI-generated client briefings, package recommendations, and call strategies.
CREATE TABLE IF NOT EXISTS fact_ai_briefings (
    briefing_id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    recommended_package TEXT NOT NULL,  -- 'Core Care', 'Security Shield', 'Enterprise Managed IT'
    estimated_mrr_usd REAL NOT NULL,
    executive_summary TEXT NOT NULL,
    discovery_call_strategy TEXT NOT NULL,
    FOREIGN KEY (lead_id) REFERENCES fact_leads(lead_id)
);

-- Audit table tracking ingestion anomalies and rejected lead payloads.
CREATE TABLE IF NOT EXISTS lead_quarantine (
    raw_payload TEXT,
    rejection_reason TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);