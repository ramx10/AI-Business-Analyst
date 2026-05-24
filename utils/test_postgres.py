from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql://postgres:ram123@localhost:5432/postgres"
)

engine = create_engine(DATABASE_URL)

connection = engine.connect()

print("Connected successfully!")

connection.close()