import os
import requests
from django.conf import settings
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
model = getattr(settings, 'IA_MODEL')

print(f'Testing model: {model}')

if api_key:
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'Say hello in Portuguese'}],
            'max_tokens': 100,
        }
        print('Attempting request to OpenRouter...')
        resp = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=data, timeout=10)
        print(f'Status: {resp.status_code}')
        if resp.status_code == 200:
            result = resp.json()
            msg = result['choices'][0]['message']['content']
            print(f'Success! Response: {msg[:100]}')
        else:
            print(f'Error Response: {resp.text[:500]}')
    except Exception as e:
        print(f'Exception: {type(e).__name__}: {str(e)}')
