import sys
import os

# Adiciona o diretório raiz ao sys.path para permitir importações absolutas como 'from app.core...'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import asdict
import streamlit as st
from app.core.services import compute_metrics, get_sample_data
from app.db.oracle import OracleConfig, config_from_secrets, connect, select_one_dual


def render_header():
    st.set_page_config(page_title="Painel de Solicitações", layout="wide")
    st.title("Painel de Acompanhamento de Solicitações")


def render():
    render_header()
    data = get_sample_data()
    rows = [asdict(d) for d in data]

    col1, col2, col3 = st.columns(3)
    metrics = compute_metrics(data)
    col1.metric("Total", metrics["total"])
    col2.metric("Em Andamento", metrics["em_andamento"])
    col3.metric("Concluídas", metrics["concluidas"])

    st.subheader("Solicitações")
    st.dataframe(rows)

    with st.expander("Teste de conexão Oracle"):
        defaults = config_from_secrets()
        c1, c2, c3 = st.columns(3)
        user = c1.text_input("Usuário", value=defaults.user if defaults else "")
        password = c2.text_input("Senha", type="password", value=defaults.password if defaults else "")
        host = c3.text_input("Host", value=defaults.host if defaults else "")
        c4, c5 = st.columns(2)
        port = c4.number_input("Porta", min_value=1, max_value=65535, value=defaults.port if defaults else 1521)
        service = c5.text_input("Service Name", value=defaults.service_name if defaults else "XE")
        if st.button("Testar conexão e SELECT 1"):
            if not all([user, password, host, service]):
                st.warning("Preencha usuário, senha, host e service name.")
            else:
                cfg = OracleConfig(user=user, password=password, host=host, port=int(port), service_name=service)
                try:
                    with st.spinner("Conectando ao Oracle..."):
                        conn = connect(cfg)
                        try:
                            result = select_one_dual(conn)
                        finally:
                            conn.close()
                    st.success(f"Conexão OK. Retorno do SELECT 1 FROM DUAL: {result}")
                except Exception as e:  # pragma: no cover
                    st.error(f"Falha na conexão/consulta: {e}")

if __name__ == "__main__":
    render()
