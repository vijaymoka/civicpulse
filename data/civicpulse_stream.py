import random
import uuid
import time
import sys
import threading
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch, helpers

# ==================================
# 🔐 ELASTIC CONNECTION
# ==================================
ELASTIC_URL = "https://my-elasticsearch-project-dc90bb.es.us-central1.gcp.elastic.cloud:443"
API_KEY = "MGktcG1ad0JheVhCa1lQYThRb086SHBkNUdYSU5lOWFpc3pSWW0yYWdoUQ=="
INDEX_NAME = "civicpulse_complaints"

MAX_RECORDS = 5000
STREAM_INTERVAL = 5

es = Elasticsearch(
    ELASTIC_URL,
    api_key=API_KEY
)

# ==================================
# 🗺 DISTRICTS + GEO CENTERS
# ==================================
districts = {
    "East":  (40.75, -73.80),
    "North": (40.82, -73.92),
    "South": (40.65, -73.95),
    "West":  (40.73, -74.00)
}

# Category weights - "Other" is kept minimal (8%)
categories = [
    "Garbage",
    "Water Leak",
    "Power Outage",
    "Road Damage",
    "Sanitation",
    "Noise",
    "Other"
]

# Weighted distribution: Other = 8%, rest distributed evenly
category_weights = [0.18, 0.18, 0.18, 0.18, 0.15, 0.15, 0.08]

priorities = ["Low", "Medium", "High"]

sla_map = {
    "Low": 10,
    "Medium": 7,
    "High": 3
}

district_risk_factor = {
    "East": 0.20,
    "North": 0.30,
    "South": 0.45,
    "West": 0.28
}

CRISIS_MODE = False

# ==================================
# 🏗 INDEX SETUP WITH CORRECT MAPPING
# ==================================
def setup_index():
    """Create index with proper geo_point mapping if it doesn't exist"""
    
    mapping = {
        "mappings": {
            "properties": {
                "complaint_id": {"type": "keyword"},
                "district": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "category": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "priority": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "status": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "sla_days": {"type": "long"},
                "days_open": {"type": "long"},
                "resolution_time_days": {"type": "long"},
                "escalated": {"type": "boolean"},
                "sla_breached": {"type": "boolean"},
                "created_at": {"type": "date"},
                "resolved_at": {"type": "date"},
                "geo_location": {"type": "geo_point"}
            }
        }
    }
    
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"✅ Created index '{INDEX_NAME}' with correct geo_point mapping")
    else:
        current_mapping = es.indices.get_mapping(index=INDEX_NAME)
        geo_field = current_mapping[INDEX_NAME]["mappings"]["properties"].get("geo_location", {})
        
        if geo_field.get("type") != "geo_point":
            print("⚠️  WARNING: Index exists but geo_location is not geo_point type!")
            print("   Consider reindexing or creating a new index with correct mapping.")
        else:
            print(f"✅ Index '{INDEX_NAME}' exists with correct mapping")

# ==================================
# 📍 GEO GENERATOR
# ==================================
def generate_location(lat, lon):
    """Generate geo_point in correct format for Elasticsearch"""
    actual_lat = lat + random.uniform(-0.01, 0.01)
    actual_lon = lon + random.uniform(-0.01, 0.01)
    
    return {
        "lat": actual_lat,
        "lon": actual_lon
    }

# ==================================
# 🧠 RECORD GENERATOR (GHC OPTIMIZED)
# ==================================
def generate_record():
    global CRISIS_MODE

    district = random.choice(list(districts.keys()))
    base_lat, base_lon = districts[district]

    # Use weighted category selection to keep "Other" at ~8%
    category = random.choices(categories, weights=category_weights)[0]
    
    priority = random.choices(priorities, weights=[0.4, 0.4, 0.2])[0]
    sla_days = sla_map[priority]

    # Spread created_at over last 30 days
    created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))

    # ==================================
    # 🎯 GHC TARGET: 65-70 (Normal Mode)
    # ==================================
    # GHC Formula:
    # (100 - SLA_breach%) * 0.4 + (100 - escalation%) * 0.3 + closure% * 0.3
    #
    # Target breakdown for GHC ~67-68:
    # - SLA breach rate: ~20% → contributes 32 points (80 * 0.4)
    # - Escalation rate: ~25% → contributes 22.5 points (75 * 0.3)
    # - Closure rate: ~65% → contributes 19.5 points (65 * 0.3)
    # Total: ~74 points (adjusted below)

    if not CRISIS_MODE:
        # Normal mode: Target GHC 65-70
        days_open = random.randint(0, 12)
        
        # SLA breach: ~25% of cases
        sla_breached = days_open > sla_days and random.random() < 0.25
        
        # Escalation: ~20% base + district risk
        escalated = False
        if sla_breached and random.random() < 0.7:  # 70% of breaches escalate
            escalated = True
        elif random.random() < (district_risk_factor[district] * 0.5):  # Reduced district impact
            escalated = True
        
        # Closure rate: ~65% to hit target
        status = "Closed" if random.random() < 0.65 else "Open"

    else:
        # ==================================
        # 🚨 CRISIS MODE: GHC drops to ~40-50
        # ==================================
        days_open = random.randint(5, 20)
        
        # Increase SLA breaches to ~50%
        sla_breached = days_open > sla_days or random.random() < 0.5
        
        # Increase escalations to ~45%
        escalated = sla_breached or random.random() < 0.45
        
        # Reduce closure rate to ~40%
        status = "Closed" if random.random() < 0.40 else "Open"
        
        # South district hit hardest
        if district == "South":
            sla_breached = True
            escalated = True
            days_open += 5
            status = "Open" if random.random() < 0.8 else "Closed"

    resolved_at = None
    resolution_time_days = None

    if status == "Closed":
        resolution_time_days = random.randint(1, 10)
        resolved_at = created_at + timedelta(days=resolution_time_days)

    return {
        "complaint_id": str(uuid.uuid4()),
        "district": district,
        "category": category,
        "priority": priority,
        "sla_days": sla_days,
        "days_open": days_open,
        "status": status,
        "escalated": escalated,
        "sla_breached": sla_breached,
        "created_at": created_at,
        "resolved_at": resolved_at,
        "resolution_time_days": resolution_time_days,
        "geo_location": generate_location(base_lat, base_lon)
    }

