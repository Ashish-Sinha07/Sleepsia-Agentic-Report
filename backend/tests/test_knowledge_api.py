"""Knowledge admin API tests (spec section 19.F/E): auth gate, upload
validation, list/delete, all against an isolated temporary vector store so
the real indexed knowledge base is never touched by the test suite.
"""

import io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

TEST_ADMIN_KEY = "test-admin-key-for-pytest"


@pytest.fixture(autouse=True)
def isolated_knowledge_base(monkeypatch, tmp_path):
    import app.api.routes.knowledge as knowledge_routes
    from app.rag.vector_store import ChromaVectorStore
    from app.config import settings

    temp_store = ChromaVectorStore(persist_path=str(tmp_path / "chroma"), collection_name="test_knowledge_api")
    monkeypatch.setattr(knowledge_routes, "get_vector_store", lambda: temp_store)
    monkeypatch.setattr(settings, "KNOWLEDGE_ADMIN_API_KEY", TEST_ADMIN_KEY)
    yield


def test_upload_without_admin_key_is_rejected(client):
    response = client.post(
        "/api/knowledge/upload", files={"file": ("rules.md", io.BytesIO(b"# Rule\n\nBody"), "text/markdown")}
    )
    assert response.status_code == 401


def test_upload_with_wrong_admin_key_is_rejected(client):
    response = client.post(
        "/api/knowledge/upload",
        files={"file": ("rules.md", io.BytesIO(b"# Rule\n\nBody"), "text/markdown")},
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_upload_valid_markdown_succeeds(client):
    response = client.post(
        "/api/knowledge/upload",
        files={"file": ("rules.md", io.BytesIO(b"# Rule\n\nBody text here."), "text/markdown")},
        headers={"X-Admin-Key": TEST_ADMIN_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_created"] >= 1


def test_upload_rejects_disallowed_extension(client):
    response = client.post(
        "/api/knowledge/upload",
        files={"file": ("malware.exe", io.BytesIO(b"MZ..."), "application/octet-stream")},
        headers={"X-Admin-Key": TEST_ADMIN_KEY},
    )
    assert response.status_code == 400


def test_list_then_delete_document(client):
    client.post(
        "/api/knowledge/upload",
        files={"file": ("to_delete.md", io.BytesIO(b"# X\n\nY"), "text/markdown")},
        headers={"X-Admin-Key": TEST_ADMIN_KEY},
    )
    listing = client.get("/api/knowledge/documents", headers={"X-Admin-Key": TEST_ADMIN_KEY})
    assert listing.status_code == 200
    assert any(d["source_file"] == "to_delete.md" for d in listing.json())

    delete_resp = client.delete("/api/knowledge/documents/to_delete.md", headers={"X-Admin-Key": TEST_ADMIN_KEY})
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_chunks"] >= 1

    listing_after = client.get("/api/knowledge/documents", headers={"X-Admin-Key": TEST_ADMIN_KEY})
    assert not any(d["source_file"] == "to_delete.md" for d in listing_after.json())


def test_delete_nonexistent_document_returns_404(client):
    response = client.delete("/api/knowledge/documents/does_not_exist.md", headers={"X-Admin-Key": TEST_ADMIN_KEY})
    assert response.status_code == 404


def test_admin_endpoints_disabled_when_no_key_configured(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_ADMIN_API_KEY", "")
    response = client.get("/api/knowledge/documents", headers={"X-Admin-Key": "anything"})
    assert response.status_code == 503
