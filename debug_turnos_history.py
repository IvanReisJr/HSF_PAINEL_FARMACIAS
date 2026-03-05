from app.db import oracle
import pandas as pd

def check_turnos():
    try:
        cfg = oracle.config_from_secrets()
        conn = oracle.connect(cfg)
        
        # SQL para identificar o turno atual e os anteriores
        sql = """
        WITH TURNOS AS (
            SELECT 1 AS ID_TURNO, 'TURNOS 1' AS TURNO, '03:00' AS HORA_INICIAL, '06:59' AS HORA_FINAL FROM DUAL UNION ALL
            SELECT 2, 'TURNOS 2', '07:00', '10:59' FROM DUAL UNION ALL
            SELECT 3, 'TURNOS 3', '11:00', '14:59' FROM DUAL UNION ALL
            SELECT 4, 'TURNOS 4', '15:00', '18:59' FROM DUAL UNION ALL
            SELECT 5, 'TURNOS 5', '19:00', '22:59' FROM DUAL UNION ALL
            SELECT 6, 'TURNOS 6', '23:00', '02:59' FROM DUAL
        ),
        TURNO_ATUAL AS (
            SELECT ID_TURNO
            FROM TURNOS T
            WHERE 
                (T.HORA_INICIAL <= TO_CHAR(SYSDATE, 'HH24:MI') AND T.HORA_FINAL >= TO_CHAR(SYSDATE, 'HH24:MI'))
                OR
                (T.HORA_INICIAL > T.HORA_FINAL AND (TO_CHAR(SYSDATE, 'HH24:MI') >= T.HORA_INICIAL OR TO_CHAR(SYSDATE, 'HH24:MI') <= T.HORA_FINAL))
        )
        SELECT 
            TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') AS DATA_HORA_AGORA,
            CASE 
                WHEN T.ID_TURNO = TA.ID_TURNO THEN 'ATUAL'
                WHEN T.ID_TURNO = TA.ID_TURNO - 1 OR (TA.ID_TURNO = 1 AND T.ID_TURNO = 6) THEN 'ANTERIOR 1'
                WHEN T.ID_TURNO = TA.ID_TURNO - 2 OR (TA.ID_TURNO = 2 AND T.ID_TURNO = 6) OR (TA.ID_TURNO = 1 AND T.ID_TURNO = 5) THEN 'ANTERIOR 2'
                ELSE 'OUTRO'
            END AS STATUS,
            T.* 
        FROM TURNOS T
        CROSS JOIN TURNO_ATUAL TA
        WHERE 
            T.ID_TURNO = TA.ID_TURNO -- Atual
            OR T.ID_TURNO = CASE WHEN TA.ID_TURNO - 1 < 1 THEN 6 ELSE TA.ID_TURNO - 1 END -- Anterior 1
            OR T.ID_TURNO = CASE WHEN TA.ID_TURNO - 2 < 1 THEN 6 + (TA.ID_TURNO - 2) ELSE TA.ID_TURNO - 2 END -- Anterior 2
        ORDER BY 
            CASE 
                WHEN T.ID_TURNO = TA.ID_TURNO THEN 1 
                WHEN T.ID_TURNO = CASE WHEN TA.ID_TURNO - 1 < 1 THEN 6 ELSE TA.ID_TURNO - 1 END THEN 2
                ELSE 3 
            END
        """
        
        df = pd.read_sql(sql, conn)
        print("\n=== TURNO ATUAL E ANTERIORES ===")
        print(df.to_string(index=False))
        print("================================")
        
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_turnos()
