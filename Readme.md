# ETL de Cobros Edesur y Contribuyentes DGII

## Descripción

Este proyecto implementa un proceso **ETL (Extract, Transform, Load)** desarrollado en Python para integrar información proveniente de dos fuentes públicas:

- **Edesur:** información histórica de cobros.
- **DGII:** listado de contribuyentes registrados en el RNC.

Los datos son extraídos desde sus fuentes originales, transformados utilizando **Pandas** y posteriormente cargados en una base de datos **PostgreSQL**.

Finalmente, la información almacenada en PostgreSQL puede ser consumida desde **Power BI** para realizar análisis y visualizaciones.

## Arquitectura

El flujo general del proyecto es:

```text
          FUENTES

 Edesur CSV       DGII ZIP/CSV
      │                │
      ▼                ▼
  edesur.py         dgii.py
      │                │
      └───────┬────────┘
              │
              ▼
        DataFrames Pandas
              │
              ▼
           load.py
              │
              ▼
          PostgreSQL
              │
              ▼
           Power BI
```

## Tecnologías utilizadas

- Python
- Pandas
- Requests
- ZipFile
- SQLAlchemy
- Psycopg
- PostgreSQL
- Power BI

## Estructura del proyecto

```text
ETL/
│
├── main.py
├── edesur.py
├── dgii.py
├── database.py
├── load.py
│
├── config.ini
├── config.example.ini
├── requirements.txt
│
├── sql/
│   └── create_tables.sql
│
└── powerbi/
    └── Dashboard_ETL.pbix
```

## Descripción de los archivos Python

### `main.py`

Es el **orquestador principal del pipeline ETL**.

Su responsabilidad es controlar el orden en el que se ejecutan los diferentes procesos.

El flujo ejecutado es:

```text
Extraer/Transformar Edesur
          ↓
Cargar Edesur en PostgreSQL
          ↓
Extraer/Transformar DGII
          ↓
Cargar DGII en PostgreSQL
```

Las funciones principales son importadas desde los demás módulos:

```python
from edesur import extract_transform_edesur
from dgii import extract_transform_dgii
from load import load_edesur, load_dgii
```

Los DataFrames generados durante la extracción y transformación son enviados posteriormente a las funciones encargadas de realizar la carga.

---

### `edesur.py`

Contiene el proceso de **extracción y transformación de los datos de Edesur**.

La función principal es:

```python
extract_transform_edesur()
```

Entre sus responsabilidades se encuentran:

- Descargar/leer el archivo CSV publicado por Edesur.
- Cargar los datos en un DataFrame de Pandas.
- Normalizar los nombres de las columnas.
- Estandarizar los nombres de las zonas.
- Convertir los meses a su representación numérica.
- Crear una fecha a partir del año y el mes.
- Convertir los tipos de datos necesarios.
- Ordenar y validar la información.

La función finalmente devuelve un DataFrame transformado:

```python
return df
```

Este DataFrame es recibido por `main.py` y posteriormente enviado a `load.py`.

---

### `dgii.py`

Contiene el proceso de **extracción y transformación del listado de contribuyentes de la DGII**.

La fuente de DGII es proporcionada como un archivo comprimido ZIP que contiene un archivo CSV.

El proceso realizado es:

```text
DGII
  ↓
Descarga HTTP
  ↓
Archivo ZIP
  ↓
Extracción del CSV
  ↓
Pandas DataFrame
  ↓
Transformaciones
```

Para la descarga se utiliza `requests`, mientras que el contenido comprimido es procesado utilizando `zipfile`.

Entre las transformaciones realizadas se encuentran:

- Normalización de nombres de columnas.
- Conversión del RNC a texto.
- Limpieza de campos de texto.
- Conversión de la fecha de inicio de operaciones a tipo fecha.
- Tratamiento de valores vacíos.
- Validación de cantidad de registros y valores nulos.

La función principal:

```python
extract_transform_dgii()
```

devuelve el DataFrame transformado para que pueda ser cargado posteriormente en PostgreSQL.

---

### `database.py`

Centraliza la **configuración de conexión con PostgreSQL**.

Lee los parámetros de conexión definidos en:

```text
config.ini
```

como:

```ini
[postgresql]
host=localhost
port=5432
database=etl
username=postgres
password=PASSWORD
```

Posteriormente crea un `engine` de SQLAlchemy:

```python
engine = create_engine(...)
```

Este objeto es reutilizado por `load.py` para establecer las conexiones con PostgreSQL.

De esta manera las credenciales y la lógica de conexión no tienen que repetirse en cada módulo.

---

### `load.py`

Contiene la etapa **Load** del proceso ETL.

Recibe los DataFrames previamente procesados por `edesur.py` y `dgii.py` y los carga en PostgreSQL.

Las funciones principales son:

```python
load_edesur(df)
load_dgii(df)
```

Antes de realizar cada carga se ejecuta un:

```sql
TRUNCATE TABLE
```

sobre la tabla correspondiente.

