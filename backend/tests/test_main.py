import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_image_bytes():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model" in body


def test_remove_bg_success(client, sample_image_bytes):
    response = client.post(
        "/remove-bg",
        files={"file": ("sample.jpg", sample_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_remove_bg_rejects_wrong_content_type(client):
    fake_text_file = b"this is not an image"
    response = client.post(
        "/remove-bg",
        files={"file": ("not_an_image.txt", fake_text_file, "text/plain")},
    )
    assert response.status_code == 400


def test_remove_bg_rejects_empty_file(client):
    response = client.post(
        "/remove-bg",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400


def test_remove_bg_requires_file(client):
    response = client.post("/remove-bg")
    assert response.status_code == 422
