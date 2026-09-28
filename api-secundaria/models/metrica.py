from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Metrica(Base):
    __tablename__ = 'metrica_convidados'

    id = Column(Integer, primary_key=True)
    convidado_id = Column(Integer, unique=True, nullable=False) # <-- Nova coluna
    qtd_adultos = Column(Integer, default=0)
    qtd_criancas = Column(Integer, default=0)
    data_registo = Column(DateTime, default=func.now())

    def __init__(self, convidado_id: int, qtd_adultos: int, qtd_criancas: int):
        self.convidado_id = convidado_id
        self.qtd_adultos = qtd_adultos
        self.qtd_criancas = qtd_criancas