from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas

app = FastAPI()

models.Base.metadata.create_all(bind=models.engine)
database = Session(models.engine)


# Создание фильма
@app.post('/film/')
def create_film(film: schemas.Film):
    return crud.create_film(film=dict(film))

# Получение фильма по id
@app.get('/film/{film_id}')
def get_film(film_id: int):
    return crud.get_film(film_id=film_id)

# Получение всех фильмов по году или жанру
@app.get("/film/")
def get_films_tag_or_year(tag: str, year: int):
    return crud.get_films_tag_or_year(tag=tag, year=year)

# Изменение данных о фильме
@app.put('/film/{film_id}')
def update_film(film_id : int, new_film: schemas.Film):
    return crud.update_film(film_id=film_id, new_film=dict(new_film))

# Удаление фильма
@app.delete('/film/{film_id}')
def delete_film(film_id: int, ):
    if film_id > len(crud.get_films()) or film_id <= 0:
        raise HTTPException(status_code=404, detail="Theme not found")

    return crud.delete_film(film_id=film_id)