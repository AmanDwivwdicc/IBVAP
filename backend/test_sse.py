import bcrypt
from dotenv import load_dotenv

from main import supabase

load_dotenv()

# Create a test API key
raw_key = "super-secret-key-123"
hashed = bcrypt.hashpw(raw_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Ensure we have a clean slate
supabase.table("devices").delete().eq("device_id", "edge-sse-test").execute()

# 1. Create a dummy device
res = supabase.table("devices").insert({
    "device_id": "edge-sse-test",
    "name": "Test SSE Device",
    "api_key_hash": hashed
}).execute()

device_uuid = res.data[0]["id"]
print(f"Created device {device_uuid}")

# 2. Add initial device settings
supabase.table("device_settings").insert({
    "device_id": device_uuid,
    "version": "v1-initial",
    "settings": {"confidence_threshold": 0.5, "enabled_plugins": ["object_detection"]}
}).execute()
print("Initial settings added.")
