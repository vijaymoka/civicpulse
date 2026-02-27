import random
import uuid
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch, helpers

# ----------------------------------
# 🔐 ELASTIC CONNECTION
# ----------------------------------
ELASTIC_URL = "https://my-elasticsearch-project-dc90bb.es.us-central1.gcp.elastic.cloud:443"
API_KEY = "MGktcG1ad0JheVhCa1lQYThRb086SHBkNUdYSU5lOWFpc3pSWW0yYWdoUQ=="

INDEX_NAME = "civicpulse_complaints"
NUM_RECORDS = 5000

es = Elasticsearch(
    ELASTIC_URL,
    api_key=API_KEY
)

# ----------------------------------
# 🗺 DISTRICT CENTERS (NYC STYLE)
# ----------------------------------
districts = {
    "East":  (40.75, -73.80),
    "North": (40.82, -73.92),
    "South": (40.65, -73.95),
    "West":  (40.73, -74.00)
}

district_weights = {
    "East": 0.20,
    "North": 0.25,
    "South": 0.35,   # higher volume
    "West": 0.20
}

# ----------------------------------
# 🏛 CATEGORIES WITH CONTROLLED "OTHER"
# ----------------------------------
categories = [
    "Garbage",
    "Water Leak",
    "Power Outage",
    "Road Damage",
    "Sanitation",
    "Noise",
    "Pothole",
    "Streetlight",
    "Illegal Dumping",
    "Vandalism",
    "Other"  # Kept minimal
]

# Weights ensure "Other" stays at ~8%
category_weights = [
    0.15,  # Garbage
    0.12,  # Water Leak
    0.11,  # Power Outage
    0.13,  # Road Damage
    0.10,  # Sanitation
    0.09,  # Noise
    0.10,  # Pothole
    0.08,  # Streetlight
    0.06,  # Illegal Dumping
    0.06,  # Vandalism
    0.08   # Other - CAPPED AT 8%
]

priorities = ["Low", "Medium", "High"]

sla_map = {
    "Low": 10,
    "Medium": 7,
    "High": 3
}

district_risk_factor = {
    "East": 0.20,
    "North": 0.30,
    "South": 0.45,   # stressed governance
    "West": 0.28
}

# ----------------------------------
# 📍 GEO GENERATOR (FIXED FOR GEO_POINT)
# ----------------------------------
def generate_location(lat, lon):
    """Generate geo_point in correct format"""
    actual_lat = lat + random.uniform(-0.01, 0.01)
    actual_lon = lon + random.uniform(-0.01, 0.01)
    
    return {
        "lat": actual_lat,
        "lon": actual_lon
    }

# ----------------------------------
# 🧠 RECORD GENERATOR (GHC OPTIMIZED)
# ----------------------------------
def generate_record():
    """
    Generate record targeting GHC of 65-70
    
    GHC Formula:
    (100 - SLA_breach%) * 0.4 + (100 - escalation%) * 0.3 + closure% * 0.3
    
    Target breakdown:
    - SLA breach rate: ~25% → contributes ~30 points
    - Escalation rate: ~20% → contributes ~24 points
    - Closure rate: ~65% → contributes ~19.5 points
    Total GHC: ~67-70
    """
    
    district = random.choices(
        list(districts.keys()),
        weights=list(district_weights.values())
    )[0]
    
    base_lat, base_lon = districts[district]
    
    # Use weighted category selection to keep "Other" at ~8%
    category = random.choices(categories, weights=category_weights)[0]
    
    priority = random.choices(priorities, weights=[0.4, 0.4, 0.2])[0]
    sla_days = sla_map[priority]
    
    # Spread records over last 180 days
    created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 180))
    
    # Controlled days_open for GHC targeting
    days_open = random.randint(0, 12)
    
    # --------------------------
    # SLA BREACH (~25% rate)
    # --------------------------
    sla_breached = days_open > sla_days and random.random() < 0.25
    
    # --------------------------
    # ESCALATION LOGIC (~20% rate)
    # --------------------------
    escalated = False
    
    if sla_breached and random.random() < 0.7:  # 70% of breaches escalate
        escalated = True
    elif random.random() < (district_risk_factor[district] * 0.5):  # Reduced district impact
        escalated = True
    elif priority == "High" and days_open > 4 and random.random() < 0.3:
        escalated = True
    
    # --------------------------
    # STATUS (~65% closure rate)
    # --------------------------
    status = "Closed" if random.random() < 0.65 else "Open"
    
    resolved_at = None
    resolution_time_days = None
    
    if status == "Closed":
        resolution_time_days = max(1, days_open)
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

