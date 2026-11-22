import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

usuario = os.getenv("MYSQL_USER")
password = quote_plus(os.getenv("MYSQL_PASSWORD"))
host = os.getenv("MYSQL_HOST")
base_datos = os.getenv("MYSQL_DATABASE")


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False