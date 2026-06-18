import json
import random
import csv
from datetime import datetime
import pandas as pd
from generator_core import DataGenerator

class DataOrchestrator:
    def __init__(self):
        self.engine = DataGenerator()

    def _generar_registro_limpio(self):
        """Genera un solo diccionario base."""
        nombre, genero = self.engine.generar_genero_y_nombre()
        apellido = self.engine.generar_apellido()
        correo = self.engine.generar_correo(nombre, apellido)
        doc = self.engine.generar_documento()
        direccion = self.engine.generar_direccion()
        fecha = self.engine.generar_fecha(dias_atras_max=365, formato="YYYY-MM-DD")
        financiero = self.engine.generar_importe_transaccion(tax=True)
        
        celular = self.engine.generar_celular()
        metodo_pago = self.engine.generar_metodo_pago()
        terminos = self.engine.generar_flag_boolean(modo_sucio=False)
        
        return {
            "id_transaccion": random.randint(10000, 99999),
            "fecha": fecha,
            "nombre_completo": f"{nombre} {apellido}",
            "tipo_documento": doc["tipo_documento"],
            "documento": doc["numero_documento"],
            "celular": celular,
            "correo": correo,
            "direccion": direccion,
            "metodo_pago": metodo_pago,
            "subtotal": financiero["subtotal"],
            "total": financiero["total"],
            "terminos_aceptados": terminos
        }

    # =========================================================================
    # ESCENARIOS CON GENERADORES (Usan 'yield' en lugar de listas)
    # =========================================================================
    def stream_escenario_limpio(self, cantidad):
        """Generador eficiente para datos limpios."""
        for _ in range(cantidad):
            yield self._generar_registro_limpio()

    def stream_escenario_sucio(self, cantidad):
        """Generador eficiente para datos sucios con mutación al vuelo."""
        formatos_fecha_erroneos = ["%d/%m/%Y", "%m/%d/%Y", "Fecha: %Y-%m-%d"]
        for _ in range(cantidad):
            reg = self._generar_registro_limpio()
            
            if random.random() < 0.40:
                fecha_obj = datetime.strptime(reg["fecha"], "%Y-%m-%d")
                reg["fecha"] = fecha_obj.strftime(random.choice(formatos_fecha_erroneos))
            if random.random() < 0.30:
                reg["nombre_completo"] = reg["nombre_completo"].upper()
            elif random.random() < 0.60:
                reg["nombre_completo"] = reg["nombre_completo"].lower()
            if random.random() < 0.25:
                reg["direccion"] = f"   {reg['direccion']}   "
            if random.random() < 0.30:
                reg["total"] = f"${reg['total']} COP"
            if random.random() < 0.20:
                reg["documento"] = f"{reg['documento']}.0"
            if random.random() < 0.25:
                reg["celular"] = f"+57 {reg['celular'][:3]}-{reg['celular'][3:6]}-{reg['celular'][6:]}"
            if random.random() < 0.50:
                reg["terminos_aceptados"] = self.engine.generar_flag_boolean(modo_sucio=True)
                
            yield reg

    def stream_escenario_basura(self, cantidad):
        """Generador eficiente para la capa Bronze, combinando flujos."""
        llaves_omitibles = ["correo", "direccion", "tipo_documento", "celular", "metodo_pago"]
        publicidad_basura = [
            {"meta_banner_click": "true", "utm_source": "facebook_ads"},
            {"system_log_status": "DEBUG_OK", "server_id": "ip-10-0-2-4"},
            {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            {"api_request_payload_size_bytes": 2048, "retry_count": 0}
        ]
        
        # Consumimos del generador sucio registro por registro
        for reg in self.stream_escenario_sucio(cantidad):
            if random.random() < 0.35:
                columna_a_borrar = random.choice(llaves_omitibles)
                if columna_a_borrar in reg:
                    del reg[columna_a_borrar]
            if random.random() < 0.50:
                reg.update(random.choice(publicidad_basura))
                
            yield reg

    # =========================================================================
    # EXPORTADOR POR BLOQUES (Ultra bajo consumo de RAM)
    # =========================================================================
    def exportar_datos_stream(self, generador_datos, formato, nombre_archivo):
        """Escribe los datos iterativamente en el disco sin saturar la RAM."""
        formato = formato.lower()

        # 1. EXPORTAR A CSV (Streaming puro, fila por fila)
        if formato == "csv":
            # Para la cabecera tomamos un registro de muestra
            primer_registro = next(generador_datos)
            columnas = list(primer_registro.keys())
            
            with open(f"{nombre_archivo}.csv", "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columnas, extrasaction='ignore')
                writer.writeheader()
                writer.writerow(primer_registro)
                
                # Consumir el resto del generador directo al disco
                for reg in generador_datos:
                    writer.writerow(reg)
            print(f" [STREAM OK] Guardado en: {nombre_archivo}.csv")
            return

        # 2. EXPORTAR A JSON (Formato de lista iterativa)
        elif formato == "json":
            with open(f"{nombre_archivo}.json", "w", encoding="utf-8") as f:
                f.write("[\n")
                primer_registro = next(generador_datos)
                json.dump(primer_registro, f, ensure_ascii=False, indent=2)
                
                for reg in generador_datos:
                    f.write(",\n")
                    json.dump(reg, f, ensure_ascii=False, indent=2)
                f.write("\n]")
            print(f" [STREAM OK] Guardado en: {nombre_archivo}.json")
            return

        # 3. FORMATOS ANALÍTICOS (Parquet, XLSX, TXT) mediante Chunks de Pandas
        else:
            # Agrupamos los datos en bloques pequeños (ej: de a 10,000 filas)
            chunk_size = 10000
            chunk = []
            es_primero = True
            
            for reg in generador_datos:
                chunk.append(reg)
                if len(chunk) == chunk_size:
                    df = pd.DataFrame(chunk)
                    self._escribir_chunk_pandas(df, formato, nombre_archivo, es_primero)
                    chunk = []
                    es_primero = False
            
            # Escribir el residuo que quede
            if chunk:
                df = pd.DataFrame(chunk)
                self._escribir_chunk_pandas(df, formato, nombre_archivo, es_primero)
                
            print(f" [CHUNK OK] Guardado en avanzado: {nombre_archivo}.{formato}")

    def _escribir_chunk_pandas(self, df, formato, nombre_archivo, es_primero):
        """Escribe bloques parciales (append) según el formato."""
        if formato == "txt":
            mode = "w" if es_primero else "a"
            header = es_primero
            df.to_csv(f"{nombre_archivo}.txt", sep="\t", index=False, mode=mode, header=header)
            
        elif formato == "parquet":
            # Parquet nativo permite append por filas usando fastparquet o pyarrow.dataset
            # Para simplificar manteniéndolo ligero, pyarrow maneja append de tablas:
            import pyarrow as pa
            import pyarrow.parquet as pq
            table = pa.Table.from_pandas(df)
            mode = "w" if es_primero else "a"
            if es_primero:
                self.parquet_writer = pq.ParquetWriter(f"{nombre_archivo}.parquet", table.schema)
            self.parquet_writer.write_table(table)
            
        elif formato in ["xlsx", "xls"]:
            # Excel no soporta streaming nativo real de forma fácil sin cargar el libro completo.
            # Sin embargo, usando openpyxl en modo 'a' se mitiga el impacto. 
            mode = "w" if es_primero else "a"
            if es_primero:
                df.to_excel(f"{nombre_archivo}.{formato}", index=False)
            else:
                with pd.ExcelWriter(f"{nombre_archivo}.{formato}", mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
                    df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)


# =========================================================================
# MENÚ INTERACTIVO (CLI)
# =========================================================================
if __name__ == "__main__":
    orquestador = DataOrchestrator()
    print("\n==========================================================")
    print("   MOTOR EN STREAMING PARA VOLÚMENES MASIVOS DE DATOS     ")
    print("==========================================================\n")
    
    try:
        cantidad = int(input("¿Cuántos registros deseas generar?: "))
        print("\nSelecciona el tipo de datos/reto de ingeniería:")
        print("1. Limpios y Estructurados (Caso Ideal)")
        print("2. Sucios / Formatos Erróneos (Reto de Data Cleansing)")
        print("3. Modo 'Basura' / Data Lake Crudo (Reto de Data Drift)")
        opcion = int(input("Elige una opción (1-3): "))
        
        print("\n¿En qué formato deseas exportar el resultado?")
        print("1. JSON")
        print("2. CSV")
        print("3. TXT (Delimitado por Tabuladores)")
        print("4. XLSX (Excel Moderno)")
        print("5. XLS (Excel Legacy)")
        
        if opcion == 1:
            print("6. PARQUET (Formato Columnar Analítico - Solo datos limpios)")
            max_formato = 6
        else:
            max_formato = 5
            
        formato_opcion = int(input(f"Elige formato (1-{max_formato}): "))
        formatos_map = {1: "json", 2: "csv", 3: "txt", 4: "xlsx", 5: "xls", 6: "parquet"}
        formato = formatos_map.get(formato_opcion, "csv")
        
        # En vez de almacenar listas, pasamos la FUNCIÓN GENERADORA (sin ejecutar con paréntesis aún)
        if opcion == 1:
            gen = orquestador.stream_escenario_limpio(cantidad)
            archivo_final = "datos_perfectos"
        elif opcion == 2:
            gen = orquestador.stream_escenario_sucio(cantidad)
            archivo_final = "datos_corruptos_reto"
        elif opcion == 3:
            gen = orquestador.stream_escenario_basura(cantidad)
            archivo_final = "datalake_raw_basura"
        else:
            print("Opción inválida.")
            exit()
            
        # Lanzar el guardado iterativo
        orquestador.exportar_datos_stream(gen, formato, archivo_final)
        
        # Si se abrió un stream de parquet, cerrarlo de forma segura
        if formato == "parquet" and opcion == 1:
            orquestador.parquet_writer.close()
            
        print("\n¡Proceso de generación completado con éxito!")
        
    except ValueError as e:
        print(f"\n[ERROR] Entrada inválida detectada: {e}")