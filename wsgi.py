import sys
import os

# Configurar variável de ambiente para indicar que estamos em produção
os.environ['FLASK_ENV'] = 'production'
os.environ['RENDER'] = 'true'

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Adicionar diretório web ao path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "web"))

# Importar a aplicação Flask
from web.app import app

# Para execução direta deste arquivo
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))