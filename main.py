import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import mysql.connector
from typing import List, Dict, Any

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    human_query: str

class QueryResponse(BaseModel):
    answer: str

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        schema[table] = [{"column": col[0], "type": col[1]} for col in columns]
    
    conn.close()
    return schema

def execute_query(sql_query: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql_query)
    result = cursor.fetchall()
    conn.close()
    return result

async def human_to_sql(human_query: str):
    schema = get_schema()
    
    prompt = f"""
Esquema de DataSnap:
{json.dumps(schema, indent=2)}

Convierte esta pregunta a SQL: {human_query}

Responde SOLO con JSON válido:
{{"sql_query": "SELECT ...", "original_query": "{human_query}"}}
"""
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer gsk_free_token_datasnap_2024"},
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        },
        timeout=30
    )
    
    if response.status_code != 200:
        # Fallback simple si falla
        return {"sql_query": "SELECT COUNT(*) as total FROM users", "original_query": human_query}
    
    content = response.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except:
        return {"sql_query": "SELECT COUNT(*) as total FROM users", "original_query": human_query}

async def build_answer(result: List[Dict], human_query: str):
    prompt = f"""
Pregunta: {human_query}
Datos de DataSnap: {json.dumps(result, indent=2)}

Responde en español de forma clara y concisa basándote en los datos.
"""
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer gsk_free_token_datasnap_2024"},
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        },
        timeout=30
    )
    
    if response.status_code != 200:
        # Fallback simple
        count = len(result) if isinstance(result, list) else 1
        return f"Encontré {count} resultado(s) para tu consulta sobre DataSnap."
    
    return response.json()["choices"][0]["message"]["content"]

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        # Convertir a SQL
        sql_data = await human_to_sql(request.human_query)
        
        # Ejecutar consulta
        result = execute_query(sql_data["sql_query"])
        
        # Generar respuesta
        answer = await build_answer(result, request.human_query)
        
        return QueryResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)