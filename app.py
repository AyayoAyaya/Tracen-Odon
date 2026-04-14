from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt # <--- Nueva librería
import os

app = Flask(__name__)
CORS(app)

MONGO_URL = "mongodb://mongo:pYkvNafdiRhIxwWkckgLmnYsqmcubklP@maglev.proxy.rlwy.net:38868" 
client = MongoClient(MONGO_URL)
db = client.test
usuarios_col = db.usuarios

@app.route('/registrar', methods=['POST'])
def registrar():
    datos = request.json
    user = datos.get('user')
    password = datos.get('pass').encode('utf-8') # Convertir a bytes

    # --- AQUÍ OCURRE LA MAGIA DEL HASH ---
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    # Guardamos el usuario con la clave ENCRIPTADA
    usuarios_col.insert_one({
        "user": user, 
        "pass": hashed_password.decode('utf-8') 
    })
    
    return jsonify({"status": "success", "mensaje": "Usuario creado con seguridad"})

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    u = datos.get('user')
    p = datos.get('pass').encode('utf-8')

    user_found = usuarios_col.find_one({"user": u})
    
    if user_found:
        # Comparamos la clave que puso el usuario con el HASH de la base de datos
        if bcrypt.checkpw(p, user_found['pass'].encode('utf-8')):
            return jsonify({"status": "success", "mensaje": "Acceso permitido"})
    
    return jsonify({"status": "error", "mensaje": "Datos incorrectos"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
