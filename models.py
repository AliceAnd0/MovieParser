from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DATE
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from databaseV import DB_URL


engine = create_engine(DB_URL, echo=False, connect_args={'check_same_thread': False})
sessionLocal = sessionmaker(engine)
Base = declarative_base()


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    year = Column(DATE)
    rating = Column(Float)
    tags = relationship('Tag', secondary='film_tags', back_populates='films')

    def __repr__(self):
        return f"title={self.title}, year={self.year}, rating={self.rating}"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    films = relationship('Film', secondary='film_tags', back_populates='tags')

    def __repr__(self):
        return f"name={self.name}"


class FilmTag(Base):
    __tablename__ = "film_tags"

    film_id = Column(Integer, ForeignKey('films.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

    def __repr__(self):
        return f"film_id={self.film_id}, tag_id={self.tag_id}"


def create_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)