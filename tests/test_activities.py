from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_filters_by_search_term():
    response = client.get("/activities", params={"search": "software"})

    assert response.status_code == 200
    assert list(response.json()) == ["Programming Class"]


def test_get_activities_filters_by_schedule_case_insensitively():
    response = client.get("/activities", params={"schedule": "FRIDAYS"})

    assert response.status_code == 200
    assert list(response.json()) == ["Chess Club", "Gym Class"]


def test_get_activities_combines_search_and_schedule_filters():
    response = client.get(
        "/activities",
        params={"search": "class", "schedule": "thursdays"},
    )

    assert response.status_code == 200
    assert list(response.json()) == ["Programming Class"]
