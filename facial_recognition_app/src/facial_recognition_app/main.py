# main.py
import sys
from pathlib import Path

# Adiciona automaticamente a pasta 'src' ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from flask import Flask
try:
    from models.user import db  # agora deve encontrar corretamente
except ModuleNotFoundError as e:
    print("ERRO: Não encontrou 'models.user'. Verifique a estrutura de pastas.")
    raise e

app = Flask(__name__)

# Configuração mínima do banco de dados (SQLite como exemplo)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(BASE_DIR / "database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy
db.init_app(app)

# Rota de teste
@app.route('/')
def home():
    return "Aplicação rodando!"

# Permite rodar localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
