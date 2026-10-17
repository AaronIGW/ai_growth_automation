# AI-Powered Marketing Growth & Client Intelligence Pipeline

An automated data pipeline and sales enablement engine designed to ingest inbound B2B marketing leads, score prospect fit, and synthesize structured client briefings for Managed Service Providers (MSPs).

## Architecture & Data Flow

1. **Lead Ingestion & Quality Validation (src/data_generator.py, src/pipeline.py)**
   * Generates and parses multi-channel inbound inquiries from Google Ads, LinkedIn, Organic SEO, and Local Search.
   * Enforces referential integrity against campaign dimensions and catches malformed payloads (negative budgets, zero seat counts) into a dead-letter quarantine table.

2. **Deterministic Sales Scoring (src/pipeline.py)**
   * Computes a 0–100 qualification score based on seat scale, monthly recurring revenue (MRR) potential, and timeline urgency.
   * Triages accounts into High-Priority, Warm, and Cold sales queues.

3. **AI Executive Briefing Engine (src/ai_briefing.py)**
   * Evaluates high-intent prospects and determines recommended service packages (Core Care, Security Shield, Enterprise Managed IT).
   * Synthesizes commercial executive summaries and structured 4-point outbound discovery call strategies.

4. **Executive Growth Dashboard (app.py)**
   * Deploys an interactive Streamlit application visualizing campaign acquisition ROI, lead qualification distributions, and client account dossiers.

## Schema Specifications

* **dim_campaigns**
  * campaign_id (TEXT, Primary Key)
  * campaign_name (TEXT)
  * channel (TEXT)
  * budget_allocated_usd (REAL)
  * spend_to_date_usd (REAL)
  * target_vertical (TEXT)

* **fact_leads**
  * lead_id (TEXT, Primary Key)
  * campaign_id (TEXT, Foreign Key)
  * submission_timestamp (TIMESTAMP)
  * submission_date (DATE)
  * company_name (TEXT)
  * employee_count (INTEGER)
  * stated_budget_monthly_usd (REAL)
  * urgency_level (TEXT)
  * primary_need (TEXT)
  * unstructured_notes (TEXT)
  * lead_score (INTEGER)
  * qualification_tier (TEXT)

* **fact_ai_briefings**
  * briefing_id (TEXT, Primary Key)
  * lead_id (TEXT, Foreign Key)
  * generated_at (TIMESTAMP)
  * recommended_package (TEXT)
  * estimated_mrr_usd (REAL)
  * executive_summary (TEXT)
  * discovery_call_strategy (TEXT)

* **lead_quarantine**
  * raw_payload (TEXT)
  * rejection_reason (TEXT)
  * flagged_at (TIMESTAMP)

## Prerequisites & Dependencies

* Python 3.9+
* Required packages:
    pip install pandas streamlit plotly

## How to Run

1. Clone repository & open folder:
    git clone https://github.com/AaronIGW/ai_growth_automation.git
    cd ai_growth_automation

2. Generate synthetic campaigns and lead records:
    python src/data_generator.py
   (Generates synthetic marketing campaigns and prospect leads with intentional anomalies in data/raw_leads.json)

3. Run ingestion and deterministic scoring pipeline:
    python src/pipeline.py
   (Initializes growth_marketing.db, seeds dim_campaigns, stages scored leads in fact_leads, and routes bad payloads to lead_quarantine)

4. Generate AI account briefings:
    python src/ai_briefing.py
   (Evaluates qualified leads, determines recommended service tiers, and stages commercial discovery dossiers in fact_ai_briefings)

5. Launch executive growth dashboard:
    streamlit run app.py
   (Opens the interactive dashboard to review acquisition metrics, conversion rates, and client account briefs)
