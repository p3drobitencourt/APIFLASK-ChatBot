from flask import Flask, jsonify, request
import os
import psycopg2
from dotenv import load_dotenv
import google.generativeai as generativeai
from flask_cors import CORS
from geminiFunctions import melhorarResposta

load_dotenv()
app = Flask(__name__)
# Apply CORS specifically to the correct /api endpoint
CORS(app, resources={r"/api": {"origins": "https://front-api-flask.vercel.app"}})

chave_secreta = os.getenv('GEMINI_API_KEY')
generativeai.configure(api_key=chave_secreta)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def buscar_contexto(consulta):
    result = generativeai.embed_content(
        model='models/gemini-embedding-001',
        content=consulta,
        task_type="retrieval_query"
    )
    embedding = str(result['embedding'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Pega os 3 contextos mais próximos com operador <=>
    cursor.execute(
        "SELECT conteudo FROM documentos ORDER BY embedding <=> %s::vector LIMIT 3",
        (embedding,)
    )
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return " ".join([row[0] for row in resultados]) if resultados else ""

@app.route("/")
def home():
    consulta = "Quem é você ?"
    contexto = buscar_contexto(consulta)
    prompt = f"Consulta: {consulta} Contexto: {contexto}"
    response = melhorarResposta(prompt)
    return response

@app.route("/api", methods=["POST"])
def results():
    data = request.get_json(force=True)
    consulta = data.get("consulta", "")
    
    contexto = buscar_contexto(consulta)
    prompt = f"Consulta: {consulta} Contexto: {contexto}"
    
    response = melhorarResposta(prompt)
    return jsonify({"mensagem": response})
