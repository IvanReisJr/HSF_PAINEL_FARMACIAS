# HSF_PAINEL_FARMACIAS — Contexto do Projeto (Handoff)

Este arquivo consolida o contexto do projeto para que outra IA (ou dev) consiga dar continuidade sem precisar “re-descobrir” decisões, estrutura e problemas já resolvidos.

## Objetivo

Aplicação em **Streamlit** para monitorar demandas e, principalmente, exibir o painel **Farmácia Central**:

- **Grid 1 (Lotes)**: lista lotes pendentes/gerados, com filtros de turno e setor.
- **Grid 2 (Itens)**: detalha os itens do lote selecionado (ou relacionados via agrupamento/prescrição).

Banco de dados: **Oracle**, via biblioteca `oracledb`.

## Estrutura do repositório (alto nível)

- [app.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app.py): entrypoint simples que chama `app.main.render()`.
- [app/main.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/main.py): página principal “Painel de Acompanhamento de Solicitações” + expander de teste Oracle.
- [pages/farmacia_central.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/pages/farmacia_central.py): página do painel Farmácia Central (2 grids).
- [app/db/oracle.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py): conexão Oracle (Thin/Thick), leitura de SQL e execução em DataFrame.
- [app/queries/](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries):
  - [farmacia_central.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central.sql): SQL do Grid 1 (lotes).
  - [farmacia_central_grid2.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central_grid2.sql): SQL do Grid 2 (itens).
  - [UNION.SQL](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/UNION.SQL): referência/origem do SQL de grid 2 (usado para conferência).
  - [turnos.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/turnos.sql): definição de turnos (apoio/debug).
- [debug_performance.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/debug_performance.py), [debug_turnos.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/debug_turnos.py), [debug_turnos_history.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/debug_turnos_history.py): scripts auxiliares para diagnóstico.
- [tests/](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/tests): testes unitários básicos.
- Configuração Streamlit: [.streamlit/config.toml](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/.streamlit/config.toml).

## Como rodar (local)

### Requisitos

- Python 3.11 (recomendado; `pyproject.toml` aponta `py311` em ferramentas).
- Dependências:
  - Produção: [requirements.txt](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/requirements.txt)
  - Desenvolvimento: [requirements-dev.txt](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/requirements-dev.txt)

### Streamlit

Executar o app principal:

```bash
streamlit run app.py
```

Executar diretamente a página Farmácia Central:

```bash
streamlit run pages/farmacia_central.py
```

O servidor costuma operar em `localhost:8000` por padrão (ver [.streamlit/config.toml](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/.streamlit/config.toml)).

### Secrets (Oracle)

É esperado `st.secrets["oracle"]` com:

```toml
[oracle]
user = "USUARIO"
password = "SENHA"
host = "HOST"
port = 1521
service_name = "SERVICE"
```