# ----------------------------------
# 📊 CALCULATE GHC FROM GENERATED DATA
# ----------------------------------
def calculate_ghc_from_records(records):
    """Calculate expected GHC from generated records"""
    total = len(records)
    sla_breached = sum(1 for r in records if r["sla_breached"])
    escalated = sum(1 for r in records if r["escalated"])
    closed = sum(1 for r in records if r["status"] == "Closed")
    
    sla_breach_pct = (sla_breached / total) * 100
    escalation_pct = (escalated / total) * 100
    closure_pct = (closed / total) * 100
    
    ghc = (
        ((100 - sla_breach_pct) * 0.4) +
        ((100 - escalation_pct) * 0.3) +
        (closure_pct * 0.3)
    )
    
    return {
        "ghc": round(ghc, 1),
        "sla_breach_pct": round(sla_breach_pct, 1),
        "escalation_pct": round(escalation_pct, 1),
        "closure_pct": round(closure_pct, 1)
    }

# ----------------------------------
# 📊 CALCULATE CATEGORY DISTRIBUTION
# ----------------------------------
def calculate_category_distribution(records):
    """Calculate category distribution percentages"""
    total = len(records)
    category_counts = {}
    
    for record in records:
        cat = record["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    distribution = {
        cat: round((count / total) * 100, 1)
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    }
    
    return distribution

# ----------------------------------
# 🚀 INGESTION
# ----------------------------------
def ingest():
    
    print("🔄 Resetting index...")
    
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    # ✅ CORRECT MAPPING WITH GEO_POINT
    es.indices.create(
        index=INDEX_NAME,
        mappings={
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
                "geo_location": {"type": "geo_point"}  # ✅ CORRECT TYPE
            }
        }
    )
    
    print(f"📝 Generating {NUM_RECORDS} records...")
    
    records = []
    actions = []
    
    for _ in range(NUM_RECORDS):
        record = generate_record()
        records.append(record)
        actions.append({
            "_index": INDEX_NAME,
            "_source": record
        })
    
    # Calculate metrics before ingestion
    print("\n📊 Pre-Ingestion Analysis:")
    print("=" * 50)
    
    ghc_stats = calculate_ghc_from_records(records)
    print(f"🎯 Target GHC Score: {ghc_stats['ghc']}")
    print(f"   - SLA Breach Rate: {ghc_stats['sla_breach_pct']}%")
    print(f"   - Escalation Rate: {ghc_stats['escalation_pct']}%")
    print(f"   - Closure Rate: {ghc_stats['closure_pct']}%")
    
    print(f"\n📁 Category Distribution:")
    cat_dist = calculate_category_distribution(records)
    for cat, pct in cat_dist.items():
        indicator = "⚠️ " if cat == "Other" and pct > 10 else "✅"
        print(f"   {indicator} {cat}: {pct}%")
    
    print("\n" + "=" * 50)
    print("💾 Bulk inserting to Elasticsearch...")
    
    helpers.bulk(es, actions)
    
    print(f"✅ Successfully inserted {NUM_RECORDS} records")
    print(f"📍 Index: {INDEX_NAME}")
    print(f"🗺️  Geo-location: Properly formatted as geo_point")
    print(f"\n💡 Tip: Refresh your Kibana data view to see updated fields")

# ----------------------------------
# ▶ RUN
# ----------------------------------
if __name__ == "__main__":
    ingest()