# Data Quality & Volume Simulator 🚀

¡Bienvenido al **Simulador de Escenarios de Calidad de Datos**! Esta es una librería y herramienta de línea de comandos (CLI) desarrollada en Python diseñada para resolver uno de los problemas más comunes en la ingeniería de datos: la falta de datos de prueba realistas que emulen los desafíos, errores de formato y desorganización estructural del mundo real (*Data Quality & Data Drift*).

A diferencia de los generadores tradicionales que solo crean tablas perfectas, este motor permite generar **volúmenes masivos de datos (más de 1M de registros)** optimizando el uso de memoria RAM mediante **Streaming y Generadores (`yield`)**, permitiendo exportar en múltiples formatos analíticos y de negocio como **Parquet, CSV, JSON, TXT, y Excel (XLSX/XLS)**.

---

## 🛠️ Características Principales y Arquitectura

El proyecto está construido bajo el paradigma de **Programación Orientada a Objetos (POO)** y se divide en dos componentes core:

1.  **`generator_core.py` (El Núcleo Sintético):** Clase `DataGenerator` encargada de la consistencia semántica profunda. Mapea relaciones reales (ej: si el nombre es masculino, el correo es coherente; si la dirección tiene una *Torre* o *Interior*, obliga jerárquicamente a que exista un *Apartamento* u *Oficina* al final). Maneja distribuciones probabilísticas mediante pesos reales del mercado.
2.  **`main.py` (El Orquestador de Escenarios y Streaming):** Aplica mutaciones controladas sobre los datos limpios para simular fallos críticos de calidad de datos, inyectando ruido y procesando la salida por bloques (*Chunks*) hacia el disco.

---

## 🗂️ Escenarios de Datos Soportados (Los Retos ETL)

El simulador permite elegir entre tres niveles de dificultad, ideales para entrenar pipelines en herramientas como Apache Airflow, dbt, Spark, Pandas o data warehouses (BigQuery, Snowflake):

### 1. Limpios y Estructurados (Caso Ideal)
Datos tabulares perfectos con tipado estricto e identificadores únicos. Ideal para probar inserciones directas o simulaciones transaccionales limpias de un ERP.

### 2. Sucios / Formatos Erróneos (Reto de Data Cleansing)
Simula un sistema legacy con problemas graves de calidad. Ideal para practicar expresiones regulares (Regex), transformaciones y tipado en tus ETLs:
* **Fechas Corruptas:** Mezcla formatos en la misma columna (`DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY-MM-DD`).
* **Inconsistencia de Texto:** Mezcla aleatoria de `MAYÚSCULAS`, `minúsculas` y espacios en blanco peligrosos (*trailing spaces*) en nombres y direcciones.
* **Campos Numéricos Sucios:** Strings inyectados en importes financieros (ej: `"$340500.5 COP"`) o casteo erróneo de enteros a flotantes en documentos (`"1017198122.0"`).
* **Data Quality en Booleanos:** Mutación de flags booleanos nativos a textos inconsistentes (`"SI"`, `"0"`, `"false"`, `"S"`).

### 3. Modo 'Basura' / Data Lake Crudo (Reto de Data Drift y Parseo)
Simula la capa **Bronze/Raw** de un Data Lake salvaje. Añade comportamiento acumulativo (hereda los formatos corruptos del escenario 2) y destruye la estructura:
* **Schema Drift (Pérdida de Columnas):** Filas con datos faltantes de manera estocástica (unas filas no tienen correo, otras no tienen celular).
* **Inyección de Ruido (Logs):** Mezcla diccionarios con metadatos basura no requeridos por el negocio como payloads de APIs, estados del servidor (`system_log_status`) o firmas de navegador (`user_agent`).

---

## 💾 Optimización de Memoria Analítica (Streaming & Chunks)

Para evitar errores de desbordamiento de memoria (`Out of Memory`) en servidores al generar volúmenes masivos (ej: 500,000 filas), el script implementa **Generadores de Python (`yield`)**. 

Los datos no se acumulan en la memoria RAM; se transmiten en un flujo continuo (*Streaming*) directo al disco para formatos como **CSV y JSON**. Para formatos analíticos complejos como **Parquet** o **Excel**, los registros se agrupan en memoria en bloques pequeños (*Chunks de 10,000 registros*) y se escriben de forma iterativa mediante métodos `append` eficientes (PyArrow Dataset).

---

## 📊 Formatos de Exportación Disponibles

* **.parquet** (Almacenamiento columnar analítico comprimido - *Exclusivo para el escenario limpio por restricciones de tipado estricto*).
* **.csv** (Separado por comas tradicional, manejado con `DictWriter` para soportar esquemas mutables).
* **.txt** (Plano delimitado por tabulaciones `\t`, emulando salidas de Mainframes antiguos).
* **.xlsx / .xls** (Formatos Excel moderno y antiguo consumidos por áreas de negocio).
* **.json** (Estructura de lista jerárquica).

---

## 🚀 Muestras de Datos Generados

### Muestra: Datos Limpios e Integridad Semántica (.json)
Note la coherencia del correo frente al nombre, el celular con prefijo real de Colombia, y el cálculo exacto del IVA/Subtotal financieros:
```json
{
  "id_transaccion": 61593,
  "fecha": "2026-05-14",
  "nombre_completo": "Alejandro Vargas",
  "tipo_documento": "CC",
  "documento": "821156998",
  "celular": "3017584932",
  "correo": "avargas798@hotmail.com",
  "direccion": "Variante 125 Bis # 95 - 6 Torre 3 Apartamento 402",
  "metodo_pago": "Tarjeta de Crédito",
  "subtotal": 3794095.53,
  "total": 4514973.68,
  "terminos_aceptados": true
}
```
### Muestra: Data Lake Crudo / Modo Basura (.json)
Note el caos estructural: datos faltantes, fechas rotas, strings en números y metadatos basura inyectados aleatoriamente:
```json
[
  {
    "id_transaccion": 37485,
    "fecha": "09/07/2025",
    "nombre_completo": "SANTIAGO BERMÚDEZ",
    "tipo_documento": "CC",
    "documento": "1017198122.0",
    "direccion": "   Carrera 69 # 14 - 11 Consultorio 399   ",
    "metodo_pago": "Efectivo",
    "subtotal": 4325075.08,
    "total": "$5146839.35 COP",
    "terminos_aceptados": "SI",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  {
    "id_transaccion": 14675,
    "fecha": "Fecha: 2026-03-25",
    "nombre_completo": "manuel muñoz",
    "documento": "726864629",
    "subtotal": 2822560.97,
    "total": 3358847.55,
    "terminos_aceptados": "0"
  }
]
```
## Instalación y Uso

#### Clona este repositorio:

```bash
git clone https://github.com/tu-usuario/Data_Generator.git
cd Data_Generator
```

#### Instala las dependencias necesarias en tu entorno virtual:

```bash
pip install -r requirements.txt
```

#### Ejecuta el orquestador interactivo:

```bash
python main.py
```

#### Sigue las instrucciones en la interfaz de consola para elegir la cantidad de registros, el reto de calidad y tu formato preferido.