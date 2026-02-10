# Example ingestion command using Elastic Bulk API

curl -X POST "http://localhost:9200/public_complaints_v1/_bulk" \
  -H "Content-Type: application/json" \
  --data-binary @synthetic_311.ndjson
