"""Testes críticos de API pública, autenticação e fluxo editorial."""

import os
import time
import uuid
import requests
import pytest
from pymongo import MongoClient


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
LOGIN_EMAIL = "editor@viarchive.pt"
LOGIN_PASSWORD = "xuToEVZpqyVGmomzaP7x"


@pytest.fixture(scope="session")
def http():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def mongo_db():
    # Limpeza de dados de teste diretamente no Mongo para não deixar registos públicos fictícios.
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        pytest.skip("MONGO_URL/DB_NAME indisponíveis para limpeza de dados de teste.")
    client = MongoClient(mongo_url)
    db = client[db_name]
    yield db
    client.close()


@pytest.fixture(scope="session")
def cleanup_registry():
    return {"entity_ids": set(), "draft_ids": set(), "source_ids": set(), "audit_targets": set()}


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data(mongo_db, cleanup_registry):
    yield
    entity_ids = list(cleanup_registry["entity_ids"])
    draft_ids = list(cleanup_registry["draft_ids"])
    source_ids = list(cleanup_registry["source_ids"])

    if draft_ids:
        mongo_db.drafts.delete_many({"id": {"$in": draft_ids}})
        mongo_db.publications.delete_many({"id": {"$in": draft_ids}})
        mongo_db.assertions.delete_many({"id": {"$regex": f"^({'|'.join(map(lambda x: x.replace('-', '\\-'), draft_ids))})-"}})
        mongo_db.audit_events.delete_many({"target": {"$in": draft_ids}})

    if entity_ids:
        mongo_db.entities.delete_many({"id": {"$in": entity_ids}})
        mongo_db.entity_search.delete_many({"id": {"$in": entity_ids}})
        mongo_db.publications.delete_many({"entity_id": {"$in": entity_ids}})
        mongo_db.assertions.delete_many({"entity_id": {"$in": entity_ids}})

    if source_ids:
        mongo_db.sources.delete_many({"id": {"$in": source_ids}})


def _login(http_session: requests.Session):
    response = http_session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD},
        timeout=20,
    )
    return response


class TestPublicAPI:
    """Contratos públicos: saúde, pesquisa, detalhe, histórico e paginação."""

    def test_base_url_configured(self):
        assert BASE_URL, "REACT_APP_BACKEND_URL ausente no ambiente"

    def test_health(self, http):
        response = http.get(f"{BASE_URL}/api/health", timeout=20)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "VI Archive"

    def test_stats_expected_counts(self, http):
        response = http.get(f"{BASE_URL}/api/v1/stats", timeout=20)
        assert response.status_code == 200
        data = response.json()
        assert data["entities"] == 12
        assert data["types"]["personagem"] == 5
        assert data["types"]["local"] == 7

    def test_search_exact_alias_accent_typo(self, http):
        exact = http.get(f"{BASE_URL}/api/v1/entities?q=Jason", timeout=20)
        accent = http.get(f"{BASE_URL}/api/v1/entities?q=L%C3%BAcia", timeout=20)
        typo = http.get(f"{BASE_URL}/api/v1/entities?q=Jasno", timeout=20)
        assert exact.status_code == 200
        assert accent.status_code == 200
        assert typo.status_code == 200
        exact_data = exact.json()
        accent_data = accent.json()
        typo_data = typo.json()
        assert any(item["slug"] == "jason-duval" for item in exact_data["items"])
        assert any(item["slug"] == "lucia-caminos" for item in accent_data["items"])
        assert typo_data["suggestion"] in ("Jason", "Jason Duval")

    def test_search_pagination_limit_2_without_duplicates(self, http):
        first = http.get(f"{BASE_URL}/api/v1/entities?limit=2", timeout=20)
        assert first.status_code == 200
        data_first = first.json()
        assert len(data_first["items"]) == 2
        cursor = data_first["next_cursor"]
        assert isinstance(cursor, str) and cursor

        second = http.get(f"{BASE_URL}/api/v1/entities?limit=2&cursor={cursor}", timeout=20)
        assert second.status_code == 200
        data_second = second.json()
        first_ids = {item["id"] for item in data_first["items"]}
        second_ids = {item["id"] for item in data_second["items"]}
        assert first_ids.isdisjoint(second_ids)

    def test_entity_detail_and_history(self, http):
        detail = http.get(f"{BASE_URL}/api/v1/entities/jason-duval", timeout=20)
        history = http.get(f"{BASE_URL}/api/v1/entities/jason-duval/history", timeout=20)
        assert detail.status_code == 200
        assert history.status_code == 200
        d = detail.json()
        h = history.json()
        assert d["name"] == "Jason Duval"
        assert len(d["assertions"]) > 0
        assert d["assertions"][0]["source"]["url"].startswith("https://")
        assert len(h) >= 1
        assert h[0]["version"] >= 1

    def test_entity_version_query_and_not_found(self, http):
        v1 = http.get(f"{BASE_URL}/api/v1/entities/jason-duval?version=1", timeout=20)
        missing = http.get(f"{BASE_URL}/api/v1/entities/nao-existe", timeout=20)
        assert v1.status_code == 200
        assert v1.json()["version"] == 1
        assert missing.status_code == 404


