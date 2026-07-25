import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("La variable DATABASE_URL no esta definida.")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")