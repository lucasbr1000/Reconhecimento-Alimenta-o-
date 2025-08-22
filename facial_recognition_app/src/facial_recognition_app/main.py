import sys
import os
from flask import Flask

# garante que o Python ache os módulos no mesmo diretório
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# agora importa direto sem o "src."
from models.user import db
from routes import auth, user, facial_recognition

app = Flask(__name__)

# configurações do banco de dados (ajuste se precisar)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# registra as rotas
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(facial_recognition.bp)

@app.route("/")
def index():
    return "Facial Recognition App rodando no Heroku! 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
