from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import os
import re # <--- Importante: Librería para buscar símbolos (Regex)

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
    password_raw = datos.get('pass') # La recibimos como texto primero para validar

    # --- 1. VALIDACIONES DE TU BOCETO ---
    
    # Regla 1: Extensión mínima de 8 caracteres
    if len(password_raw) < 8:
        return jsonify({"status": "error", "mensaje": "La contraseña debe tener al menos 8 caracteres"})

    # Regla 2: Que contenga caracteres especiales (@, $, !, %, etc.)
    # Esta expresión regular busca si hay al menos un símbolo
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password_raw):
        return jsonify({"status": "error", "mensaje": "La contraseña debe incluir al menos un carácter especial"})

    # --- 2. SI PASA LAS REGLAS, CREAMOS EL HASH ---
    
    password_bytes = password_raw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # --- 3. GUARDAR EN MONGO ---
    
    # Opcional: Verificar si el usuario ya existe antes de crearlo
    if usuarios_col.find_one({"user": user}):
        return jsonify({"status": "error", "mensaje": "El nombre de usuario ya está ocupado"})

    usuarios_col.insert_one({
        "user": user, 
        "pass": hashed_password.decode('utf-8') 
    })
    
    return jsonify({"status": "success", "mensaje": "¡Usuario creado con éxito!"})

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    u = datos.get('user')
    p = datos.get('pass').encode('utf-8')

    user_found = usuarios_col.find_one({"user": u})
    
    if user_found:
        if bcrypt.checkpw(p, user_found['pass'].encode('utf-8')):
            return jsonify({"status": "success", "mensaje": "Acceso permitido"})
    
    return jsonify({"status": "error", "mensaje": "Usuario o contraseña incorrectos"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
