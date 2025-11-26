"""
app.py
---------
Aplicação principal em Flask que replica a API PhishingChecker feita originalmente em Spring Boot.
Gerencia rotas, banco de dados, frontend e unifica análises: heurística + IA Groq.

Autor: Biel GOAT
"""

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from checker import analisar_url
from ai_groq import ai_analyze_url
from models import db, LinkCheck
import os

# ---------------------------------------------------------------
# Inicialização da aplicação Flask
# ---------------------------------------------------------------

app = Flask(__name__, static_folder="static")

# ---------------------------------------------------------------
# Configuração do banco de dados (SQLite local)
# ---------------------------------------------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ---------------------------------------------------------------
# Função de classificação final
# ---------------------------------------------------------------

def classify(score):
    if score >= 70:
        return "ALTO"
    elif score >= 40:
        return "MÉDIO"
    return "BAIXO"

# ---------------------------------------------------------------
# Rota principal (Frontend)
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Carrega o arquivo HTML da pasta static"""
    return send_from_directory("static", "index.html")

# ---------------------------------------------------------------
# Rota de verificação de URL (Heurística + IA)
# ---------------------------------------------------------------

@app.route("/api/check", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")

    # 1) Heurística local
    heur = analisar_url(url)

    # 2) IA Groq complementa
    ia = ai_analyze_url(url, heur)

    # 3) Score híbrido
    score_final = round((heur["score"] * 0.6) + (ia["score"] * 0.4), 2)
    classificacao = classify(score_final)

    # 4) Monta resposta completa
    resultado_final = {
        "url": url,
        "heuristica": heur,
        "ia": ia,
        "score_final": score_final,
        "classificacao": classificacao,
        "dataVerificacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    # 5) Salva no banco
    novo = LinkCheck(
        url=url,
        score=score_final,
        nivel_risco=classificacao,
        motivos="; ".join(heur["motivos"]) + f" | IA: {ia['motivo']}",
        created_at=datetime.now()
    )
    db.session.add(novo)
    db.session.commit()

    return jsonify(resultado_final)

# ---------------------------------------------------------------
# Rota de histórico
# ---------------------------------------------------------------

@app.route("/api/history", methods=["GET"])
def get_history():

    registros = LinkCheck.query.order_by(LinkCheck.created_at.desc()).limit(20).all()

    return jsonify([
        {
            "url": r.url,
            "score": r.score,
            "nivelRisco": r.nivel_risco,
            "motivos": r.motivos,
            "dataVerificacao": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in registros
    ])

# ---------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists("database.db"):
        with app.app_context():
            db.create_all()

    print("Servidor rodando em http://127.0.0.1:8080")
    app.run(port=8080, debug=True)
