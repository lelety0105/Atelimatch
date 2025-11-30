import requests
import json

print("Testing the chat API endpoint...")

try:
    response = requests.post(
        'http://127.0.0.1:8000/ia/api/chat/',
        json={'message': 'Olá, qual é uma boa ideia para um ateliê de costura?'},
        timeout=30
    )
    
    print(f'Status: {response.status_code}')
    print(f'Response: {response.json()}')
    
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
