from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class Status(StrEnum):
    NOVA = "Nova"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"


class Prioridade(StrEnum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"


@dataclass(slots=True)
class Solicitacao:
    id: int
    titulo: str
    status: Status = Status.NOVA
    prioridade: Prioridade = Prioridade.MEDIA
    criado_em: datetime = field(default_factory=lambda: datetime.now(UTC))
