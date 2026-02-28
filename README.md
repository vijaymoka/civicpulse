# 🏛️ CivicPulse: Multi-Agent Civic Intelligence System

> AI-powered governance analytics platform built with Elastic Agent Builder for the **Elasticsearch Agent Builder Hackathon 2026**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Elastic](https://img.shields.io/badge/Elastic-Agent%20Builder-005571)
![ES|QL](https://img.shields.io/badge/ES%7CQL-Powered-00bfb3)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 🎯 Problem

Urban governance teams struggle with fragmented complaint data, reactive decision-making, and no predictive capability. Mayors and administrators lack real-time visibility into district-level stress, SLA compliance, and escalation patterns. Citizens have no intelligent interface to track complaints or find nearby issues.

## 💡 Solution

CivicPulse is a unified AI assistant built on Elastic Agent Builder that transforms raw complaint data into actionable insights, predictive projections, and intervention simulations through natural language conversation.

> **One conversation. Infinite intelligence.**

---

## 🏗️ Architecture

```
         USER (Citizen / Mayor)
                  │
                  ▼
    ┌──────────────────────────┐
    │  CivicPulse Super Agent  │
    │  - Intent Classification │
    │  - Stress Computation    │
    │  - ES|QL Execution       │
    │  - Risk Classification   │
    │  - Intervention Sim      │
    │  - 7-Day Projection      │
    └────────────┬─────────────┘
                 │
     ┌───────────┴───────────┐
     ▼                       ▼
┌──────────────┐   ┌─────────────────┐
│   Citizen    │   │  Mayor Command  │
│  Dashboard   │   │     Center      │
│  - Map View  │   │ - Stress Monitor│
│  - Complaints│   │ - Risk Panels   │
│  - Filters   │   │ - Trends        │
└──────┬───────┘   └────────┬────────┘
       └────────┬───────────┘
                ▼
    ┌────────────────────────┐
    │     Elasticsearch      │
    │  civicpulse_complaints │
    │   5,000+ geo-tagged    │
    │        docs            │
    └────────────────────────┘
```

---

## ✨ Features

### 🤖 AI Agent Capabilities

- **Stress Score Calculation** — Custom formula with transparent multi-step reasoning
- **Risk Classification** — Stable / Warning / High Risk bands
- **7-Day Projection** — Velocity-based trend forecasting
- **District Comparison** — Ranked analysis across all districts
- **Root Cause Analysis** — Category-level breach breakdown
- **Intervention Simulation** — What-if scenarios with before/after impact
- **Complaint Lookup** — Individual complaint retrieval by ID
- **Geo Search** — Find nearby complaints by coordinates

### 📊 Dashboard Features

- **Mayor Command Center** — Strategic overview with stress metrics, trends, and category breakdowns
- **Citizen Dashboard** — Operational map view with complaint locations and status filters

### 🔧 Data Pipeline

- **Bulk Ingestion** — 5,000 records with controlled GHC score (65–70)
- **Live Streaming** — Real-time data with crisis mode simulation
- **Rolling Retention** — Automatic cleanup maintaining 5,000 record cap
- **Geo-point Support** — Proper `geo_point` mapping for map visualizations

---

## 🧮 Stress Model

```
Stress = (SLA_breach_rate × 50) + (Escalation_rate × 30)
```

Where:
- `SLA_breach_rate` = breached_complaints / total_complaints
- `Escalation_rate` = escalated_complaints / total_complaints

**Risk Classification:**

| Score | Status |
|-------|--------|
| < 35 | ✅ Stable |
| 35–50 | ⚠️ Warning |
| ≥ 50 | 🔴 High Risk |

**7-Day Projection:**
```
Velocity = (recent_7d - previous_7d) / previous_7d
Projected_Stress = Current_Stress + (Velocity × 0.5)
```

---

## 📁 Project Structure

```
civicpulse-intelligence/
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── data/
│   ├── elastic_ingest.py       # Bulk data ingestion (5000 records)
│   └── elastic_stream.py       # Live streaming engine with crisis mode
└── agent/
    └── system_instruction.md   # Super Agent system instruction
```

---

## 🚀 Setup Guide

### Prerequisites

- Python 3.10+
- Elasticsearch cluster (Elastic Cloud)
- Kibana access
- `elasticsearch` Python package

### Step 1: Install Dependencies

```bash
pip install elasticsearch
```

### Step 2: Ingest Data

```bash
python data/elastic_ingest.py
```

This creates the `civicpulse_complaints` index with proper `geo_point` mapping and ingests 5,000 records.

### Step 3: Start Live Streaming *(Optional)*

```bash
python data/elastic_stream.py
```

**Controls:**
- Press `c` — Activate crisis mode (GHC drops to 40–50)
- Press `n` — Normalize (GHC returns to 65–70)
- Press `q` — Quit

### Step 4: Create Agent

1. Open **Elastic Agent Builder** in Kibana
2. Create new agent: `CivicPulse Intelligence`
3. Enable tools:
   - `platform.core.execute_esql`
   - `platform.core.search`
   - `platform.core.get_document_by_id`
   - `platform.core.get_index_mapping`
4. Paste system instruction from `agent/system_instruction.md`
5. Save agent

### Step 5: Create Dashboards

1. Create **Mayor Command Center** dashboard in Kibana
2. Create **Citizen Dashboard** with map visualization
3. Configure data view for `civicpulse_complaints` index

---

## 🔧 Tools Used

| Tool | Purpose |
|------|---------|
| Elastic Agent Builder | AI agent with system instructions and tool integration |
| ES\|QL | Structured queries for aggregations and analysis |
| Elasticsearch | Data storage, search, and aggregations |
| Kibana Dashboards | Strategic and operational visualizations |
| Python | Data ingestion and streaming pipeline |

---

## 🎥 Demo

[Watch Demo Video →](YOUR_YOUTUBE_LINK)

---

## 📊 Index Schema

| Field | Type | Description |
|-------|------|-------------|
| `complaint_id` | keyword | Unique identifier |
| `district` | text + keyword | North / South / East / West |
| `category` | text + keyword | Complaint category |
| `status` | text + keyword | Open / Closed |
| `priority` | text + keyword | Low / Medium / High |
| `sla_breached` | boolean | SLA compliance flag |
| `escalated` | boolean | Escalation flag |
| `created_at` | date | Creation timestamp |
| `resolved_at` | date | Resolution timestamp |
| `days_open` | long | Days since creation |
| `resolution_time_days` | long | Time to resolve |
| `sla_days` | long | SLA target days |
| `geo_location` | geo_point | Lat/lon coordinates |

---

## 📊 Dashboards (NDJSON Export)

This file contains:
- Mayor Command Center Dashboard
- Citizen Service Agent Dashboard
- Associated visualizations and saved objects

**Import via:** Kibana → Stack Management → Saved Objects → Import

---

## 👤 Author

Built for the **Elasticsearch Agent Builder Hackathon 2026**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.