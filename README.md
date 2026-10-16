# AI-Powered Marketing Growth & Client Intelligence Pipeline

An automated data pipeline and sales enablement engine designed to ingest inbound B2B marketing leads, score prospect fit, and synthesize structured client briefings for Managed Service Providers (MSPs).

## Architecture & Data Flow

1. **Lead Ingestion & Quality Validation (`src/data_generator.py`, `src/pipeline.py`)**
   * Generates and parses multi-channel inbound inquiries from Google Ads, LinkedIn, Organic SEO, and Local Search.
   * Enforces referential integrity against campaign dimensions and catches malformed payloads (negative budgets, zero seat counts) into a dead-letter quarantine table.

2. **Deterministic Sales Scoring (`src/pipeline.py`)**
   * Computes a 0–100 qualification score based on seat scale, monthly recurring revenue (MRR) potential, and timeline urgency.
   * Triages accounts into High-Priority, Warm, and Cold sales queues.

3. **AI Executive Briefing Engine (`src/ai_briefing.py`)**
   * Evaluates high-intent prospects and determines recommended service packages (`Core Care`, `Security Shield`, `Enterprise Managed IT`).
   * Synthesizes commercial executive summaries and structured 4-point outbound discovery call strategies.

4. **Executive Growth Dashboard (`app.py`)**
   * Deploys an interactive Streamlit application visualizing campaign acquisition ROI, lead qualification distributions, and client account dossiers.

## Schema Specifications

* **`dim_campaigns`**
  * `campaign_id` (TEXT, Primary Key)
  * `campaign_name` (TEXT)
  * `channel` (TEXT)
  * `budget_allocated_usd` (REAL)
  * `spend_to_date_usd` (REAL)
  * `target_vertical` (TEXT)

* **`fact_leads`**
  * `lead_id` (TEXT, Primary Key)
  * `campaign_id` (TEXT, Foreign Key)
  * `submission_timestamp` (TIMESTAMP)
  * `submission_date` (DATE)
  * `company_name` (TEXT)
  * `employee_count` (INTEGER)
  * `stated_budget_monthly_usd` (REAL)
  * `urgency_level` (TEXT)
  * `primary_need` (TEXT)
  * `unstructured_notes` (TEXT)
  * `lead_score` (INTEGER)
  * `qualification_tier` (TEXT)

* **`fact_ai_briefings`**
  * `briefing_id` (TEXT, Primary Key)
  * `lead_id` (TEXT, Foreign Key)
  * `generated_at` (TIMESTAMP)
  * `recommended_package` (TEXT)
  * `estimated_mrr_usd` (REAL)
  * `executive_summary` (TEXT)
  * `discovery_call_strategy` (TEXT)

* **`lead_quarantine`**
  * `raw_payload` (TEXT)
  * `rejection_reason` (TEXT)
  * `flagged_at` (TIMESTAMP)

## Execution Instructions

1. Generate synthetic campaigns and lead records:
   ```bash
   python src/data_generator.py