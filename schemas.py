from pydantic import BaseModel

class FilmBase(BaseModel):

    title: str
    year: int
    tags: list
    rating: float

class Film(FilmBase):

    class Config:
        from_attributes = True
