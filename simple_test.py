import requests

url = "https://chatbot-vffi.onrender.com/chat"
data = {"human_query": "cuantos usuarios tengo"}

response = requests.post(url, json=data)
print("Status:", response.status_code)
if response.status_code == 200:
    print("Success! API working")
    print("Answer:", response.json().get('answer', 'No answer'))
else:
    print("Error:", response.text)