CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.stg_edesur_cobros
(
    zona VARCHAR(100) NOT NULL,
    cobros_rd_mm NUMERIC(15,6),
    mes VARCHAR(20) NOT NULL,
    numero_mes SMALLINT NOT NULL,
    ano INTEGER NOT NULL,
    fecha DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.stg_dgii_contribuyentes
(
    rnc VARCHAR(20) NOT NULL,
    razon_social TEXT NOT NULL,
    actividad_economica TEXT,
    fecha_inicio_operaciones DATE,
    estado VARCHAR(50) NOT NULL,
    regimen_pago VARCHAR(50) NOT NULL
);