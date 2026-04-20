import streamlit as st

# Ocultar o menu "app" utilizando o novo sistema de navegação do Streamlit (v1.36+)
pg = st.navigation([
    st.Page("pages/farmacia_central.py", title="Farmácia Central", icon="💊"),
    st.Page("pages/painel_tv.py", title="Painel TV", icon="📺")
])

pg.run()
