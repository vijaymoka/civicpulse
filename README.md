# CivicPulse

CivicPulse is a deterministic, multi-step AI agent built with Elastic Agent Builder that analyzes public complaint data to prioritize issues, predict service delays, and generate explainable operational insights.

## Problem
Public agencies receive millions of complaints across systems like 311 service requests and federal consumer complaint portals. Existing tools rely on static dashboards and manual review, making it difficult to detect emerging issues, predict SLA breaches, and prioritize limited resources.

## Demo Application
This repository includes a lightweight Streamlit application located in the `/app` directory.
The app demonstrates a live execution of the CivicPulse agent workflow, showing how public
complaint data is analyzed, prioritized, and explained using Elastic Agent Builder and
Elasticsearch-backed reasoning.


## Solution
CivicPulse treats Elasticsearch as the primary reasoning engine and uses LLMs only for orchestration and explanation. The agent ingests publicly available U.S. complaint data, normalizes it into a canonical schema, and performs deterministic analytics to generate traceable, reproducible decisions.

## Key Features
- Multi-step agent using Elastic Agent Builder
- Deterministic trend and anomaly detection
- SLA breach risk prediction
- Geospatial and fairness analysis
- Explainable priority queues
- Optional LLM-assisted explanation mode

## Why Elastic
This project demonstrates how Elastic Agent Builder can orchestrate complex analytical workflows where Elasticsearch performs scalable, explainable reasoning over large datasets.

## Data
Uses publicly available U.S. open data (311-style datasets) and synthetic samples. No personal data enrichment.

## Demo
See demo script in the `/demo` folder.

## Ingestion
Public complaint datasets are ingested into Elasticsearch using a deterministic pipeline with explicit source detection and field normalization. The AI agent operates exclusively on indexed data.

## Running the Demo
To run the demo application locally:

```bash
python -m streamlit run app/app.py


## Notes
The demo application is designed to illustrate agent orchestration and explainability.
All rankings are derived from deterministic Elasticsearch logic; the AI agent only
coordinates steps and explains results.