O carregamento ocorre em [config_from_secrets](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py#L92-L107).

## Conexão Oracle (Thin/Thick) e histórico de problemas

O módulo [oracle.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py) tenta inicializar **Thick Mode** para suportar ambientes onde o Oracle exige verificador antigo (erro típico: `DPY-3015`).

- O caminho esperado do Instant Client fica em:
  - `utils/instantclient-basiclite-windows` (relativo ao root do projeto).
- A inicialização é tentada em [connect](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py#L31-L57) e registra logs no console.
- DSN usa Easy Connect (`host:port/service`) via [build_dsn](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py#L25-L28).

Execução de SQL:

- SQL é carregado de `app/queries/<nome>.sql` por [load_sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py#L67-L77).
- Execução parametrizada em DataFrame por [execute_query_df](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/db/oracle.py#L79-L89).

## Página Farmácia Central (2 grids)

Implementação em [pages/farmacia_central.py](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/pages/farmacia_central.py).

### Comportamento

- Botão **Atualizar Dados** limpa caches (`load_data.clear()` e `load_items.clear()`) e força rerun.
- `load_data()`:
  - Conecta no Oracle
  - Carrega SQL `farmacia_central.sql`
  - Renderiza Grid 1 com seleção de linha (single-row).
- `load_items(nr_lote, nr_prescricao)`:
  - Conecta no Oracle
  - Carrega SQL `farmacia_central_grid2.sql`
  - Executa passando parâmetros `nr_lote` e `nr_prescricao`.
- Seleção:
  - Se o usuário selecionar uma linha no Grid 1, o lote/prescrição daquela linha alimenta o Grid 2.
  - Se não houver seleção, o sistema usa o **primeiro registro** do Grid 1 por padrão.

### Observação (Streamlit width)

Foi tentado usar `width='large'`, mas a versão atual do Streamlit valida `width` apenas como:

- inteiro positivo (pixels), ou
- `'stretch'`, ou
- `'content'`.

Resultado: `StreamlitInvalidWidthError`.

O arquivo foi revertido para a forma estável sem `width='large'`.

## SQLs e regras de negócio

### Grid 1 — Lotes (farmacia_central.sql)

Arquivo: [farmacia_central.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central.sql).

O SQL atual faz:

- Define turnos (1..6) e calcula **turno atual** baseado em `SYSDATE`.
- Constrói janela de tempo para **turno atual + 2 turnos anteriores** em CTEs (`TURNOS_BASE`, `TURNO_ATUAL`, `TURNO_ALVO`, `RANGES`).
- Filtra lotes por:
  - `A.DT_ATEND_LOTE` dentro do range global
  - `EXISTS` para garantir que o horário do item (via `OBTER_HORARIO_ITEM_LOTE`) caia em algum range do(s) turno(s)
  - `A.IE_STATUS_LOTE = 'G'`
  - `M.NR_ATENDIMENTO IS NOT NULL`
  - regras de agrupamento (`NR_LOTE_AGRUPAMENTO` / `IE_AGRUPAMENTO`)
  - exclusões ACM/SN, classif != 6, item não suspenso, material não nulo
  - filtro fixo de setor: `A.CD_SETOR_ATENDIMENTO = 70` (9º Andar)

Campos expostos (principais):

- Datas/horas do lote e limites, status, setor, paciente, convênio, turno/classificação
- `NR_LOTE` (`A.NR_SEQUENCIA`) e `NR_PRESCRICAO` (usados para encadear o Grid 2)

### Grid 2 — Itens (farmacia_central_grid2.sql)

Arquivo: [farmacia_central_grid2.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central_grid2.sql).

Consulta com **3 blocos** via `UNION ALL`:

1) Itens do lote quando `A.NR_SEQUENCIA = :NR_LOTE`
2) Itens do agrupamento quando `A.NR_LOTE_AGRUPAMENTO = :NR_LOTE`
3) Itens por prescrição quando `M.NR_PRESCRICAO = :NR_PRESCRICAO` e **não existe** lote com `:NR_LOTE`

Parâmetros esperados:

- `:NR_LOTE` (inteiro)
- `:NR_PRESCRICAO` (inteiro)

#### Problema resolvido: ORA-00942

O 2º bloco estava usando `PRESCR_MAT_HOR_RECOM`, causando `ORA-00942` (tabela/view inexistente).

- Correção aplicada: trocar para `PRESCR_MAT_HOR`, alinhando com a referência em [UNION.SQL](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/UNION.SQL).

## Linha do tempo (resumo do que foi feito)

1) Estrutura base do projeto Streamlit e layout inicial.
2) Criação de modelos/serviços utilitários (dataclasses; Pydantic removido).
3) Testes unitários básicos com Pytest.
4) Integração Oracle:
   - ajustes para Thin (DSN Easy Connect)
   - habilitação de Thick Mode (Instant Client no `utils/`)
   - funções para carregar SQL e retornar DataFrame.
5) Painel Farmácia Central:
   - Grid 1 com [farmacia_central.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central.sql)
   - Grid 2 com [farmacia_central_grid2.sql](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/app/queries/farmacia_central_grid2.sql)
   - parâmetros `nr_lote` e `nr_prescricao` encadeados do Grid 1 para o Grid 2.
6) Correções recentes:
   - Streamlit: revert de `width='large'` que gerava `StreamlitInvalidWidthError`.
   - Oracle SQL: correção de `ORA-00942` trocando `PRESCR_MAT_HOR_RECOM` → `PRESCR_MAT_HOR` no 2º bloco do grid 2.

## Como validar (dev)

Executar testes:

```bash
pytest
```

Checagens de estilo (conforme ferramentas no [pyproject.toml](file:///c:/IvanReis/Paineis/HSF_PAINEL_FARMACIAS/pyproject.toml)):

```bash
black .
isort .
flake8 .
```

## Pontos de atenção / próximos passos (para continuidade)

- Confirmar se o filtro fixo `A.CD_SETOR_ATENDIMENTO = 70` no Grid 1 deve ser permanente ou parametrizável.
- Se houver necessidade de “grid original + grid 2” com separação visual, usar `width='stretch'` (compatível) ou `use_container_width=True` (dependendo da versão do Streamlit), evitando valores inválidos.
- Se o Grid 2 continuar retornando vazio para lotes específicos, validar:
  - consistência de `NR_LOTE` e `NR_PRESCRICAO` no Grid 1
  - se `AP_LOTE_ITEM.NR_SEQ_MAT_HOR` realmente referencia `PRESCR_MAT_HOR.NR_SEQUENCIA` no ambiente
  - privilégios de acesso do usuário Oracle às views/tabelas usadas nas queries.

