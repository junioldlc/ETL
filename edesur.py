import pandas as pd
import configparser

def extract_transform_edesur():

# ============================================================
# CONFIGURACIÓN
# ============================================================

    config = configparser.ConfigParser()
    config.read("config.ini")

    url = config["edesur"]["edesur_url"]
    encoding = config["edesur"]["encoding"]


    # ============================================================
    # EXTRACT
    # ============================================================

    print("Extrayendo datos de Edesur...")

    df = pd.read_csv(
        url,
        encoding=encoding
    )

    print(f"Registros extraídos: {len(df):,}")


    # ============================================================
    # TRANSFORM
    # ============================================================

    print("Transformando datos de Edesur...")


    # ------------------------------------------------------------
    # 1. Renombrar columnas
    # ------------------------------------------------------------

    df = df.rename(columns={
        "ZONA": "zona",
        "COBROS (RD$ MM)": "cobros_rd_mm",
        "MES": "mes",
        "AÑO": "ano"
    })


    # ------------------------------------------------------------
    # 2. Limpiar strings
    # ------------------------------------------------------------

    df["zona"] = df["zona"].str.strip()
    df["mes"] = df["mes"].str.strip()


    # ------------------------------------------------------------
    # 3. Normalizar nombres de zonas
    # ------------------------------------------------------------

    mapeo_zonas = {
        "Zona Distrito": "Zona 1 - Distrito",
        "Zona San Cristobal": "Zona 2 - San Cristóbal",
        "Zona Bani": "Zona 3 - Baní",
        "Zona San Juan": "Zona 4 - San Juan",
        "Zona Barahona": "Zona 5 - Barahona",
        "Zona Santo Domingo": "Zona 6 - Santo Domingo"
    }

    df["zona"] = df["zona"].replace(mapeo_zonas)


    # ------------------------------------------------------------
    # 4. Convertir nombre del mes a número
    # ------------------------------------------------------------

    meses = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12
    }

    df["numero_mes"] = df["mes"].map(meses)


    # ------------------------------------------------------------
    # 5. Asegurar tipos
    # ------------------------------------------------------------

    df["ano"] = pd.to_numeric(
        df["ano"],
        errors="coerce"
    )

    df["cobros_rd_mm"] = pd.to_numeric(
        df["cobros_rd_mm"],
        errors="coerce"
    )


    # ------------------------------------------------------------
    # 6. Crear fecha
    # ------------------------------------------------------------

    df["fecha"] = pd.to_datetime(
        {
            "year": df["ano"],
            "month": df["numero_mes"],
            "day": 1
        },
        errors="coerce"
    )


    # ------------------------------------------------------------
    # 7. Ordenar columnas
    # ------------------------------------------------------------

    df = df[
        [
            "zona",
            "cobros_rd_mm",
            "mes",
            "numero_mes",
            "ano",
            "fecha"
        ]
    ]


    # ------------------------------------------------------------
    # 8. Ordenar cronológicamente
    # ------------------------------------------------------------

    df = df.sort_values(
        by=["fecha", "zona"]
    ).reset_index(drop=True)


    # ============================================================
    # VALIDACIÓN
    # ============================================================

    print("\n========================================")
    print("VALIDACIÓN EDESUR")
    print("========================================")

    print(f"\nRegistros: {len(df):,}")

    print("\nColumnas:")
    print(df.columns.tolist())

    print("\nTipos:")
    print(df.dtypes)

    print("\nValores nulos:")
    print(df.isna().sum())

    print("\nZonas:")
    print(df["zona"].value_counts())

    print("\nPrimeros registros:")
    print(df.head())

    print("\nÚltimos registros:")
    print(df.tail())

    print("\nTransformación Edesur completada.")

    return df