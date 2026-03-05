from app.core.models import Solicitacao, Status
from app.core.services import add_solicitacao, compute_metrics


def test_add_solicitacao():
    items = []
    nova = Solicitacao(id=1, titulo="Teste", status=Status.NOVA)
    result = add_solicitacao(items, nova)
    assert len(result) == 1
    assert result[0].titulo == "Teste"


def test_compute_metrics():
    items = [
        Solicitacao(id=1, titulo="A", status=Status.NOVA),
        Solicitacao(id=2, titulo="B", status=Status.EM_ANDAMENTO),
        Solicitacao(id=3, titulo="C", status=Status.CONCLUIDA),
        Solicitacao(id=4, titulo="D", status=Status.CONCLUIDA),
    ]
    metrics = compute_metrics(items)
    assert metrics["total"] == 4
    assert metrics["em_andamento"] == 1
    assert metrics["concluidas"] == 2

