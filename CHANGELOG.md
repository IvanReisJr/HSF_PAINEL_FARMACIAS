# Changelog

## 0.1.0 - Inicial
- Estrutura base do projeto Streamlit criada.
- Configuração de ambiente, dependências e linters definida.
- Serviços e utilitários mínimos sem SQL.
- Interface inicial do painel.
- Testes unitários básicos com Pytest.

## 0.1.1 - Ajustes de dependências e venv
- Trocado ambiente para pasta venv.
- Reduzido requirements para apenas Streamlit e OracleDB.
- Removido Pydantic; modelos convertidos para dataclasses.
- UI ajustada para não depender explicitamente de pandas.

## 0.1.2 - Correção de import
- Adicionado app.py na raiz para execução via `streamlit run app.py`, evitando erro `No module named 'app'` ao subir o app.

## 0.1.3 - Teste de conexão Oracle
- Adicionado módulo de conexão Oracle com oracledb e função de SELECT 1.
- Incluído expander no painel para testar conexão (campos e botão).
- Leitura opcional de credenciais via st.secrets['oracle'].

## 0.2.0 - Lançamento da Feature: Painel TV (Dispensação)
- Implementada interface `pages/painel_tv.py` de Gestão à Vista orientada para Fila de Pendências.
- Criada a query dedicadada `painel_tv_turno.sql` (exibindo apenas `IE_STATUS_LOTE = G`).
- Modificação de layout para **TV / Tela passiva** (`initial_sidebar_state="collapsed"`, `use_container_width=True`), embutindo atualização via `@st.fragment(run_every="60s")` a fim de desonerar o Oracle no longo prazo.
- Layout de dupla visão nativa (Grid Principal: Fila de lotes pendentes do turno; Grid 2 Inferior Mestre-Detalhe: Automático sobre a Cesta do 1º Lote da Fila utilizando reuso de `farmacia_central_grid2.sql`).
- **Comitê de Privacidade**: Toggle LGPD incluído no sidebar para anonimização instantânea de nomes (`Modo Anônimo`).
- Planejamento de caso documentado.
- Esboço de testes iniciais em `tests/test_painel_tv.py`.
