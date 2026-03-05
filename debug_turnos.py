from app.db import oracle
import pandas as pd

def check_current_turno():
    try:
        cfg = oracle.config_from_secrets()
        conn = oracle.connect(cfg)
        
        sql = """
        WITH TURNOS AS (
            SELECT 'TURNOS 1' AS TURNO, '03:00' AS HORA_INICIAL, '06:59' AS HORA_FINAL FROM DUAL UNION ALL
            SELECT 'TURNOS 2', '07:00', '10:59' FROM DUAL UNION ALL
            SELECT 'TURNOS 3', '11:00', '14:59' FROM DUAL UNION ALL
            SELECT 'TURNOS 4', '15:00', '18:59' FROM DUAL UNION ALL
            SELECT 'TURNOS 5', '19:00', '22:59' FROM DUAL UNION ALL
            SELECT 'TURNOS 6', '23:00', '02:59' FROM DUAL
        )
        SELECT 
            TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') AS DATA_HORA_ATUAL,
            T.* 
        FROM TURNOS T
        WHERE 
            (T.HORA_INICIAL <= TO_CHAR(SYSDATE, 'HH24:MI') AND T.HORA_FINAL >= TO_CHAR(SYSDATE, 'HH24:MI'))
            OR
            (T.HORA_INICIAL > T.HORA_FINAL AND (TO_CHAR(SYSDATE, 'HH24:MI') >= T.HORA_INICIAL OR TO_CHAR(SYSDATE, 'HH24:MI') <= T.HORA_FINAL))
        """
        
        df = pd.read_sql(sql, conn)
        print("\n=== RESULTADO DO TURNO ATUAL ===")
        print(df.to_string(index=False))
        print("================================")
        
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_current_turno()
