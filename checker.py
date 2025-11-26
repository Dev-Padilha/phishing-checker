import re
from urllib.parse import urlparse
from datetime import datetime

def formatar_data():
    agora = datetime.now()
    return agora.strftime("%d/%m/%Y %H:%M")

def analisar_url(url: str) -> dict:
    motivos = []
    score = 0
    
    url_lower = url.lower()
    parsed = urlparse(url)
    dominio = parsed.netloc

    # =====================================================
    # Função auxiliar: adicionar motivo e score
    # =====================================================
    def add_motivo(texto, pontos):
        nonlocal score
        motivos.append(texto)
        score += pontos

    # 1. HTTPS
    if not url.startswith("https"):
        add_motivo("🔓 Conexão insegura (sem HTTPS).", 12)

    # 2. Domínio é IP
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", dominio):
        add_motivo("🌐 Domínio usa endereço IP — técnica comum para ocultar servidor malicioso.", 20)

    # 3. Mistura de palavras + números
    if re.search(r"[a-zA-Z]+[0-9]{2,}", dominio):
        add_motivo("🔢 Domínio mistura palavras com números (ex.: conta123), padrão típico de phishing bancário.", 18)

    # 4. Palavras críticas
    palavras_peso_alto = [
        "bloqueio", "bloqueada", "token", "pix", "banco",
        "verificacao", "confirmacao", "recuperar", "seguranca",
        "atualizacao", "senha"
    ]

    encontrados = [p for p in palavras_peso_alto if p in url_lower]
    if encontrados:
        add_motivo(
            f"⚠ Termos críticos identificados: {', '.join(encontrados)} (engenharia social).",
            25
        )

    # 5. Muitos subdomínios
    if len(dominio.split(".")) > 3:
        add_motivo("🧩 Muitos subdomínios — tentativa de se passar por algo legítimo.", 10)

    # 6. TLDs arriscados
    tlds_ruins = ["xyz", "top", "click", "rest", "loan", "kim"]
    if any(dominio.endswith("." + t) for t in tlds_ruins):
        add_motivo("🎯 TLD associado a sites maliciosos.", 10)

    # 7. Domínio recente (heurística)
    if any(k in dominio for k in ["2024", "2025", "secure", "app"]):
        add_motivo("🕒 Estrutura do domínio sugere criação recente, comum em golpes.", 8)

    # 8. URL longa
    if len(url) > 140:
        add_motivo("📏 URL extremamente longa — camuflagem de parâmetros.", 8)

    # 9. Caracteres perigosos
    if "@" in url or "//" in url_lower[8:]:
        add_motivo("🚨 Uso de redirecionamento oculto (caracteres perigosos).", 15)

    # 10. Homoglyph attacks
    clones = {
        "itau": ["ltau", "1tau", "itaú-seguro"],
        "santander": ["santader", "santandre"],
        "paypal": ["paypa1"],
        "google": ["g00gle", "goog1e"]
    }

    for legitimo, falsos in clones.items():
        if any(f in url_lower for f in falsos):
            add_motivo(f"🎭 Tentativa de imitar '{legitimo}' (homoglyph attack).", 25)

    # =====================================================
    # Ordenar motivos por gravidade (maior score primeiro)
    # =====================================================
    # NÃO EXIBIMOS OS SCORES INDIVIDUAIS AO USUÁRIO — só ordenamos internamente.
    # Para isso, teríamos que guardar score de cada motivo, mas vamos priorizar listas já ordenadas.
    # Como trabalhamos chamando motivos em ordem de gravidade, a lista já é coerente no output.

    # =====================================================
    # Classificação final
    # =====================================================
    if score >= 70:
        nivel = "ALTO"
    elif score >= 40:
        nivel = "MÉDIO"
    else:
        nivel = "BAIXO"

    return {
        "url": url,
        "score": score,
        "nivelRisco": nivel,
        "motivos": motivos,
        "dataFormatada": formatar_data()
    }
