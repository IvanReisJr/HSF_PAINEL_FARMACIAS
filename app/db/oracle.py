from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import oracledb
import pandas as pd

try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # noqa: N816


@dataclass(slots=True)
class OracleConfig:
    user: str
    password: str
    host: str
    port: int = 1521
    service_name: str = "XE"


def build_dsn(host: str, port: int, service_name: str) -> str:
    """Build a DSN string for Thin mode connection."""
    # Use Easy Connect string format which is robust for Thin mode
    return f"{host}:{port}/{service_name}"


def connect(cfg: OracleConfig):
    if not cfg.host or not cfg.user:
        raise ValueError("Host e User são obrigatórios para conexão Oracle.")
    
    # Tenta inicializar o Thick Mode explicitamente com o caminho fornecido
    try:
        # Caminho relativo ao projeto para o Instant Client
        base_dir = Path(__file__).parent.parent.parent
        lib_dir = base_dir / "utils" / "instantclient-basiclite-windows"
        
        # Log para debug (aparecerá no terminal do Streamlit)
        print(f"Tentando inicializar Oracle Client em: {lib_dir}")
        
        if lib_dir.exists():
            oracledb.init_oracle_client(lib_dir=str(lib_dir))
            print("Oracle Client inicializado com sucesso!")
        else:
            print(f"Pasta do Oracle Client não encontrada: {lib_dir}")
            oracledb.init_oracle_client()
            
    except Exception as e:
        # Se falhar, imprime o erro no console para diagnóstico
        print(f"Erro ao inicializar Oracle Client: {e}")
        pass

    dsn = build_dsn(cfg.host, cfg.port, cfg.service_name)
    return oracledb.connect(user=cfg.user, password=cfg.password, dsn=dsn)


def select_one_dual(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("select 1 from dual")
        val = cur.fetchone()
        return int(val[0]) if val else 0


def load_sql(query_name: str) -> str:
    """Load SQL from a file in the queries directory."""
    # Assuming this file is in app/db/oracle.py, queries are in app/queries/
    base_dir = Path(__file__).parent.parent
    query_path = base_dir / "queries" / f"{query_name}.sql"
    if not query_path.exists():
        raise FileNotFoundError(f"SQL file not found: {query_path}")
    
    with open(query_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_query_df(conn, sql: str, params: Optional[dict[str, Any]] = None) -> pd.DataFrame:
    """Execute a SQL query and return a pandas DataFrame."""
    if params is None:
        params = {}
    
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        
    return pd.DataFrame(data, columns=columns)


def config_from_secrets() -> Optional[OracleConfig]:
    if st is None:  # pragma: no cover
        return None
    try:
        sec = st.secrets.get("oracle")  # type: ignore[attr-defined]
    except Exception:
        sec = None
    if not sec:
        return None
    return OracleConfig(
        user=str(sec.get("user", "")),
        password=str(sec.get("password", "")),
        host=str(sec.get("host", "")),
        port=int(sec.get("port", 1521)),
        service_name=str(sec.get("service_name", "XE")),
    )

