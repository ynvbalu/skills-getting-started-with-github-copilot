import sys
from pathlib import Path
import json

# make src/ available on sys.path so we can import app
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # expect some known activities from the in-memory DB
    assert "Chess Club" in data


def test_signup_and_duplicate():
    email = "test_student@example.com"
    activity = "Chess Club"

    # ensure not present initially
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # cleanup before test
        client.post(f"/activities/{activity}/unregister?email={email}")

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # signing up again should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")


def test_unregister_not_signed():
    email = "not_signed@example.com"
    activity = "Chess Club"

    # ensure not present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.post(f"/activities/{activity}/unregister?email={email}")

    # attempt to unregister when not signed should return 400
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400