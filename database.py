import configparser

from sqlalchemy import create_engine
from urllib.parse import quote_plus


config = configparser.ConfigParser()
config.read("config.ini")

host = config["postgresql"]["host"]
port = config["postgresql"]["port"]
database = config["postgresql"]["database"]
username = config["postgresql"]["username"]
password = config["postgresql"]["password"]

password = quote_plus(password)

engine = create_engine(
    f"postgresql+psycopg://"
    f"{username}:{password}@"
    f"{host}:{port}/{database}"
)