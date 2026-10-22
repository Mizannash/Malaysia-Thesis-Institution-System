"""Acceptance tests for centralized API key configuration and modes.
Verifies:
1. Given DEMO_MODE=true and all keys empty -> system boots, /health returns 200, full pipeline runs on fixtures.
2. Given DEMO_MODE=false and both LLM keys empty -> startup fails with a clear human-readable error naming the missing env vars.
3. Given LLM_PROVIDER=deepseek with only OPENAI key set -> adapter falls back and logs the fallback.
"""
import os
import sys
import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app, lifespan
from app.config import Settings, validate_startup_config, settings
from app.ai.llm_adapter import resolve_provider_config, complete, ProviderConfig
from app.schemas import GapAnalysisResponse, GapItem


def test_demo_mode_true_all_keys_empty_pipeline_runs_on_fixtures(monkeypatch):
    """
    Given DEMO_MODE=true and all keys empty:
    -> system boots, /health returns 200, full pipeline runs on fixtures.
    """
    # 1. Clear all external API keys and enforce DEMO_MODE=true
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_KEY", raising=False)
    monkeypatch.delenv("OPENALEX_EMAIL", raising=False)

    # Apply to runtime settings
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", None)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)

    # 2. System boots and /health returns 200
    with TestClient(app) as client:
        health_resp = client.get("/health")
        assert health_resp.status_code == 200
        health_data = health_resp.json()
        assert health_data.get("status") == "ok"

        # 3. Full pipeline runs on fixtures with zero keys
        # Get demo auth token with supervisor role (99 quota)
        import time
        unique_email = f"demo.supervisor.{int(time.time()*1000)}@utm.my"
        auth_resp = client.post("/auth/demo-login", json={
            "email": unique_email,
            "name": "Demo Supervisor Researcher",
            "role": "supervisor",
            "tenant_id": "tenant-utm-001"
        })
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 0: Initialize Research Project
        res_proj = client.post(
            "/projects",
            json={
                "title": "IoT precision agriculture in Malaysia",
                "stage": "search",
                "state_json": {}
            },
            headers=headers
        )
        assert res_proj.status_code == 201
        project_id = res_proj.json()["id"]

        # Step 1: Search acquisition (runs on UTM HTML fixture + OpenAlex fixture/mock)
        res_search = client.post(
            "/api/search",
            json={
                "query": "IoT agriculture Malaysia",
                "scope": "MY",
                "limit": 10,
            },
            headers=headers
        )
        assert res_search.status_code == 200
        search_data = res_search.json()
        papers = search_data.get("papers", [])
        assert len(papers) >= 5

        # Step 2: Gap Analysis (runs on gap_fixture.json)
        res_gap = client.post(
            f"/projects/{project_id}/stage/gap",
            json={"project_id": project_id, "papers": papers},
            headers=headers
        )
        assert res_gap.status_code == 200
        gap_data = res_gap.json()
        gaps = gap_data["state_json"]["gaps"]
        assert len(gaps) >= 1
        chosen_gap = gaps[0]["gap_id"]

        # Step 3: Title Suggestions (runs on title_fixture.json)
        res_title = client.post(
            f"/projects/{project_id}/stage/title",
            json={"project_id": project_id, "gap_id": chosen_gap, "language": "EN"},
            headers=headers
        )
        assert res_title.status_code == 200
        title_data = res_title.json()
        titles = title_data["state_json"]["titles"]
        assert len(titles) >= 2
        chosen_title = titles[0]["title"]

        # Step 4: Deep-Dive Literature (runs on deepdive_fixture.json)
        res_deep = client.post(
            f"/projects/{project_id}/stage/deepdive",
            json={"project_id": project_id, "gap_id": chosen_gap, "chosen_title": chosen_title},
            headers=headers
        )
        assert res_deep.status_code == 200
        deep_data = res_deep.json()
        assert len(deep_data["state_json"]["deepdive_papers"]) >= 1

        # Step 5: Research Plan Generation (runs on plan_fixture.json)
        res_plan = client.post(
            f"/projects/{project_id}/stage/plan",
            json={"project_id": project_id},
            headers=headers
        )
        assert res_plan.status_code == 200
        plan_data = res_plan.json()
        assert plan_data["plan_id"] is not None
        assert "plan" in plan_data["state_json"]

        # Direct test on llm_adapter.complete in DEMO_MODE with all keys empty
        gap_obj = complete(
            prompt="Identify thesis gap",
            schema=GapAnalysisResponse,
            stage="test_demo_mode",
            user="demo@utm.my",
        )
        assert isinstance(gap_obj, GapAnalysisResponse)
        assert len(gap_obj.gaps) >= 1


