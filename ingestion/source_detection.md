# Source Detection

CivicPulse uses deterministic, rule-based source detection to identify the type of complaint dataset being ingested.

## Detection Rules

### 311-Style Datasets
Detected if fields include:
- complaint_type
- agency
- created_date

Examples:
- NYC 311
- SF 311
- Other U.S. city service request datasets

### Federal / Consumer Complaint Datasets
Detected if fields include:
- Product
- Company
- Consumer complaint narrative

Examples:
- CFPB Consumer Complaint Database

## Design Choice
Source detection is rule-based and deterministic.
No LLMs are used during ingestion to ensure reproducibility and low cost.
