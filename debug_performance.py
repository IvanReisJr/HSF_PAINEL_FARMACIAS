import time
import pandas as pd
from app.db import oracle

def test_performance():
    print("Iniciando teste de performance da query Farmácia Central...")
    
    # Configuração
    cfg = oracle.config_from_secrets()
    if not cfg:
        print("Erro: Configuração não encontrada.")
        return

    try:
        conn = oracle.connect(cfg)
        print("Conexão estabelecida.")
        
        # Carregar SQL
        sql = oracle.load_sql("farmacia_central")
        print("SQL carregado.")
        
        # Executar e medir tempo
        start_time = time.time()
        print("Executando query...")
        
        df = oracle.execute_query_df(conn, sql)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n--- Resultados ---")
        print(f"Tempo de execução: {duration:.2f} segundos")
        print(f"Registros retornados: {len(df)}")
        print(f"Colunas: {list(df.columns)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    # Setup sys.path para imports funcionarem
    import sys
    import os
    sys.path.append(os.getcwd())
    
    test_performance()
