from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging

LOG_FILE = os.getenv('LOG_FILE', 'py_log.log')
logging.basicConfig(filename=LOG_FILE, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DB_URL = os.getenv('DB_URL', 'sqlite:///movies.db')
engine = create_engine(DB_URL)
Base = declarative_base()
class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    tags = relationship('Tag', secondary='film_tags', back_populates='films')

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    films = relationship('Film', secondary='film_tags', back_populates='tags')

class FilmTag(Base):
    __tablename__ = "film_tags"

    film_id = Column(Integer, ForeignKey('films.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

Base.metadata.create_all(engine)

# Подключаемся к сайту
site = os.getenv('site', 'https://www.kinoafisha.info/rating/movies/')
logging.info(f'Sending request to the site {site}...')
response = requests.get(site)
soup = BeautifulSoup(response.text, 'html.parser')
logging.info('Received response from the site.')

# Парсим ссылки на все страницы, включая изначальную
pages = soup.find_all('a', {'class': 'bricks_item'})[4:14]

mv_links = []
for page_url in pages:
    page_response = requests.get(page_url['href'])
    soup = BeautifulSoup(page_response.text, 'html.parser')
    #  Добываем ссылки на фильмы по ссылке страницы
    movies_tags = soup.find_all('a', {'class': 'movieItem_title'})
    links_movies = [tag['href'] for tag in movies_tags]
    mv_links.extend(links_movies)

session = Session(bind=engine)
tag_set = set()

for i, url_m in enumerate(mv_links):
    mv_response = requests.get(url_m)
    soup = BeautifulSoup(mv_response.text, 'html.parser')

    #  Добываем данные фильма
    title = soup.find('h1', {'class': "trailer_title"}).get_text()[:-6]
    year = int(soup.find('span', {'class': "trailer_year"}).get_text()[:4])
    rating = float(soup.find('span', {'class': "rating_num"}).get_text())
    film_i = Film(title= title, year= year, rating= rating)

    # Добавление всех тегов на странице фильма
    cur_tags = soup.find_all('span', {'class': "filmInfo_genreItem button-main"})
    # Достаем название тега и сразу создаем экземпляр класса
    tags_name = list(map(lambda x: x.get_text(), cur_tags))
    tags_f_i = list(map(lambda x: Tag(name=x), tags_name))

    # Добавляем фильм и тег
    logging.info(f'Inserting film "{title}"({url_m}) into the database...')
    session.add(film_i)
    logging.info('Film inserted into the database.')
    for tag in tags_f_i:
        # Проверяем не был ли занесен тег ранее
        if tag.name not in tag_set:
            logging.info(f'Inserting tag "{tag.name}" into the database...')
            session.add(tag)
            tag_set.update([tag.name])
            logging.info('Tag inserted into the database.')
        # Связываем фильм с его тегами (добавление в таблицу film_tags)
        film_i.tags = [tag]
    session.commit()

# Запрос к базе данных для среднего рейтинга фильмов с тегом по годам
logging.info('Executing query...')
query = """
SELECT t.name AS tag_name, 
       f.year AS release_year, 
       AVG(f.rating) AS average_rating
FROM tags t
JOIN film_tags ft ON t.id = ft.tag_id
JOIN films f ON f.id = ft.film_id
GROUP BY t.name, f.year
"""
df = pd.read_sql_query(query, engine)
logging.info('Query executed.')

# Построение графиков изменения среднего рейтинга фильмов с определенным тегом по годам
for t_name in df['tag_name'].unique():
    t_data = df[df['tag_name'] == t_name]
    plt.plot(t_data['release_year'], t_data['average_rating'])
    plt.title(t_name)
    plt.xlabel('Дата')
    plt.ylabel('Средний рейтинг')
    plt.show()

session.close()
logging.info('Connection to the database closed.')