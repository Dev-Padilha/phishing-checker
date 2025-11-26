"""
models.py
----------
Camada de persistência do sistema.
Define a estrutura da tabela 'link_check' no banco de dados SQLite.

Autor: Biel GOAT
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LinkCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    score = db.Column(db.Integer)
    nivel_risco = db.Column(db.String(50))
    motivos = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)


