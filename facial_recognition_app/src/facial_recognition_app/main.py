# main.py
import sys
from pathlib import Path

# Adiciona a pasta 'src' ao PYTHONPATH
sys.path.append(str(Path(__file__).parent / "src"))

from flask import Flask
from models.user import db  # agora deve encontrar corretamente

app = Flask(__name__)

# Configuração do banco de dados (exemplo)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return "Aplicação rodando!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
