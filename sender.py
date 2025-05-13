import requests
import json

#docker run -p 8000:8000 --name=api_container python-redes-image
url1 = "http://127.0.0.1:8000/Empresa1/form/"

data = {
    "data": "2025-05-09"
}
response = requests.post(url1, data=data)
print(response.json())