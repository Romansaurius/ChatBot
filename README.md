# DataSnap Chatbot API

API para chatbot que convierte lenguaje natural a consultas SQL para DataSnap.

## Setup Local

1. `pip install -r requirements.txt`
2. Copiar `.env.example` a `.env` y configurar
3. `python main.py`

## Deploy Render

1. Conectar repo a Render
2. Configurar variables de entorno
3. Deploy automático

## Uso

POST `/chat`
```json
{
  "human_query": "¿Cuántos usuarios tengo?"
}
```

Respuesta:
```json
{
  "answer": "Tienes 150 usuarios registrados en DataSnap."
}
```