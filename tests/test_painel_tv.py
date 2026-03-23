"""
Testes unitários para o módulo Painel TV.
Regras aplicadas: PEP-8, DRY e testes isolados.
"""
import pytest
from unittest.mock import MagicMock

# Como ainda não foi desenvolvido o código (apenas planejado), 
# seguimos com os stubs das funções a serem implementadas validando os turnos.

def mock_get_medicamentos_por_turno():
    return [
        {"id_paciente": 1, "status": "ENVIADO", "turno": "MANHA"},
        {"id_paciente": 2, "status": "PENDENTE", "turno": "TARDE"}
    ]

def filter_medicamentos(dados, status=None, turno=None):
    if status:
        dados = [d for d in dados if d.get("status") == status]
    if turno:
        dados = [d for d in dados if d.get("turno") == turno]
    return dados

def test_filter_medicamentos_por_status():
    dados = mock_get_medicamentos_por_turno()
    resultado = filter_medicamentos(dados, status="PENDENTE")
    assert len(resultado) == 1
    assert resultado[0]["id_paciente"] == 2

def test_filter_medicamentos_por_turno():
    dados = mock_get_medicamentos_por_turno()
    resultado = filter_medicamentos(dados, turno="MANHA")
    assert len(resultado) == 1
    assert resultado[0]["status"] == "ENVIADO"

def test_filter_medicamentos_yagni():
    """Valida que nenhum filtro retorna tudo (YAGNI)."""
    dados = mock_get_medicamentos_por_turno()
    resultado = filter_medicamentos(dados)
    assert len(resultado) == 2
