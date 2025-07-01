from api.main import app
from pathlib import Path
from fastapi.testclient import TestClient
import duckdb

client = TestClient(app)
FIXTURE = Path(__file__).with_name("vehicle_prices.csv")


def test_upload_and_profile(tmp_path, monkeypatch):
    # Redirect DATA_DIR to a temp folder
    monkeypatch.setattr("api.routers.datasets.DATA_DIR", tmp_path)

    resp = client.post(
        "/datasets/", files={"file": ("vehicle_prices.csv", FIXTURE.read_bytes())}
    )
    assert resp.status_code == 200

    payload = resp.json()
    profile_html = tmp_path / payload["dataset_id"] / "vehicle_prices.profile.html"
    assert profile_html.exists()

    # DuckDB should have a row
    con = duckdb.connect("autostat.duckdb")
    rows = con.execute("SELECT count(*) FROM dataset_meta").fetchone()[0]
    assert rows >= 1
