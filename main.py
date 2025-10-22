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

class FileInfo(BaseModel):
    name: str
    content: dict = {}
    size: int = 0

class QueryRequest(BaseModel):
    human_query: str
    file_info: FileInfo = None

class QueryResponse(BaseModel):
    answer: str

def get_file_schema(file_info):
    if not file_info or not file_info.content:
        return {}
    
    content = file_info.content
    if 'headers' in content:
        # CSV file
        return {file_info.name: [{"column": col, "type": "varchar"} for col in content['headers']]}
    elif 'data' in content and content['data']:
        # JSON file
        first_row = content['data'][0] if content['data'] else {}
        return {file_info.name: [{"column": key, "type": "varchar"} for key in first_row.keys()]}
    
    return {}

def execute_query_on_file(sql_query: str, file_info):
    if not file_info or not file_info.content:
        return [{"error": "No hay datos disponibles"}]
    
    content = file_info.content
    data = content.get('data', [])
    
    # Simulación básica de consultas SQL
    if "COUNT" in sql_query.upper():
        return [{"total": content.get('total_rows', len(data))}]
    elif "LIMIT" in sql_query.upper():
        limit = 5  # Mostrar primeras 5 filas
        return data[:limit] if data else []
    elif "SELECT *" in sql_query.upper():
        return data[:10] if data else []  # Primeras 10 filas
    else:
        return data[:5] if data else []  # Por defecto, primeras 5 filas

async def human_to_sql(human_query: str, file_info):
    query_lower = human_query.lower()
    table_name = file_info.name if file_info else "data"
    
    if "cuántos" in query_lower or "cantidad" in query_lower or "count" in query_lower:
        return {"sql_query": f"SELECT COUNT(*) as total FROM {table_name}", "original_query": human_query}
    elif "primeras" in query_lower or "muestra" in query_lower or "ver" in query_lower:
        return {"sql_query": f"SELECT * FROM {table_name} LIMIT 5", "original_query": human_query}
    elif "columnas" in query_lower or "campos" in query_lower:
        return {"sql_query": f"DESCRIBE {table_name}", "original_query": human_query}
    elif "todo" in query_lower or "all" in query_lower:
        return {"sql_query": f"SELECT * FROM {table_name}", "original_query": human_query}
    else:
        return {"sql_query": f"SELECT * FROM {table_name} LIMIT 5", "original_query": human_query}

async def build_answer(result: List[Dict], human_query: str, file_info):
    if not result:
        return "No encontré datos en el archivo."
    
    query_lower = human_query.lower()
    file_name = file_info.name if file_info else "archivo"
    
    if "cuántos" in query_lower or "cantidad" in query_lower:
        total = result[0].get('total', len(result))
        return f"El archivo '{file_name}' contiene {total} registros."
    elif "columnas" in query_lower or "campos" in query_lower:
        if file_info and file_info.content.get('headers'):
            cols = ', '.join(file_info.content['headers'])
            return f"El archivo '{file_name}' tiene estas columnas: {cols}"
        else:
            return f"No pude identificar las columnas del archivo '{file_name}'."
    elif "primeras" in query_lower or "muestra" in query_lower:
        if len(result) > 0:
            sample = "\n".join([str(row) for row in result[:3]])
            return f"Primeras filas de '{file_name}':\n{sample}"
        else:
            return f"No hay datos para mostrar en '{file_name}'."
    else:
        return f"Encontré {len(result)} resultado(s) en '{file_name}'. \nPrimera muestra: {str(result[0]) if result else 'Sin datos'}"

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        # Convertir a SQL
        sql_data = await human_to_sql(request.human_query, request.file_info)
        
        # Ejecutar consulta en el archivo
        result = execute_query_on_file(sql_data["sql_query"], request.file_info)
        
        # Generar respuesta
        answer = await build_answer(result, request.human_query, request.file_info)
        
        return QueryResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)