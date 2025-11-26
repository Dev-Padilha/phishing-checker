from groq import Groq
from dotenv import load_dotenv
import json
import os

# Carrega o .env
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ai_analyze_url(url, heuristics_data):

    prompt = f"""
Você é um analista de segurança especializado em detecção de phishing.

Avalie a URL considerando:
- engenharia social
- tentativa de imitar bancos/marcas
- urgência, pressão ou recompensa ao usuário
- estrutura do domínio, subdomínios e parâmetros
- padrões novos que a heurística não identificou
- sinais semânticos suspeitos

NÃO repita motivos já identificados pela heurística.

URL analisada:
{url}

Heurística:
{json.dumps(heuristics_data, indent=2)}

RETORNE SOMENTE um JSON válido no formato:

{{
    "risco": "baixo" | "medio" | "alto",
    "score": 0-100,
    "motivo": "explicação curta e objetiva"
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # ACESSO CORRETO PARA O SDK NOVO
    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "risco": "medio",
            "score": 50,
            "motivo": "A IA retornou formato inválido. Fallback aplicado."
        }
