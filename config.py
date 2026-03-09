import os
from dotenv import load_dotenv

env = os.getenv("APP_ENV", "dev")

if env == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")

DB_HOST = os.getenv("ENCRYPTION_SALT")
DB_USER = os.getenv("ENCRYPTION_IV")

print("DB_HOST: ", DB_HOST)