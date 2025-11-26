# PhishingChecker – API de Detecção de URLs Maliciosas

Projeto desenvolvido para analisar URLs suspeitas utilizando heurísticas técnicas e Inteligência Artificial (Groq – modelo openai/gpt-oss-20b). A API foi construída em Python com Flask e SQLAlchemy, possui banco de dados SQLite e um frontend simples em HTML/CSS/JavaScript.

## Como funciona
A análise é composta por duas etapas:
- Heurística: regras de segurança como ausência de HTTPS, palavras críticas, TLDs suspeitos, homoglyph, IP como domínio, URL longa, redirecionamentos e inúmeras características típicas de phishing.
- IA Groq: análise semântica e contextual da URL, avaliando engenharia social, urgência, imitação de marca e padrões recentes.

