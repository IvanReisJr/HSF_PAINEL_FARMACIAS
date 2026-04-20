import streamlit as st
import pandas as pd
from app.db import oracle

st.set_page_config(
    page_title="(Teste) Farmácia Central",
    page_icon="💊",
    layout="wide"
)

st.title("(TESTE) Farmácia Central - Monitoramento")

@st.cache_data(ttl=300)
def load_data():
    cfg = oracle.config_from_secrets()
    if not cfg:
        st.error("Configuração do banco de dados não encontrada nos secrets.")
        return None
    
    try:
        conn = oracle.connect(cfg)
        sql = oracle.load_sql("test_farmacia_central")
        df = oracle.execute_query_df(conn, sql)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar ou executar a consulta: {e}")
        return None

@st.cache_data(ttl=300)
def load_items(nr_lote, nr_prescricao):
    cfg = oracle.config_from_secrets()
    if not cfg:
        return None
    
    try:
        conn = oracle.connect(cfg)
        sql = oracle.load_sql("farmacia_central_grid2")
        df = oracle.execute_query_df(conn, sql, params={"nr_lote": nr_lote, "nr_prescricao": nr_prescricao})
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar itens: {e}")
        return None

if st.button("Atualizar Dados"):
    load_data.clear()
    load_items.clear()
    st.rerun()

df = load_data()

if df is not None:
    st.write(f"Total de registros: {len(df)}")
    
    # Grid 1 - Lotes
    event = st.dataframe(
        df, 
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="grid_lotes"
    )
    
    # Lógica de Seleção
    selected_lote = None
    
    if len(event.selection["rows"]) > 0:
        # Se houve seleção manual
        idx = event.selection["rows"][0]
        selected_lote = df.iloc[idx]
    elif len(df) > 0:
        # Se não houve seleção, pega o primeiro por padrão (conforme solicitado)
        selected_lote = df.iloc[0]
        
    # Grid 2 - Itens do Lote Selecionado
    if selected_lote is not None:
        nr_lote = int(selected_lote["NR_LOTE"])
        nr_prescricao = int(selected_lote["NR_PRESCRICAO"])
        st.markdown(f"### Itens do Lote: {nr_lote} - Prescrição: {nr_prescricao} - {selected_lote['NM_PACIENTE']}")
        
        df_items = load_items(nr_lote, nr_prescricao)
        
        if df_items is not None and not df_items.empty:
            st.dataframe(
                df_items,
                hide_index=True
            )
        else:
            st.info("Nenhum item encontrado para este lote.")