# ==================================
# ♻ ROLLING RETENTION (REAL CAP)
# ==================================
def apply_rolling_retention():
    try:
        count = es.count(index=INDEX_NAME)["count"]

        if count > MAX_RECORDS:
            excess = count - MAX_RECORDS

            response = es.search(
                index=INDEX_NAME,
                size=excess,
                sort=[{"created_at": {"order": "asc"}}],
                _source=False
            )

            ids_to_delete = [hit["_id"] for hit in response["hits"]["hits"]]

            actions = [
                {
                    "_op_type": "delete",
                    "_index": INDEX_NAME,
                    "_id": doc_id
                }
                for doc_id in ids_to_delete
            ]

            if actions:
                helpers.bulk(es, actions)
    except Exception as e:
        print(f"❌ Error in retention: {e}")

# ==================================
# 📊 CALCULATE CURRENT GHC
# ==================================
def calculate_ghc():
    """Calculate current GHC score from index data"""
    try:
        # Get aggregations
        agg_query = {
            "size": 0,
            "aggs": {
                "total": {"value_count": {"field": "complaint_id"}},
                "sla_breached": {"filter": {"term": {"sla_breached": True}}},
                "escalated": {"filter": {"term": {"escalated": True}}},
                "closed": {"filter": {"term": {"status.keyword": "Closed"}}}
            }
        }
        
        result = es.search(index=INDEX_NAME, body=agg_query)
        
        total = result["aggregations"]["total"]["value"]
        if total == 0:
            return 0
        
        sla_breach_count = result["aggregations"]["sla_breached"]["doc_count"]
        escalated_count = result["aggregations"]["escalated"]["doc_count"]
        closed_count = result["aggregations"]["closed"]["doc_count"]
        
        sla_breach_pct = (sla_breach_count / total) * 100
        escalation_pct = (escalated_count / total) * 100
        closure_pct = (closed_count / total) * 100
        
        ghc = (
            ((100 - sla_breach_pct) * 0.4) +
            ((100 - escalation_pct) * 0.3) +
            (closure_pct * 0.3)
        )
        
        return round(ghc, 1)
    except:
        return 0

# ==================================
# 🔥 CRISIS TOGGLE THREAD
# ==================================
def key_listener():
    global CRISIS_MODE

    while True:
        try:
            key = input().strip().lower()

            if key == "c":
                CRISIS_MODE = True
                print("🚨 Crisis Mode Activated - GHC will drop to ~40-50")
            elif key == "n":
                CRISIS_MODE = False
                print("✅ Crisis Mode Deactivated - GHC will stabilize at ~65-70")
            elif key == "q":
                print("🛑 Exiting stream...")
                sys.exit()
        except EOFError:
            time.sleep(1)
        except Exception as e:
            print(f"Input error: {e}")

# ==================================
# 🚀 STREAM ENGINE
# ==================================
def start_stream():
    print("🚀 CivicPulse Rolling Stream Engine Running")
    print("📊 Target GHC: 65-70 (Normal) | 40-50 (Crisis)")
    print("📁 'Other' category capped at ~8%")
    print("Press 'c' for crisis, 'n' to normalize, 'q' to quit")

    threading.Thread(target=key_listener, daemon=True).start()

    while True:
        try:
            batch_size = random.randint(5, 15)

            actions = [
                {
                    "_index": INDEX_NAME,
                    "_source": generate_record()
                }
                for _ in range(batch_size)
            ]

            helpers.bulk(es, actions)

            apply_rolling_retention()

            total = es.count(index=INDEX_NAME)["count"]
            ghc = calculate_ghc()

            crisis_indicator = "🚨" if CRISIS_MODE else "✅"
            print(f"{crisis_indicator} Inserted {batch_size} | Total: {total} | GHC: {ghc} | Crisis: {CRISIS_MODE}")

            time.sleep(STREAM_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Stream stopped by user")
            sys.exit()
        except Exception as e:
            print(f"❌ Error in stream: {e}")
            time.sleep(STREAM_INTERVAL)

# ==================================
# 🏁 MAIN
# ==================================
if __name__ == "__main__":
    try:
        setup_index()
        start_stream()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")