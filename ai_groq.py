from groq import Groq
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ai_analyze_url(url, heuristics_data):

    prompt = f"""
    Você é um analista de segurança.
    Analise a URL e complemente a heurística sem repeti-la.

    URL: {url}

    Heurística:
    {json.dumps(heuristics_data, indent=2)}

    Responda APENAS com JSON:
    {{
        "risco": "baixo" | "medio" | "alto",
        "score": 0-100,
        "motivo": "texto curto"
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "risco": "medio",
            "score": 50,
            "motivo": "JSON inválido pela IA"
        }
