import models
import datetime


dataBase = models.sessionLocal()

def create_film(film: dict):
    # film {name, year, tags:[a,b,c], rating}
    with dataBase as db:
        insert_f = models.Film(title=film['title'], year=datetime.datetime(film['year'],1,1), rating=film['rating'])
        insert_ts = [models.Tag(name=t) for t in film['tags']]

        db.add(insert_f)
        db.add_all(insert_ts)
        insert_f.tags = insert_ts

        db.commit()
        db.refresh(insert_f)
        for tag in insert_ts:
            db.refresh(tag)


        answer = dict(id=insert_f.id, title=insert_f.title, year= insert_f.year.year, tags=insert_ts, rating=insert_f.rating)
        return answer

def get_film(film_id : int):
    with dataBase as db:
        film = db.query(models.Film).filter(models.Film.id == film_id).first()
        if film:
            return dict(id=film.id, title=film.title, year= film.year.year, tags=[t.name for t in film.tags], rating=film.rating)
        else:
            return None

def get_films():
    with dataBase as db:
        films = db.query(models.Film).all()
        return [dict(id=film.id, title=film.title) for film in films]


def get_films_tag_or_year(tag: str, year: int):

    with dataBase as db:
        tag_id = [t.id for t in db.query(models.Tag ).all() if t.name == tag]
        films = db.query(models.Film).join(models.FilmTag, models.FilmTag.film_id == models.Film.id).filter((models.Film.year == datetime.datetime(year,1,1))|(models.FilmTag.tag_id == tag_id[0])).all()
        if films:
            return [dict(id=film.id, title=film.title, year= film.year.year, tags=[t.name for t in film.tags], rating=film.rating) for film in films]
        else:
            return None


def update_film(film_id: int, new_film: dict):
    new_film['year'] = datetime.datetime(new_film['year'],1,1)
    with dataBase as db:
        query = db.query(models.Film).filter(models.Film.id == film_id)
        for q in query:
            q.title = new_film.get('title', q.title)
            q.year = new_film.get('year', q.year)
            q.rating = new_film.get('rating', q.rating)
            if 'tags' in new_film.keys():
                q.tags = [models.Tag(name=t_str) for t_str in new_film['tags']]
            db.commit()
            return dict(film_id=q.id, title=q.title, year= q.year.year, tags=[t.name for t in q.tags], rating=q.rating)


def delete_film(film_id: int):
    with dataBase as db:
        query = db.query(models.Film).filter(models.Film.id == film_id)
        for q in query:
            answer = dict(id=q.id,
                          title=q.title, year= q.year.year,
                          tags=[t.name for t in q.tags],
                          rating=q.rating)

            db.delete(q)
            db.commit()
            return answer