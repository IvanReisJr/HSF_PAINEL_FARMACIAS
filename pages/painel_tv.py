import streamlit as st
import pandas as pd
from app.db import oracle

st.set_page_config(
    page_title="Painel TV",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS para UI limpa focada em TV (Data-Ink ratio)
st.markdown("""
<style>
    /* Ocultar barra superior redimensionável e rodapé do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Puxar todo o layout para o topo, eliminando a "testa" em branco gigante do Streamlit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    .status-enviado {
        padding: 5px; background-color: #1e4620; color: #a1fca8; 
        border-radius: 5px; font-weight: bold; text-align: center;
    }
    .status-pendente {
        padding: 5px; background-color: #5c4109; color: #fce386; 
        border-radius: 5px; font-weight: bold; text-align: center;
    }
    .status-atrasado {
        padding: 5px; background-color: #591616; color: #fc9595; 
        border-radius: 5px; font-weight: bold; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Toggle LGPD
modo_anonimo = st.sidebar.checkbox("Modo Anônimo (LGPD) - Ocultar Nomes", value=False, help="Marque para ocultar os nomes dos pacientes na TV.")

@st.cache_data(ttl=60) # TTL reduz sobrecarga no Oracle
def fetch_lotes_tv():
    cfg = oracle.config_from_secrets()
    if not cfg:
        st.error("Sem configs de Oracle")
        return pd.DataFrame()
    
    try:
        conn = oracle.connect(cfg)
        sql = oracle.load_sql("painel_tv_turno")
        df = oracle.execute_query_df(conn, sql)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro BD: {e}")
        return pd.DataFrame()

# Uso de st.fragment para auto-refresh sem recarregar scripts inteiros (Requer Streamlit >= 1.37)
@st.fragment(run_every="60s")
def render_painel():
    st.markdown("<h1 style='text-align: center;'>📺 Painel de Distribuição de Medicamentos</h1>", unsafe_allow_html=True)
    
    # CSS robusto para alinhar título e valor numérico das métricas perfeitamente ao centro
    st.markdown("""
    <style>
        div[data-testid="stMetricLabel"] { text-align: center !important; justify-content: center !important; }
        div[data-testid="stMetricValue"] { text-align: center !important; justify-content: center !important; }
        div[data-testid="stMetricValue"] > div { text-align: center !important; justify-content: center !important; }
        div[data-testid="stMetric"] { 
            display: flex !important; 
            flex-direction: column !important; 
            align-items: center !important; 
        }
    </style>
    """, unsafe_allow_html=True)
    
    df = fetch_lotes_tv()
    
    if df.empty:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 55px;'>✅ Nenhum lote pendente no turno</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        _, col_centro, _ = st.columns([2, 1, 2])
        with col_centro:
            st.metric("Última Atualização", pd.Timestamp.now().strftime('%H:%M'))
            
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.caption("Auto-refresh a cada 60 segundos.")
        return
        
    # Exibir métricas da carga de trabalho global centralizadas (limitando a largura)
    _, c1, c2, c3, _ = st.columns([1.5, 1, 1, 1, 1.5])
    
    with c1:
        st.metric("Total de Lotes no Turno", len(df))
    with c2:
        # Para simplificar na tela de teste, assumimos Pendentes = todos carregados no Teste
        st.metric("Lotes Pendentes", len(df))
    with c3:
        st.metric("Última Atualização", pd.Timestamp.now().strftime('%H:%M'))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>ACOMPANHAMENTO DE SOLICITAÇÕES</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0; padding-top: 0;'/>", unsafe_allow_html=True)
    
    col_lotes, col_req = st.columns(2)
    
    with col_lotes:
        st.markdown("<h3 style='text-align: center; border-bottom: 2px solid black;'>LOTES</h3>", unsafe_allow_html=True)
        
        if df.empty:
            st.info("Nenhum lote carregado.")
        else:
            df_visual = df.copy()
            
            # Aplicar LGPD
            if modo_anonimo:
                df_visual["PACIENTE"] = df_visual.apply(lambda r: f"Pront: {r.get('NR_ATENDIMENTO', 'N/A')}", axis=1)
            else:
                df_visual["PACIENTE"] = df_visual.apply(lambda r: str(r.get('NM_PACIENTE', 'N/A'))[:25], axis=1)
                
            # Mapear e preparar dados do Grid
            df_lotes = df_visual[["DS_LEITO", "NR_LOTE", "PACIENTE", "HORA_ATEND"]].copy()
            # Limpar NAs para boa visualização
            df_lotes = df_lotes.fillna("N/A")
            df_lotes.columns = ["SETOR", "LOTE", "PACIENTE", "HORARIO"]
            
            # O Streamlit renderiza altura dinamicamente, limitar exibição a 4 linhas
            st.dataframe(
                df_lotes.head(4), 
                use_container_width=True, 
                hide_index=True,
            )
            
    with col_req:
        st.markdown("<h3 style='text-align: center; border-bottom: 2px solid black;'>REQUISIÇÕES</h3>", unsafe_allow_html=True)
        
        # Gerando dados de mock (vazios) para representar a tabela do layout físico
        df_req = pd.DataFrame(columns=["Loca destino", "requisição", "Horario"])
        
        # Inserindo 4 linhas em branco apenas para criar uma tabela equiparada visualmente
        for i in range(4):
            df_req.loc[i] = ["-", "-", "-"]
            
        st.dataframe(
            df_req, 
            use_container_width=True, 
            hide_index=True
        )

    if not df.empty:
        # Busca o primeiro registro para detalhar
        primeiro_lote = df_visual.iloc[0]
        nr_lote = int(primeiro_lote["NR_LOTE"]) if pd.notna(primeiro_lote.get("NR_LOTE")) else 0
        paciente_nome = primeiro_lote["PACIENTE"]
        
        st.markdown("---")
        paciente_label = "" if modo_anonimo else "Paciente: "
        st.markdown(f"### 📦 Cesta de Separação — Lote: **{nr_lote}** | {paciente_label}**{paciente_nome}**")
        
        try:
            cfg = oracle.config_from_secrets()
            if cfg:
                conn = oracle.connect(cfg)
                sql_itens = oracle.load_sql("farmacia_central_grid2")
                df_itens = oracle.execute_query_df(conn, sql_itens, params={"nr_lote": nr_lote, "nr_prescricao": 0})
                conn.close()
                
                if not df_itens.empty:
                    # Mapear exatamente para o layout rascunhado pelo cliente
                    # [Codigo, Medicamento, Total Dispens, Dose UD, Horarios]
                    df_itens_tv = df_itens[["CD_MATERIAL", "DS_MATERIAL", "QT_DISPENSAR", "QT_DOSE", "DS_HORARIO"]].copy()
                    df_itens_tv = df_itens_tv.fillna("N/A")
                    df_itens_tv.columns = ["Codigo", "Medicamento", "Total Dispens", "Dose UD", "Horarios"]
                    
                    st.dataframe(
                        df_itens_tv,
                        use_container_width=True,
                        hide_index=True,
                        height=250
                    )
                else:
                    st.info("Nenhum item encontrado para compor este lote.")
        except Exception as e:
            st.error(f"Erro ao carregar os itens do lote: {e}")

    st.caption("Auto-refresh a cada 60 segundos.")

render_painel()
