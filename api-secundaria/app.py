from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from models import Session
from models.metrica import Metrica
from schemas.metrica import MetricaEntradaSchema, MetricaPathSchema, ResumoFestaSchema, ErrorSchema

# Configuração do OpenAPI (Swagger)
info = Info(title="API Secundária - Métricas da Festa", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# Definição das Tags
metricas_tag = Tag(name="Métricas", description="recepção de dados")

@app.route('/')
def home():
    """Redireciona para a tela inicial do Swagger."""
    return redirect('/openapi/swagger')

@app.post('/metricas', tags=[metricas_tag], responses={"200": MetricaEntradaSchema, "400": ErrorSchema, "409": ErrorSchema})
def registar_presencas(body: MetricaEntradaSchema):
    """Recebe a quantidade de pessoas de um novo convite confirmado e guarda na base de dados."""
    try:
        session = Session()
        nova_metrica = Metrica(
            convidado_id=body.convidado_id, 
            qtd_adultos=body.qtd_adultos, 
            qtd_criancas=body.qtd_criancas
        )
        session.add(nova_metrica)
        session.commit()
        return {"message": "Métricas registradas com sucesso"}, 200
    except IntegrityError:
        return {"message": "Já existe uma métrica registada para este convidado_id"}, 409
    except Exception as e:
        return {"message": "Erro ao guardar as métricas", "detalhes": str(e)}, 400

@app.put('/metricas', tags=[metricas_tag], responses={"200": MetricaEntradaSchema, "404": ErrorSchema, "400": ErrorSchema})
def atualizar_presencas(body: MetricaEntradaSchema):
    """Atualiza a quantidade de adultos e crianças para um convidado existente."""
    session = Session()
    metrica = session.query(Metrica).filter(Metrica.convidado_id == body.convidado_id).first()
    
    if not metrica:
        return {"message": "Métrica não encontrada para este convidado"}, 404
        
    try:
        metrica.qtd_adultos = body.qtd_adultos
        metrica.qtd_criancas = body.qtd_criancas
        session.commit()
        return {"message": "Métricas atualizadas com sucesso"}, 200
    except Exception as e:
        return {"message": "Erro ao atualizar as métricas", "detalhes": str(e)}, 400

@app.delete('/metricas/<int:convidado_id>', tags=[metricas_tag], responses={"200": ErrorSchema, "404": ErrorSchema, "400": ErrorSchema})
def remover_presencas(path: MetricaPathSchema):
    """Remove as métricas associadas a um convidado deletado na API Principal."""
    session = Session()
    metrica = session.query(Metrica).filter(Metrica.convidado_id == path.convidado_id).first()
    
    if metrica:
        try:
            session.delete(metrica)
            session.commit()
            return {"message": "Métricas do convidado removidas com sucesso"}, 200
        except Exception as e:
            return {"message": "Erro ao remover as métricas", "detalhes": str(e)}, 400
    
    return {"message": "Métrica não encontrada na base de dados"}, 404

@app.get('/metricas/resumo', tags=[metricas_tag], responses={"200": ResumoFestaSchema})
def obter_resumo():
    """Calcula o total de convidados e a estimativa de compras para o evento."""
    session = Session()
    
    # Soma todos os adultos e crianças registados
    total_adultos = session.query(func.sum(Metrica.qtd_adultos)).scalar() or 0
    total_criancas = session.query(func.sum(Metrica.qtd_criancas)).scalar() or 0
    
    # Regras de Negócio do Evento
    # Adulto: 12 salgados, 6 doces, 600ml de bebida
    # Criança: 8 salgados, 4 doces, 400ml de bebida
    salgados = (total_adultos * 12) + (total_criancas * 8)
    doces = (total_adultos * 6) + (total_criancas * 4)
    bebidas = (total_adultos * 0.6) + (total_criancas * 0.4)
    
    return {
        "total_adultos": total_adultos,
        "total_criancas": total_criancas,
        "total_convidados": total_adultos + total_criancas,
        "estimativa_salgados": salgados,
        "estimativa_doces": doces,
        "litros_refrigerante": round(bebidas, 2)
    }, 200