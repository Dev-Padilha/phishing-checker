from openai import OpenAI
import os
import json

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ai_analyze_url(url, heuristics_data):
    prompt = f"""
Você é um analista de segurança especializado em detecção de phishing.

Avalie a URL a seguir considerando:
- engenharia social
- tentativa de imitar bancos/marcas
- urgência ou pressão ao usuário
- estrutura do domínio, subdomínios e parâmetros
- padrões novos que a heurística não identificou

NÃO repita motivos já identificados pela heurística.

URL:
{url}

Heurística:
{json.dumps(heuristics_data, indent=2)}

Retorne EXCLUSIVAMENTE um JSON válido no formato:

{{
    "risco": "baixo" | "medio" | "alto",
    "score": 0-100,
    "motivo": "explicação curta e objetiva"
}}
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = completion.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "risco": "medio",
            "score": 50,
            "motivo": "Falha ao interpretar JSON retornado pela IA."
        }
