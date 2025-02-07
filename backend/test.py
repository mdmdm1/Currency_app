import requests

response = requests.get("http://127.0.0.1:8000/clients")
if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.json())
