import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import google.generativeai as generativeai

load_dotenv()

# Configurações Gemini
chave_secreta = os.getenv('GEMINI_API_KEY')
generativeai.configure(api_key=chave_secreta)

# Conexão com o banco (variáveis de ambiente, sem hardcode)
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

# Lendo o CSV
csv_url = 'https://docs.google.com/spreadsheets/d/11QU1ibjUAlNKLwLWF1s-kSpRH2UBOiVbLyl1pJIyeSk/export?format=csv&id=11QU1ibjUAlNKLwLWF1s-kSpRH2UBOiVbLyl1pJIyeSk'
df = pd.read_csv(csv_url)

model = 'models/gemini-embedding-001'

def gerar_e_salvar(titulo, conteudo):
    result = generativeai.embed_content(
        model=model,
        content=conteudo,
        task_type="retrieval_document",
        title=titulo
    )
    
    # Salva no banco (convertendo a lista pra string pro pgvector entender)
    embedding = str(result['embedding'])
    
    cursor.execute(
        "INSERT INTO documentos (titulo, conteudo, embedding) VALUES (%s, %s, %s)",
        (titulo, conteudo, embedding)
    )

print("Gerando embeddings e salvando no PostgreSQL...")
for index, row in df.iterrows():
    gerar_e_salvar(row['Titulo'], row['Conteúdo'])

conn.commit()
cursor.close()
conn.close()
print("Pronto!")