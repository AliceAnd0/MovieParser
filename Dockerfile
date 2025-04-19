FROM python:3.9

RUN pip install requests beautifulsoup4 sqlalchemy matplotlib pandas

COPY . /app
WORKDIR /app

CMD ["python", "parser.py"]
