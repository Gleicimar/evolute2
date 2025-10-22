import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS

MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
  raise ValueError("Variável MONGO_URI não está definida")
print("Conectado ao banco com sucesso")


conexao = MongoClient(MONGO_URI)
db = conexao['evolute2']

collect_leads = db['leads']
usuarios = db['usuarios']


fs = GridFS(db)

