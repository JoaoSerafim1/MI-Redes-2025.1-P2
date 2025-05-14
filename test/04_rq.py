import requests
import json


destinyAddress = 'localhost'
port = 8025
url = 'http://' + destinyAddress + ':' + str(port) + '/submit1'


payload = {'L': 'a', 'R': 'a', 'N': 'j', 'A': 'o'}

# Using the json parameter
response = requests.post(url, json=payload, timeout=5)

# Check the response
if response.status_code == 200:
    print("Request was successful.")
    print("Response:", response.json())
else:
    print(f"Request failed with status code {response.status_code}.")
    print("Response text:", response.text)