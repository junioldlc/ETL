from sqlalchemy import text
from database import engine


# ============================================================
# LOAD EDESUR
# ============================================================

def load_edesur(df):

    print("\nCargando datos de Edesur a PostgreSQL...")

    with engine.begin() as conn:

        # Limpiar staging antes de cargar
        conn.execute(
            text(
                "TRUNCATE TABLE staging.stg_edesur_cobros"
            )
        )

        # Insertar DataFrame
        df.to_sql(
            name="stg_edesur_cobros",
            con=conn,
            schema="staging",
            if_exists="append",
            index=False,
            chunksize=1000
        )

    print(
        f"Edesur cargado correctamente: "
        f"{len(df):,} registros."
    )


# ============================================================
# LOAD DGII
# ============================================================

def load_dgii(df):

    print("\nCargando datos de DGII a PostgreSQL...")

    with engine.begin() as conn:

        # Limpiar staging antes de cargar
        conn.execute(
            text(
                "TRUNCATE TABLE staging.stg_dgii_contribuyentes"
            )
        )

        # Insertar DataFrame
        df.to_sql(
            name="stg_dgii_contribuyentes",
            con=conn,
            schema="staging",
            if_exists="append",
            index=False,
            chunksize=5000
        )

    print(
        f"DGII cargado correctamente: "
        f"{len(df):,} registros."
    )