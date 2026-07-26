import json
from pathlib import Path
from pymongo import MongoClient

# ==========================================================
# GRAPHMIND AI - MONGODB LOADER
# ==========================================================

print("=" * 60)
print("GRAPHMIND AI - MONGODB LOADER")
print("=" * 60)

# ----------------------------------------------------------
# Connect to MongoDB
# ----------------------------------------------------------

try:
    client = MongoClient("mongodb://localhost:27017")
    client.admin.command("ping")
    print("\n[OK] Connected to MongoDB")
except Exception as e:
    print("\n[ERROR] Could not connect to MongoDB")
    print(e)
    exit()

# ----------------------------------------------------------
# Database & Collection
# ----------------------------------------------------------

db = client["graphmind_ai"]
collection = db["website_entities"]

# ----------------------------------------------------------
# JSON File
# ----------------------------------------------------------

json_file = Path("data/merged/unified_knowledge_base.json")

if not json_file.exists():
    print(f"\n[ERROR] File not found:\n{json_file}")
    exit()

print("\nLoading JSON file...")

try:
    with open(json_file, "r", encoding="utf-8") as f:
        records = json.load(f)
except Exception as e:
    print("\n[ERROR] Failed to read JSON")
    print(e)
    exit()

print(f"[OK] Records found : {len(records)}")

# ----------------------------------------------------------
# Clear Existing Collection
# ----------------------------------------------------------

print("\nClearing old records...")

collection.delete_many({})

print("[OK] Collection cleared")

# ----------------------------------------------------------
# Insert Records
# ----------------------------------------------------------

print("\nInserting records into MongoDB...")

if len(records) > 0:
    result = collection.insert_many(records)
    print(f"[OK] Inserted {len(result.inserted_ids)} documents")
else:
    print("[WARNING] No records found to insert")

# ----------------------------------------------------------
# Verification
# ----------------------------------------------------------

count = collection.count_documents({})

print("\nVerification")

print("-" * 40)
print("Database   :", db.name)
print("Collection :", collection.name)
print("Documents  :", count)
print("-" * 40)

sample = collection.find_one()

if sample:
    print("\nSample document:")
    print("-" * 40)
    print(json.dumps(sample, indent=4, default=str))
    print("-" * 40)

print("\n" + "=" * 60)
print("UPLOAD COMPLETED SUCCESSFULLY")
print("=" * 60)