class TestAuthAndEditorial:
    """Contratos de sessão, CSRF e cadeia editorial com publicação/histórico/conflito."""

    def test_login_wrong_credentials(self, http):
        response = http.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": LOGIN_EMAIL, "password": "senha-errada"},
            timeout=20,
        )
        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"]

    def test_login_me_and_logout_contracts(self, http):
        login = _login(http)
        assert login.status_code == 200
        data = login.json()
        assert data["user"]["email"] == LOGIN_EMAIL
        assert isinstance(data["csrf"], str) and len(data["csrf"]) > 10

        me = http.get(f"{BASE_URL}/api/v1/auth/me", timeout=20)
        assert me.status_code == 200
        me_data = me.json()
        assert me_data["user"]["email"] == LOGIN_EMAIL

        csrf = data["csrf"]
        logout = http.post(f"{BASE_URL}/api/v1/auth/logout", headers={"X-CSRF-Token": csrf}, timeout=20)
        assert logout.status_code == 200
        assert "Sessão terminada" in logout.json()["message"]

    def test_editorial_requires_cookie(self, http):
        clean = requests.Session()
        clean.headers.update({"Content-Type": "application/json"})
        response = clean.get(f"{BASE_URL}/api/v1/editorial/drafts", timeout=20)
        assert response.status_code == 401

    def test_editorial_post_without_csrf_is_forbidden(self, http):
        login = _login(http)
        assert login.status_code == 200
        payload = {
            "title": "Fonte sem CSRF",
            "url": "https://example.com/csrf-test",
            "publisher": "Example",
            "rights": "Direitos de teste para validar proteção CSRF.",
        }
        response = http.post(f"{BASE_URL}/api/v1/editorial/sources", json=payload, timeout=20)
        assert response.status_code == 403

    def test_editorial_full_flow_with_cleanup(self, http, cleanup_registry):
        login = _login(http)
        assert login.status_code == 200
        csrf = login.json()["csrf"]
        headers = {"X-CSRF-Token": csrf}

        nonce = uuid.uuid4().hex[:8]
        source_payload = {
            "title": f"Fonte Teste QA {nonce}",
            "url": f"https://example.com/vi-archive-{nonce}",
            "publisher": "QA",
            "rights": "Direitos de citação para teste funcional temporário.",
        }
        source_resp = http.post(f"{BASE_URL}/api/v1/editorial/sources", json=source_payload, headers=headers, timeout=20)
        assert source_resp.status_code == 201
        source = source_resp.json()
        cleanup_registry["source_ids"].add(source["id"])

        invalid_source_payload = {
            "snapshot": {
                "slug": f"vi-qa-entidade-{nonce}",
                "name": f"VI QA Entidade {nonce}",
                "type": "personagem",
                "summary": "Resumo de teste para validar rejeição de fonte inexistente no rascunho.",
                "aliases": [f"QA {nonce}"],
                "image": "/media/jason.webp",
                "image_position": "center",
                "label": "Official",
            },
            "assertions": [{
                "property": "Estado",
                "value": "Apenas para teste",
                "source_id": "source-inexistente",
                "excerpt": "Excerto de teste.",
                "locator": "Secção teste",
                "origin": "oficial",
                "nature": "declaracao",
                "verification": "pendente",
                "applicability": "Contexto promocional.",
                "method": "Leitura da fonte.",
                "related_entity_id": None,
                "spoiler": False,
            }],
            "reason": "Validar bloqueio de fonte inexistente",
            "entity_id": None,
            "base_version": 0,
        }
        invalid_draft = http.post(f"{BASE_URL}/api/v1/editorial/drafts", json=invalid_source_payload, headers=headers, timeout=20)
        assert invalid_draft.status_code == 422

        slug = f"vi-qa-entidade-{nonce}"
        name = f"VI QA Entidade {nonce}"
        draft_payload = {
            "snapshot": {
                "slug": slug,
                "name": name,
                "type": "personagem",
                "summary": "Resumo de teste controlado para fluxo editorial completo com publicação e histórico.",
                "aliases": [f"QA {nonce}"],
                "image": "/media/jason.webp",
                "image_position": "center",
                "label": "Official",
            },
            "assertions": [{
                "property": "Ligação",
                "value": "Jason Duval",
                "source_id": source["id"],
                "excerpt": "Excerto de validação editorial para garantir cadeia completa.",
                "locator": "Secção QA",
                "origin": "oficial",
                "nature": "declaracao",
                "verification": "pendente",
                "applicability": "Material promocional.",
                "method": "Leitura comparada da fonte.",
                "related_entity_id": "jason-duval",
                "spoiler": False,
            }],
            "reason": "Teste automatizado do fluxo editorial",
            "entity_id": None,
            "base_version": 0,
        }

        pre_search = http.get(f"{BASE_URL}/api/v1/entities?q={name.replace(' ', '%20')}", timeout=20)
        assert pre_search.status_code == 200
        assert pre_search.json()["total"] == 0

        create = http.post(f"{BASE_URL}/api/v1/editorial/drafts", json=draft_payload, headers=headers, timeout=20)
        assert create.status_code == 201
        draft = create.json()
        draft_id = draft["id"]
        entity_id = draft["entity_id"]
        cleanup_registry["draft_ids"].add(draft_id)
        cleanup_registry["entity_ids"].add(entity_id)

        publish_without_approval = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/publish", headers=headers, timeout=20)
        assert publish_without_approval.status_code == 409

        submit = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/submit", headers=headers, timeout=20)
        assert submit.status_code == 200
        assert submit.json()["status"] == "em_revisao"

        reject = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/review?approve=false", headers=headers, timeout=20)
        assert reject.status_code == 200
        assert reject.json()["status"] == "devolvido"

        submit_again = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/submit", headers=headers, timeout=20)
        assert submit_again.status_code == 200

        approve = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/review?approve=true", headers=headers, timeout=20)
        assert approve.status_code == 200
        assert approve.json()["status"] == "aprovado"

        publish = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/publish", headers=headers, timeout=20)
        assert publish.status_code == 200
        assert publish.json()["version"] == 1

        time.sleep(2)
        post_search = http.get(f"{BASE_URL}/api/v1/entities?q={name.replace(' ', '%20')}", timeout=20)
        assert post_search.status_code == 200
        assert any(item["slug"] == slug for item in post_search.json()["items"])

        detail = http.get(f"{BASE_URL}/api/v1/entities/{slug}", timeout=20)
        assert detail.status_code == 200
        detail_data = detail.json()
        assert detail_data["version"] == 1
        assert detail_data["assertions"][0]["source"]["id"] == source["id"]

        republish = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft_id}/publish", headers=headers, timeout=20)
        assert republish.status_code == 200
        assert "já concluída" in republish.json()["message"]

        draft2_payload = {
            **draft_payload,
            "entity_id": entity_id,
            "base_version": 1,
            "snapshot": {
                **draft_payload["snapshot"],
                "summary": "Resumo v2 de teste para confirmar preservação de histórico e consulta por versão.",
            },
            "reason": "Teste de revisão v2",
        }
        create2 = http.post(f"{BASE_URL}/api/v1/editorial/drafts", json=draft2_payload, headers=headers, timeout=20)
        assert create2.status_code == 201
        draft2 = create2.json()
        cleanup_registry["draft_ids"].add(draft2["id"])

        http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft2['id']}/submit", headers=headers, timeout=20)
        http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft2['id']}/review?approve=true", headers=headers, timeout=20)
        pub2 = http.post(f"{BASE_URL}/api/v1/editorial/drafts/{draft2['id']}/publish", headers=headers, timeout=20)
        assert pub2.status_code == 200
        assert pub2.json()["version"] == 2

        time.sleep(2)
        history = http.get(f"{BASE_URL}/api/v1/entities/{slug}/history", timeout=20)
        assert history.status_code == 200
        versions = [x["version"] for x in history.json()]
        assert versions[:2] == [2, 1]

        version1 = http.get(f"{BASE_URL}/api/v1/entities/{slug}?version=1", timeout=20)
        version2 = http.get(f"{BASE_URL}/api/v1/entities/{slug}", timeout=20)
        assert version1.status_code == 200
        assert version2.status_code == 200
        assert "fluxo editorial completo" in version1.json()["summary"]
        assert "Resumo v2" in version2.json()["summary"]

        conflict_payload = {
            **draft_payload,
            "entity_id": entity_id,
            "base_version": 1,
            "reason": "Teste de conflito por base_version antigo",
        }
        conflict = http.post(f"{BASE_URL}/api/v1/editorial/drafts", json=conflict_payload, headers=headers, timeout=20)
        assert conflict.status_code == 409