CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    titulo TEXT,
    conteudo TEXT,
    embedding vector(768)
);

-- Índice para acelerar a busca KNN (K-Nearest Neighbors) com distância cosseno
CREATE INDEX ON documentos USING hnsw (embedding vector_cosine_ops);
