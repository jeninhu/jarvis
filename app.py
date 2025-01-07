import psycopg2
import os
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render define a porta na variável PORT
    app.run(host="0.0.0.0", port=port)


# Configuração da API do OpenAI
openai.api_key = "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"

app = Flask(__name__)

# Configuração do PostgreSQL (substitua pelos valores do Neon)
db_config = {
    "host": "ep-autumn-silence-a51d4n1b.us-east-2.aws.neon.tech",  # Exemplo: neon.db.host.com
    "database": "JarvisDB",  # Exemplo: jarvisdb
    "user": "JarvisDB_owner",  # Exemplo: user123
    "password": "lj37xweXRTdc",  # Exemplo: suaSenha
    "port": 5432,  # Porta padrão do PostgreSQL
}

def init_db():
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

@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.json
    print("Comando recebido:", data)  # Adicione este log
    command = data.get('command', '')
    response = process_jarvis_command(command)
    return jsonify({"response": response})

    # Verificar se o comando já existe no banco
    response = get_existing_response(user_input)
    if not response:
        # Gerar nova resposta com IA
        response = get_ai_response(user_input)
        save_interaction(user_input, response)  # Salvar no banco

    return jsonify({"response": response})

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
        return f"Ocorreu um erro: {str(e)}"

def get_existing_response(command):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM interactions WHERE command = %s", (command,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_interaction(command, response):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO interactions (command, response) VALUES (%s, %s)", (command, response))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # Inicializar o banco de dados na primeira execução
    app.run(debug=True)
