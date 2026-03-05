from collections import Counter
from typing import Iterable, List

from app.core.models import Solicitacao, Status


def add_solicitacao(items: List[Solicitacao], nova: Solicitacao) -> List[Solicitacao]:
    items.append(nova)
    return items


def compute_metrics(items: Iterable[Solicitacao]) -> dict:
    items_list = list(items)
    c = Counter([i.status for i in items_list])
    return {
        "total": len(items_list),
        "em_andamento": c.get(Status.EM_ANDAMENTO, 0),
        "concluidas": c.get(Status.CONCLUIDA, 0),
    }


def get_sample_data() -> List[Solicitacao]:
    return [
        Solicitacao(id=1, titulo="Onboarding usuário", status=Status.EM_ANDAMENTO),
        Solicitacao(id=2, titulo="Ajustar layout", status=Status.NOVA),
        Solicitacao(id=3, titulo="Publicar versão", status=Status.CONCLUIDA),
    ]