def test_demo_mode_false_both_llm_keys_empty_startup_fails(monkeypatch):
    """
    Given DEMO_MODE=false and both LLM keys empty:
    -> startup fails with a clear human-readable error naming the missing env vars.
    """
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    # 1. Pydantic Settings validation directly raises ValueError naming both missing env vars
    with pytest.raises((ValueError, Exception)) as exc_info:
        Settings(
            DEMO_MODE=False,
            DEEPSEEK_API_KEY=None,
            OPENAI_API_KEY=None,
        )
    err_str = str(exc_info.value)
    assert "DEEPSEEK_API_KEY" in err_str, f"Error did not name DEEPSEEK_API_KEY: {err_str}"
    assert "OPENAI_API_KEY" in err_str, f"Error did not name OPENAI_API_KEY: {err_str}"

    # 2. validate_startup_config also raises RuntimeError naming the missing env vars
    dummy_settings = Settings(DEMO_MODE=True)
    dummy_settings.DEMO_MODE = False
    dummy_settings.DEEPSEEK_API_KEY = None
    dummy_settings.OPENAI_API_KEY = None

    with pytest.raises(RuntimeError) as exc_startup:
        validate_startup_config(dummy_settings)
    startup_msg = str(exc_startup.value)
    assert "DEEPSEEK_API_KEY" in startup_msg
    assert "OPENAI_API_KEY" in startup_msg

    # 3. LLM adapter complete() raises RuntimeError when DEMO_MODE is false without keys
    with pytest.raises(RuntimeError) as exc_adapter:
        complete(
            prompt="Analyze gap",
            schema=GapAnalysisResponse,
            current_settings=dummy_settings,
        )
    adapter_msg = str(exc_adapter.value)
    assert "DEEPSEEK_API_KEY" in adapter_msg
    assert "OPENAI_API_KEY" in adapter_msg

    # 4. App lifespan fails at startup with the human-readable error
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", None)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)

    with pytest.raises(RuntimeError) as exc_app:
        with TestClient(app):
            pass
    assert "DEEPSEEK_API_KEY" in str(exc_app.value)
    assert "OPENAI_API_KEY" in str(exc_app.value)


def test_llm_provider_deepseek_fallback_to_openai_logged(monkeypatch, caplog):
    """
    Given LLM_PROVIDER=deepseek with only OPENAI key set:
    -> adapter falls back and logs the fallback.
    """
    # 1. Configure provider as deepseek, DEEPSEEK key empty, OPENAI key present
    test_settings = Settings(
        DEMO_MODE=True,
        LLM_PROVIDER="deepseek",
        DEEPSEEK_API_KEY=None,
        OPENAI_API_KEY="sk-mock-openai-key-for-fallback-test",
    )

    # 2. Resolve provider configuration with caplog active
    with caplog.at_level(logging.WARNING):
        cfg = resolve_provider_config(test_settings)

    # Check that it resolved to OpenAI and logged the fallback
    assert cfg.provider == "openai"
    assert cfg.model == "gpt-4o-mini"
    assert cfg.fallback_from == "deepseek"
    assert "Falling back to OpenAI provider" in caplog.text

    # 3. Complete call using adapter with mocked HTTP response
    mock_llm_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "gaps": [
                            {
                                "gap_id": "GAP-FALLBACK-01",
                                "description": "Fallback gap analysis produced via OpenAI.",
                                "supporting_paper_ids": ["W1", "W2"]
                            }
                        ]
                    })
                }
            }
        ],
        "usage": {
            "prompt_tokens": 120,
            "completion_tokens": 60,
            "total_tokens": 180
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_llm_response
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        result = complete(
            prompt="Analyze research gaps",
            schema=GapAnalysisResponse,
            stage="test_fallback",
            user="test@utm.my",
            current_settings=test_settings,
        )

        assert isinstance(result, GapAnalysisResponse)
        assert len(result.gaps) == 1
        assert result.gaps[0].gap_id == "GAP-FALLBACK-01"
        assert mock_post.called

        # Confirm post URL target was OpenAI
        called_url = mock_post.call_args[0][0]
        assert "api.openai.com" in called_url


def test_encrypted_api_key_storage_and_toggle_endpoint():
    """
    Verifies:
    1. POST /api/settings/keys encrypts key with AES-256 before writing to DB.
    2. Raw DB field holds ciphertext, never plaintext.
    3. Key preview masks secret (sk-...preview).
    4. POST /api/settings/mode toggles DEMO_MODE.
    5. DELETE /api/settings/keys wipes key safely.
    """
    from app.database import SessionLocal
    from app.models import Tenant
    from app.security import decrypt_api_key

    with TestClient(app) as client:
        # Auth as supervisor for tenant-utm-001
        auth_resp = client.post("/auth/demo-login", json={
            "email": "key.admin@utm.my",
            "name": "Key Admin",
            "role": "supervisor",
            "tenant_id": "tenant-utm-001"
        })
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Save an API key
        raw_key = "sk-live-deepseek-secret-1234567890abcdef"
        post_resp = client.post(
            "/api/settings/keys",
            json={"provider": "deepseek", "api_key": raw_key},
            headers=headers
        )
        assert post_resp.status_code == 200
        data = post_resp.json()
        assert data["has_custom_key"] is True
        assert "cdef" in data["key_preview"]
        assert raw_key not in data["key_preview"]  # Masked!

        # 2. Inspect database directly: ensure zero plaintext
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.id == "tenant-utm-001").first()
            assert tenant is not None
            assert tenant.encrypted_api_key is not None
            assert raw_key not in tenant.encrypted_api_key  # MUST NOT be plaintext!
            # Decrypt with AES-256 to prove round-trip integrity
            decrypted = decrypt_api_key(tenant.encrypted_api_key)
            assert decrypted == raw_key
        finally:
            db.close()

        # 3. GET /api/settings/keys
        get_resp = client.get("/api/settings/keys", headers=headers)
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["has_custom_key"] is True
        assert get_data["provider"] == "deepseek"

        # 4. Toggle DEMO_MODE
        mode_resp = client.post("/api/settings/mode", json={"demo_mode": False}, headers=headers)
        assert mode_resp.status_code == 200
        assert mode_resp.json()["demo_mode"] is False

        # Reset back to DEMO_MODE=True
        mode_reset = client.post("/api/settings/mode", json={"demo_mode": True}, headers=headers)
        assert mode_reset.status_code == 200
        assert mode_reset.json()["demo_mode"] is True

        # 5. DELETE /api/settings/keys
        del_resp = client.delete("/api/settings/keys", headers=headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["has_custom_key"] is False

