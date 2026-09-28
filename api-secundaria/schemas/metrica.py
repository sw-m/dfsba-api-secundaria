from pydantic import BaseModel

class MetricaEntradaSchema(BaseModel):
    convidado_id: int = 1 
    qtd_adultos: int = 2
    qtd_criancas: int = 1

class MetricaPathSchema(BaseModel):
    """ Schema para receber o ID do convidado na URL (Path) para o DELETE """
    convidado_id: int = 1

class ResumoFestaSchema(BaseModel):
    """ Estrutura do dashboard de estimativas para a festa """
    total_adultos: int = 20
    total_criancas: int = 10
    total_convidados: int = 30
    estimativa_salgados: int = 320
    estimativa_doces: int = 160
    litros_refrigerante: float = 16.0
    
class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro será representada
    """
    mesage: str