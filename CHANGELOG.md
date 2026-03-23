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

## 0.2.0-draft - Planejamento Painel TV (Em Análise)
- Análise estratégica inserida para o Painel de TV focado na distribuição de medicamentos.
- Planejamento de arquitetura baseada em Clean Code, SOLID e YAGNI.
- Testes preliminares em `tests/test_painel_tv.py`.
- **Ressalva LGPD**: Mantida a visibilidade do nome de pacientes na TV aguardando validação final de risco assumido pelo cliente/parceiro da farmácia.
