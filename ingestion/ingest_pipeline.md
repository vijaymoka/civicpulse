# Data Ingestion Pipeline

CivicPulse uses a deterministic ingestion pipeline to load publicly available complaint-style datasets into Elasticsearch.

## Supported Formats
- CSV (e.g., 311 service request datasets)
- JSON (federal or city open-data APIs)

## Ingestion Steps
1. Source dataset is provided as CSV or JSON
2. Fields are normalized into a canonical schema
3. Derived metrics (resolution time, SLA breach) are computed
4. Data is indexed into Elasticsearch before agent execution

No LLMs are used during ingestion.
