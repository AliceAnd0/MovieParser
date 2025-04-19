from fastapi.testclient import TestClient
from route import app
import models

client = TestClient(app)


models.create_db()

def test_create_film():
    film_data = {"title": 'title', 'year': 2024,'tags': ['A', 'B', 'C'], 'rating': 10}
    response = client.post("/film/", json=film_data)
    assert response.status_code == 200
    assert response.json()["title"] == film_data["title"]
    return response.json()

def test_get_film():
    film_id = 1
    response = client.get(f"/film/{film_id}")
    assert response.status_code == 200
    return response.json()

def test_get_film_tag_or_year():
    tag_name = 'A'
    year = 2024
    response = client.get(f"/film/?year={year}&tag={tag_name}")
    assert response.status_code == 200
    return response.json()

def test_update_film():
    film_id = 1
    updated_film_data = {"title": 'title', 'year': 2024,'tags': ['A', 'B', 'C'], 'rating': 9}
    response = client.put(f"/film/{film_id}", json=updated_film_data)
    assert response.status_code == 200
    return response.json()


def test_delete_film():
    film_id = 1

    response = client.delete(f"/film/{film_id}")
    assert response.status_code == 200
    assert response.json()["id"] == film_id
    return response.json()

print('create film\n', test_create_film())
print('get film by id\n', test_get_film())
print('update film\n', test_update_film())
print('get film by id\n', test_get_film())
print('films with genre "A" or which were realesed in 2024\n', test_get_film_tag_or_year())
print('delete this film by id\n', test_delete_film())