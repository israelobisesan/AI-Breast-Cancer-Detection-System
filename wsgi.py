import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ['GEMINI_API_KEY'] = 'AIzaSyAYjPFUyZAyGVafyniPWqaw20PCUeDgrDQ'
os.environ['FLASK_SECRET_KEY'] = 'my-breast-cancer-app-secret-2026'

from app import app as application

if __name__ == '__main__':
    application.run()
