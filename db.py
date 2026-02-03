from sqlalchemy import create_engine

URL_DB = "postgresql://postgres:12345678@localhost:5432/parking"

engine = create_engine(URL_DB)
