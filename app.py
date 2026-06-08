from flask import Flask, jsonify, request
import numpy as np
import google.generativeai as generativeai
from google import genai
from google.genai import types
import pickle
from flask_cors import CORS
from dotenv import load_dotenv
import os
from geminiFunctions import gerarBuscarConsulta, melhorarResposta

load_dotenv()
app = Flask(__name__)
 # Initialize CORS for the entire application
# Apply CORS specifically to the correct /api endpoint
CORS(app, resources={r"/api": {"origins": "https://front-api-flask.vercel.app"}})
modelo = 'gemini-3-flash-preview'
modeloEmbeddings = pickle.load(open('datasetEmbeddings.pkl','rb'))
chave_secreta = os.getenv('GEMINI_API_KEY')
generativeai.configure(api_key=chave_secreta)


@app.route("/")
def home():
    consulta = "Quem é você ?"
    resposta = gerarBuscarConsulta(consulta, modeloEmbeddings)
    prompt = f"Consulta: {consulta} Resposta: {resposta}"
    response = melhorarResposta(prompt)
    return response


@app.route("/api", methods=["POST"])
def results():
    data = request.get_json(force=True)
    consulta = data["consulta"]
    resultado = gerarBuscarConsulta(consulta, modeloEmbeddings)
    prompt = f"Consulta: {consulta} Resposta: {resultado}"
    response = melhorarResposta(prompt)
    return jsonify({"mensagem":  response})