Posteriormente se utiliza:

```python
df.to_sql(...)
```

para insertar los registros.

La estrategia utilizada es por tanto una **carga completa (Full Refresh)**:

```text
DataFrame transformado
        ↓
TRUNCATE tabla staging
        ↓
INSERT nuevos registros
        ↓
PostgreSQL
```

La operación se realiza dentro de una transacción utilizando:

```python
with engine.begin() as conn:
```

permitiendo realizar `COMMIT` cuando la operación termina correctamente o `ROLLBACK` si ocurre un error durante la carga.

---

## Modelo de datos

Los datos son almacenados en PostgreSQL dentro del schema:

```text
staging
```

Actualmente se utilizan las siguientes tablas:

### Edesur

```text
staging.stg_edesur_cobros
```

Contiene información de cobros organizada por zona y período.

Principales campos:

```text
zona
cobros_rd_mm
mes
numero_mes
ano
fecha
```

### DGII

```text
staging.stg_dgii_contribuyentes
```

Contiene la información correspondiente al listado de contribuyentes de DGII.

Principales campos:

```text
rnc
razon_social
actividad_economica
fecha_inicio_operaciones
estado
regimen_pago
```

## Decisiones de diseño

### RNC almacenado como texto

Aunque el RNC contiene únicamente números, se almacena como texto debido a que representa un **identificador** y no una cantidad sobre la cual se realizarán operaciones matemáticas.

### RNC no utilizado como clave primaria

Durante el análisis de los datos se identificó que algunos RNC aparecen en múltiples registros.

Entre los casos observados existen contribuyentes asociados a diferentes actividades económicas.

Por esta razón no se eliminan automáticamente los registros duplicados por RNC ni se utiliza el RNC como clave primaria de la tabla de staging.

Esto permite preservar la granularidad proporcionada por la fuente original.

### Procesamiento del ZIP de DGII

La fuente de DGII distribuye la información dentro de un archivo ZIP.

Se decidió separar las responsabilidades utilizando:

```text
requests
    ↓
Descarga HTTP

zipfile
    ↓
Procesamiento del ZIP

pandas
    ↓
Lectura y transformación del CSV
```

Esto permite tener mayor control sobre la descarga y procesamiento de la fuente.

### Full Refresh

Para esta implementación se utiliza una estrategia de carga completa.

En cada ejecución:

```text
Fuente
   ↓
Extracción completa
   ↓
Transformación
   ↓
TRUNCATE
   ↓
Carga completa
```

Esta estrategia fue seleccionada por la naturaleza de la práctica y por permitir que cada ejecución genere un estado consistente de las tablas a partir de las fuentes actuales.

Para volúmenes mayores o escenarios productivos podría implementarse posteriormente una estrategia de carga incremental.

## Instalación

### 1. Clonar o descargar el proyecto

Descargar el proyecto y acceder al directorio:

```powershell
cd ETL
```

### 2. Crear un entorno virtual

```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```powershell
pip install -r requirements.txt
```

## Configuración

Copiar:

```text
config.example.ini
```

como:

```text
config.ini
```

y configurar los parámetros correspondientes a PostgreSQL y las fuentes de datos.

Ejemplo:

```ini
[postgresql]
host=localhost
port=5432
database=etl
username=postgres
password=PASSWORD
```

> `config.ini` puede contener credenciales y no debe publicarse en repositorios públicos.

## Preparación de PostgreSQL

Crear la base de datos correspondiente y posteriormente ejecutar:

```text
sql/create_tables.sql
```

Este script crea los schemas y tablas necesarios para recibir los datos procesados por el pipeline.

## Ejecución

Con el entorno virtual activado:

```powershell
python main.py
```

El pipeline ejecutará automáticamente:

```text
1. Extracción de Edesur
2. Transformación de Edesur
3. Carga de Edesur en PostgreSQL
4. Extracción de DGII
5. Transformación de DGII
6. Carga de DGII en PostgreSQL
```

## Visualización en Power BI

PostgreSQL funciona como fuente de datos para Power BI.

El dashboard permite analizar, entre otros:

### Edesur

- Total de cobros.
- Cobros por provincia/zona.
- Cobros por período.
- Comparación de cobros entre provincias.
- Provincias con mayores montos de cobros.
- Filtrado interactivo por provincia.

### DGII

- Total de contribuyentes.
- Distribución por régimen de pago.
- Distribución por estado.
- Principales actividades económicas.
- Consulta y filtrado de contribuyentes según régimen de pago.

## Reproducibilidad

Para reproducir el proyecto en otro equipo se requiere:

```text
Python
   ↓
requirements.txt

PostgreSQL
   ↓
create_tables.sql

Configuración
   ↓
config.example.ini → config.ini

Pipeline
   ↓
python main.py

Visualización
   ↓
Power BI
```

Los archivos originales de las fuentes no necesitan ser incluidos en la entrega debido a que el pipeline obtiene la información directamente desde las fuentes configuradas.
