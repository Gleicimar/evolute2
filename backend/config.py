import  os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY","minha chave secreta")
    MONGO_URI = os.getenv("MONGO_URI")

    if not MONGO_URI:
        raise ValueError("Variável Mongo não foi definida")
    print("Banco conectado")
    