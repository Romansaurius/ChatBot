import requests
import json

# Test de la API
url = "https://chatbot-vffi.onrender.com/chat"
data = {"human_query": "¿Cuántos usuarios tengo?"}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test del health endpoint
try:
    health = requests.get("https://chatbot-vffi.onrender.com/health", timeout=10)
    print(f"Health Status: {health.status_code}")
    print(f"Health Response: {health.text}")
except Exception as e:
    print(f"Health Error: {e}")