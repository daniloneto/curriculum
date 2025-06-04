import os
import sys

# Configurar variável de ambiente para indicar que estamos em produção
os.environ["FLASK_ENV"] = "production"
os.environ["RENDER"] = "true"

# Adicionar diretório raiz e pasta web ao path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "web"))

from web.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
