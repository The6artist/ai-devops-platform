
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give each test its own temporary database
    test_database = tmp_path / "test_players.db"

    monkeypatch.setattr(
        main,
        "DATABASE_PATH",
        test_database
    )

    main.initialize_database()

    with TestClient(main.app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_player(client):
    response = client.post(
        "/players",
        json={"username": "Tommy"}
    )

    assert response.status_code == 201
    assert response.json()["username"] == "Tommy"
    assert response.json()["status"] == "online"


def test_get_all_players(client):
    client.post("/players", json={"username": "Tommy"})
    client.post("/players", json={"username": "Lance"})

    response = client.get("/players")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_player(client):
    created = client.post(
        "/players",
        json={"username": "Tommy"}
    ).json()

    player_id = created["player_id"]

    response = client.get(f"/players/{player_id}")

    assert response.status_code == 200
    assert response.json()["username"] == "Tommy"


def test_update_player_status(client):
    created = client.post(
        "/players",
        json={"username": "Tommy"}
    ).json()

    player_id = created["player_id"]

    response = client.put(
        f"/players/{player_id}",
        json={"status": "offline"}
    )

    assert response.status_code == 200
    assert response.json()["player"]["status"] == "offline"


def test_delete_player(client):
    created = client.post(
        "/players",
        json={"username": "Tommy"}
    ).json()

    player_id = created["player_id"]

    response = client.delete(f"/players/{player_id}")

    assert response.status_code == 200

    get_response = client.get(f"/players/{player_id}")

    assert get_response.status_code == 404


def test_player_not_found(client):
    response = client.get("/players/999")

    assert response.status_code == 404


def test_invalid_player_status(client):
    created = client.post(
        "/players",
        json={"username": "Tommy"}
    ).json()

    player_id = created["player_id"]

    response = client.put(
        f"/players/{player_id}",
        json={"status": "sleeping"}
    )

    assert response.status_code == 422
