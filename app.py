from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# CONEXIÓN A MONGO (Usa tu URL de Railway)
MONGO_URL = "mongodb://mongo:pYkvNafdiRhIxwWkckgLmnYsqmcubklP@maglev.proxy.rlwy.net:38868" 
client = MongoClient(MONGO_URL)
db = client.test
usuarios_col = db.usuarios

@app.route('/registrar', methods=['POST'])
def registrar():
    datos = request.json
    user, pw = datos.get('user'), datos.get('pass')
    usuarios_col.insert_one({"user": user, "pass": pw})
    return jsonify({"status": "success", "mensaje": "Usuario creado"})

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    u, p = datos.get('user'), datos.get('pass')
    user_found = usuarios_col.find_one({"user": u, "pass": p})
    if user_found:
        return jsonify({"status": "success", "mensaje": "Acceso permitido"})
    return jsonify({"status": "error", "mensaje": "Datos incorrectos"})

if __name__ == '__main__':
    # Railway asigna el puerto mediante una variable de entorno
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
