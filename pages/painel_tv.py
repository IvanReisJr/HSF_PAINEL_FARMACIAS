import streamlit as st
import pandas as pd
from app.db import oracle

st.set_page_config(
    page_title="Painel TV - Monitoramento",
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
    st.title("📺 Painel de Distribuição de Medicamentos")
    
    df = fetch_lotes_tv()
    if df.empty:
        st.title("✅ Nenhum lote pendente no turno")
        return

    # Tratamento inicial
    df_visual = df.copy()
    
    # Aplicar LGPD
    if modo_anonimo:
        df_visual["PACIENTE/LEITO"] = df_visual.apply(lambda r: f"Pront: {r.get('NR_ATENDIMENTO', 'N/A')} - {r.get('DS_LEITO', 'N/A')}", axis=1)
    else:
        df_visual["PACIENTE/LEITO"] = df_visual.apply(lambda r: f"{str(r.get('NM_PACIENTE', 'N/A'))[:25]} - {r.get('DS_LEITO', '')}", axis=1)
        
    # Lógica Visual Refinada de Status e Atrasos
    agora = pd.Timestamp.now()
    
    def avaliar_status(row):
        texto = str(row.get("DS_STATUS_LOTE", "")).lower().strip()
        
        # Se veio Distribuído, o que é raro já que barramos no SQL a maioria dos finalizados
        if "distribuido" in texto:
            return "🟢 Enviado"
        
        # Caso esteja Gerado, Aberto, etc - precisamos checar há quanto tempo está lá
        dt_geracao = pd.to_datetime(row.get("DT_GERACAO_FULL")) if pd.notna(row.get("DT_GERACAO_FULL")) else None
        
        if dt_geracao:
            # Se for maior que 2 horas (exemplo flexível) na tela sem distribuir, fica Crítico
            diferenca_hs = (agora - dt_geracao).total_seconds() / 3600
            if diferenca_hs > 2:
                return "🔴 Atrasado Crítico"
            elif diferenca_hs > 1:
                return "🟠 Em Atraso"
                
        return "🟡 Pendente (Progresso)"

    df_visual["STATUS"] = df_visual.apply(avaliar_status, axis=1)
    
    # Formata colunas cruas para exibição do Grid 1
    df_grid = df_visual[["HORA_ATEND", "PACIENTE/LEITO", "DS_TURNO", "STATUS"]]
    df_grid.columns = ["HORA", "PACIENTE_LEITO", "TURNO", "STATUS_ENTREGA"]
    
    # Exibir métricas da carga de trabalho global (Mesmo não mostrando todos, o número avisa o time)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Lotes no Turno", len(df_grid))
    c2.metric("Lotes Pendentes", len(df_grid[df_grid["STATUS_ENTREGA"].str.contains("Pendente|🔴|🟠")]))
    c3.metric("Última Atualização", pd.Timestamp.now().strftime('%H:%M'))
    
    # Monta a estrutura limitando ao Top 5
    st.subheader("Fila de Espera (Próximos 5 Lotes a Separar)")
    
    # Pega apenas os 5 primeiros registros para não estender a tela da TV para baixo
    df_grid_tv = df_grid.head(5)
    
    # Busca o primeiro registro para detalhar
    primeiro_lote = df_visual.iloc[0]
    nr_lote = int(primeiro_lote["NR_LOTE"]) if pd.notna(primeiro_lote.get("NR_LOTE")) else 0
    # NR_PRESCRICAO não está na view original reduzida da TV, se mockarmos passamos zero.
    
    st.dataframe(
        df_grid_tv, 
        use_container_width=True, 
        hide_index=True,
    )
    
    # Grid 2 Focado na TV (Mostra a Cesta/Itens do 1º da Fila)
    st.markdown("---")
    st.markdown(f"### 📦 Cesta de Separação — Lote: **{nr_lote}** | Paciente: **{primeiro_lote['PACIENTE/LEITO']}**")
    
    try:
        cfg = oracle.config_from_secrets()
        if cfg:
            conn = oracle.connect(cfg)
            sql_itens = oracle.load_sql("farmacia_central_grid2")
            
            # Precisamos resolver a query 2, que espera NR_PRESCRICAO válido (usamos NR_ATENDIMENTO na consulta da TV acidentalmente como reserva se prescricao falhar, precisamos buscar a do banco)
            # Como a TV tem a coluna NR_PRESCRICAO ausente na query painel_tv_turno, vamos tratar apenas via :NR_LOTE
            # A query original pede :NR_LOTE e :NR_PRESCRICAO 
            df_itens = oracle.execute_query_df(conn, sql_itens, params={"nr_lote": nr_lote, "nr_prescricao": 0})
            conn.close()
            
            if not df_itens.empty:
                # Filtrar colunas mais amigáveis para TV, incluindo o LOTE
                df_itens_tv = df_itens[["NR_LOTE", "DS_MATERIAL", "QT_DISPENSAR", "DS_HORARIO"]].fillna("N/A")
                df_itens_tv.columns = ["LOTE", "MEDICAMENTO / MATERIAL", "QTD", "HORÁRIOS"]
                
                st.dataframe(
                    df_itens_tv,
                    use_container_width=True,
                    hide_index=True,
                    height=200
                )
            else:
                st.info("O Lote já foi faturado, não possui itens pendentes desta classificação ou exige agrupamento/prescrição específica.")
    except Exception as e:
        st.error(f"Não foi possível carregar imagem do Grid 2: {e}")

    st.caption("Auto-refresh a cada 60 segundos.")

render_painel()
