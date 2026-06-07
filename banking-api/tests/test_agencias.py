"""Testes CRUD para o endpoint /agencias da Banking API."""

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_list_agencias_returns_200(client):
    """Verifica que GET /agencias retorna status 200.

    Args:
        client: TestClient da aplicação.
    """
    response = client.get("/agencias")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.smoke
def test_create_agencia_returns_201(client, agencia_data):
    """Verifica que POST /agencias cria agência e retorna status 201.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    response = client.post("/agencias", json=agencia_data)
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == agencia_data["codigo"]
    assert data["nome"] == agencia_data["nome"]
    assert "id" in data


@pytest.mark.smoke
def test_get_agencia_by_id_returns_200(client, agencia_data):
    """Verifica que GET /agencias/{id} retorna a agência criada.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    create_resp = client.post("/agencias", json=agencia_data)
    agencia_id = create_resp.json()["id"]
    response = client.get(f"/agencias/{agencia_id}")
    assert response.status_code == 200
    assert response.json()["id"] == agencia_id


@pytest.mark.smoke
def test_delete_agencia_returns_204(client, agencia_data):
    """Verifica que DELETE /agencias/{id} remove e retorna status 204.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    create_resp = client.post("/agencias", json=agencia_data)
    agencia_id = create_resp.json()["id"]
    response = client.delete(f"/agencias/{agencia_id}")
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_update_agencia_returns_200(client, agencia_data):
    """Verifica que PUT /agencias/{id} atualiza os campos corretamente.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    create_resp = client.post("/agencias", json=agencia_data)
    agencia_id = create_resp.json()["id"]
    update_data = {"nome": "Agência Atualizada", "telefone": "11888888888"}
    response = client.put(f"/agencias/{agencia_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["nome"] == "Agência Atualizada"
    assert response.json()["telefone"] == "11888888888"


@pytest.mark.regression
def test_create_agencia_duplicate_codigo_returns_409(client, agencia_data):
    """Verifica que POST com código duplicado retorna status 409.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    client.post("/agencias", json=agencia_data)
    response = client.post("/agencias", json=agencia_data)
    assert response.status_code == 409


@pytest.mark.regression
def test_get_agencia_not_found_returns_404(client):
    """Verifica que GET /agencias/{id} com ID inexistente retorna 404.

    Args:
        client: TestClient da aplicação.
    """
    response = client.get("/agencias/99999")
    assert response.status_code == 404


@pytest.mark.regression
def test_delete_agencia_not_found_returns_404(client):
    """Verifica que DELETE /agencias/{id} com ID inexistente retorna 404.

    Args:
        client: TestClient da aplicação.
    """
    response = client.delete("/agencias/99999")
    assert response.status_code == 404


@pytest.mark.regression
def test_update_agencia_not_found_returns_404(client):
    """Verifica que PUT /agencias/{id} com ID inexistente retorna 404.

    Args:
        client: TestClient da aplicação.
    """
    response = client.put("/agencias/99999", json={"nome": "Teste"})
    assert response.status_code == 404


@pytest.mark.regression
def test_list_agencias_returns_multiple(client, agencia_data):
    """Verifica que GET /agencias retorna lista com múltiplas agências.

    Args:
        client: TestClient da aplicação.
        agencia_data: Dados de exemplo para criação de agência.
    """
    agencia2 = {**agencia_data, "codigo": "AG002", "nome": "Agência Secundária"}
    client.post("/agencias", json=agencia_data)
    client.post("/agencias", json=agencia2)
    response = client.get("/agencias")
    assert response.status_code == 200
    assert len(response.json()) >= 2
