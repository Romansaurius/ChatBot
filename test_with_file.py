import requests

url = "https://chatbot-vffi.onrender.com/chat"
data = {
    "human_query": "cuantos registros hay",
    "file_info": {
        "name": "test.csv",
        "content": {
            "headers": ["id", "name", "email"],
            "data": [
                {"id": "1", "name": "Juan", "email": "juan@test.com"},
                {"id": "2", "name": "Maria", "email": "maria@test.com"}
            ],
            "total_rows": 2
        },
        "size": 1024
    }
}

try:
    response = requests.post(url, json=data, timeout=30)
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)