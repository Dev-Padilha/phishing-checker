"""
app.py
---------
Aplicação principal da API PhishingChecker.
Compatível com Flask 3.x + Railway.
"""

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from checker import analisar_url
from ai_groq import ai_analyze_url
from models import db, LinkCheck
import os

# ---------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------

app = Flask(__name__, static_folder="static")

# ---------------------------------------------------------------
# Banco no diretório persistente do Railway
# ---------------------------------------------------------------

DB_PATH = "/data/database.db"
os.makedirs("/data", exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Criar tabelas assim que o app carrega (Flask 3 safe)
with app.app_context():
    db.create_all()

# ---------------------------------------------------------------
# Classificação final
# ---------------------------------------------------------------

def classify(score):
    if score >= 70:
        return "ALTO"
    elif score >= 40:
        return "MÉDIO"
    return "BAIXO"

# ---------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ---------------------------------------------------------------
# API principal
# ---------------------------------------------------------------

@app.route("/api/check", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")

    # Heurística local
    heur = analisar_url(url)

    # IA Groq
    ia = ai_analyze_url(url, heur)

    # Score híbrido
    score_final = round((heur["score"] * 0.6) + (ia["score"] * 0.4), 2)
    classificacao = classify(score_final)

    resultado_final = {
        "url": url,
        "heuristica": heur,
        "ia": ia,
        "score_final": score_final,
        "classificacao": classificacao,
        "dataVerificacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    # Salvar no banco
    registro = LinkCheck(
        url=url,
        score=score_final,
        nivel_risco=classificacao,
        motivos="; ".join(heur["motivos"]) + f" | IA: {ia['motivo']}",
        created_at=datetime.now()
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify(resultado_final)

# ---------------------------------------------------------------
# Histórico
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
# Execução local
# ---------------------------------------------------------------

if __name__ == "__main__":
    print("Rodando localmente em http://127.0.0.1:8080")
    app.run(port=8080, debug=True)
