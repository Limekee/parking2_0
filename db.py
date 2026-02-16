from sqlalchemy import create_engine

#здесь происходит подключение к бд, которое в дальшейшем будет использоваться
#в models.py

URL_DB = "postgresql://postgres:12345678@localhost:5432/parking"

engine = create_engine(URL_DB)
