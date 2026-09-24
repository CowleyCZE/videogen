import json, os, tempfile
os.environ.setdefault("QUEUE_TOKEN", "test-token")
os.environ["QUEUE_DB"] = tempfile.mktemp(suffix=".sqlite3")
from jsonschema import Draft202012Validator
from queue_service.app import app

schema = json.load(open("schemas/release_plan.json", encoding="utf-8"))
plan = {
    "schema_version":"1.0", "release_id":"TEST_001", "song":"Test",
    "strategy":"release_day", "release_day":"2026-10-02", "spotify_url":None,
    "clips":[{"id":"clip_01","start":1.0,"end":12.0,"platforms":["tiktok"],"purpose":"hook","format":"9:16","resolution":"1080x1920","hook":"Test"}],
    "posts":[{"id":"post_01","platform":"tiktok","type":"draft","publish_at":"2026-10-02T12:00:00Z","clip_id":"clip_01","caption":"Test","cta":"YouTube","hashtags":["#test"],"title":None,"tiktok_mode":"draft"}]
}
Draft202012Validator(schema).validate(plan)
client = app.test_client(); headers = {"Authorization":"Bearer test-token"}
r = client.post("/v1/jobs", json={"job_id":"TEST_001", "release_id":"TEST_001", "source":"x.mp4", "release_plan":plan}, headers=headers)
assert r.status_code == 202
r = client.post("/v1/jobs/claim", headers=headers); assert r.status_code == 200 and r.json["job_id"] == "TEST_001"
r = client.post("/v1/jobs/TEST_001/complete", json={"files":[]}, headers=headers); assert r.status_code == 200
r = client.get("/v1/jobs/TEST_001", headers=headers); assert r.json["status"] == "completed"
print("schema-ok queue-lifecycle-ok")
