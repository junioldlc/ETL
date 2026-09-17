import pandas as pd
import configparser
import requests
import zipfile
import os

def extract_transform_dgii():
    # ============================================================
    # CONFIGURACIÓN
    # ============================================================

    config = configparser.ConfigParser()
    config.read("config.ini")

    url = config["DGII"]["DGII_url"]
    encoding = config["DGII"]["encoding"]

    zip_path = "RNC_Contribuyentes.zip"


    # ============================================================
    # HEADERS HTTP
    # ============================================================

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*"
    }


    # ============================================================
    # EXTRACT
    # ============================================================

    print("Descargando archivo de DGII...")

    with requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=120
    ) as response:

        response.raise_for_status()

        print(f"HTTP Status: {response.status_code}")

        with open(zip_path, "wb") as archivo:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if chunk:
                    archivo.write(chunk)


    print("ZIP descargado correctamente.")


    # ============================================================
    # ABRIR ZIP
    # ============================================================

    with zipfile.ZipFile(zip_path, "r") as zip_file:

        csv_files = [
            name
            for name in zip_file.namelist()
            if name.lower().endswith(".csv")
        ]

        if not csv_files:
            raise ValueError(
                "El ZIP de DGII no contiene archivos CSV."
            )

        csv_name = csv_files[0]

        print(f"CSV encontrado: {csv_name}")

        with zip_file.open(csv_name) as csv_file:

            df = pd.read_csv(
                csv_file,
                encoding=encoding
            )


    print(f"Registros extraídos: {len(df):,}")


    # ============================================================
    # TRANSFORM
    # ============================================================

    print("Transformando datos de DGII...")


    # ------------------------------------------------------------
    # 1. Renombrar columnas
    # ------------------------------------------------------------

    df = df.rename(columns={
        "RNC": "rnc",
        "RAZÓN SOCIAL": "razon_social",
        "ACTIVIDAD ECONÓMICA": "actividad_economica",
        "FECHA DE INICIO OPERACIONES": "fecha_inicio_operaciones",
        "ESTADO": "estado",
        "RÉGIMEN DE PAGO": "regimen_pago"
    })


    # ------------------------------------------------------------
    # 2. Convertir RNC a texto
    # ------------------------------------------------------------

    df["rnc"] = df["rnc"].astype("string")


    # ------------------------------------------------------------
    # 3. Limpiar columnas de texto
    # ------------------------------------------------------------

    columnas_texto = [
        "rnc",
        "razon_social",
        "actividad_economica",
        "estado",
        "regimen_pago"
    ]

    for columna in columnas_texto:
        df[columna] = df[columna].str.strip()


    # ------------------------------------------------------------
    # 4. Convertir fecha
    # ------------------------------------------------------------

    df["fecha_inicio_operaciones"] = pd.to_datetime(
        df["fecha_inicio_operaciones"],
        errors="coerce",
        dayfirst=True
    )


    # ------------------------------------------------------------
    # 5. Convertir strings vacíos a NULL
    # ------------------------------------------------------------

    for columna in columnas_texto:

        df[columna] = df[columna].replace(
            "",
            pd.NA
        )


    # ------------------------------------------------------------
    # 6. Ordenar columnas
    # ------------------------------------------------------------

    df = df[
        [
            "rnc",
            "razon_social",
            "actividad_economica",
            "fecha_inicio_operaciones",
            "estado",
            "regimen_pago"
        ]
    ]


    # ============================================================
    # VALIDACIONES
    # ============================================================

    print("\n========================================")
    print("VALIDACIÓN DGII")
    print("========================================")

    print(f"\nRegistros: {len(df):,}")


    print("\nTipos:")
    print(df.dtypes)


    print("\nValores nulos:")
    print(df.isna().sum())


    print("\nEstados:")
    print(
        df["estado"]
        .value_counts(dropna=False)
    )


    print("\nRegímenes de pago:")
    print(
        df["regimen_pago"]
        .value_counts(dropna=False)
    )


    print("\nRNC duplicados:")
    print(
        df["rnc"]
        .duplicated()
        .sum()
    )


    print("\nEjemplos de RNC duplicados:")

    duplicados = df[
        df["rnc"].duplicated(
            keep=False
        )
    ].sort_values("rnc")

    print(
        duplicados.head(20).to_string(
            index=False
        )
    )


    print("\nRango de fechas:")

    print(
        "Desde:",
        df["fecha_inicio_operaciones"].min()
    )

    print(
        "Hasta:",
        df["fecha_inicio_operaciones"].max()
    )


    print("\nPrimeros registros:")
    print(df.head())


    print("\nTransformación DGII completada.")


    # ============================================================
    # ELIMINAR ZIP TEMPORAL
    # ============================================================

    if os.path.exists(zip_path):

        os.remove(zip_path)

        print(
            f"\nArchivo temporal eliminado: {zip_path}"
        )
        
    return df