import psycopg2
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Configuração da API do OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Chave obtida das variáveis de ambiente

# Configuração do PostgreSQL (substitua pelos valores do Neon)
db_config = {
    "host": os.getenv("DB_HOST"),          # Host do banco de dados
    "database": os.getenv("DB_NAME"),      # Nome do banco
    "user": os.getenv("DB_USER"),          # Usuário
    "password": os.getenv("DB_PASSWORD"),  # Senha
    "port": 5432,  # Porta padrão do PostgreSQL
}

# Inicializa o app Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use 5000 como porta padrão
    app.run(host="0.0.0.0", port=port)

# Inicializa o banco de dados
def init_db():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                command TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")

# Processa o comando recebido
@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '')
    print("Comando recebido:", command)  # Log para depuração

    # Verifica no banco se já existe uma resposta
    response = get_existing_response(command)
    if not response:
        # Gera uma nova resposta com IA
        response = get_ai_response(command)
        save_interaction(command, response)  # Salva a interação no banco

    return jsonify({"response": response})

# Obtém resposta da OpenAI
def get_ai_response(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente útil que responde em português do Brasil."},
                {"role": "user", "content": command},
            ],
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return f"Ocorreu um erro ao obter resposta da IA: {str(e)}"

# Verifica no banco se já existe uma resposta
def get_existing_response(command):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM interactions WHERE command = %s", (command,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Erro ao buscar resposta no banco: {str(e)}")
        return None

# Salva uma interação no banco
def save_interaction(command, response):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interactions (command, response) VALUES (%s, %s)", (command, response))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar interação no banco: {str(e)}")

# Inicializa o app
if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados na primeira execução
    port = int(os.getenv("PORT", 5000))  # Render define a porta na variável PORT
    app.run(host="0.0.0.0", port=port)
