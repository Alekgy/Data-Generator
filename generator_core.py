import json
import random
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, json_path="datos_json/data_source.json"):
        """Carga el archivo JSON de recursos en memoria al inicializar la clase."""
        with open(json_path, "r", encoding="utf-8") as f:
            self.source = json.load(f)

    def generar_genero_y_nombre(self):
        """Garantiza consistencia de género y nombre."""
        genero = random.choice(["Masculino", "Femenino"])
        if genero == "Masculino":
            nombre = random.choice(self.source["nombres"]["masculinos"])
        else:
            nombre = random.choice(self.source["nombres"]["femeninos"])
        return nombre, genero

    def generar_apellido(self):
        """Saca un apellido al azar de la lista."""
        return random.choice(self.source["apellidos"])

    def generar_correo(self, nombre, apellido):
        """
        Construye un correo realista agregando un sufijo numérico aleatorio
        al final para evitar colisiones/duplicados en restricciones UNIQUE de BD.
        """
        dominios = [item["dominio"] for item in self.source["correos"]]
        pesos = [item["peso"] for item in self.source["correos"]]
        dominio_elegido = random.choices(dominios, weights=pesos, k=1)[0]
        
        # Normalizar texto (quitar tildes y minúsculas)
        nombre_limpio = nombre.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        apellido_limpio = apellido.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        
        # Agregar un número aleatorio al final para garantizar unicidad (ej: 12, 493)
        sufijo_numerico = random.randint(10, 999)
        
        formato = random.choice([
            f"{nombre_limpio}.{apellido_limpio}{sufijo_numerico}", 
            f"{nombre_limpio[0]}{apellido_limpio}{sufijo_numerico}"
        ])
        
        return f"{formato}@{dominio_elegido}"

    def generar_documento(self):
        """Selecciona tipo de documento con pesos y genera su número."""
        tipos = [item["tipo"] for item in self.source["documentos_identidad"]]
        pesos = [item["peso"] for item in self.source["documentos_identidad"]]
        tipo_elegido = random.choices(tipos, weights=pesos, k=1)[0]
        
        if tipo_elegido in ["CC", "CE"]:
            numero = str(random.randint(10000000, 1199999999))
        elif tipo_elegido == "NIT":
            numero = f"{random.randint(800000000, 999999999)}-{random.randint(0, 9)}"
        else:
            letras = "".join(random.choices(self.source["alfanumerico"]["mayusculas"], k=2))
            numeros = "".join(str(random.choice(self.source["alfanumerico"]["numeros"])) for _ in range(6))
            numero = f"{letras}{numeros}"
            
        return {"tipo_documento": tipo_elegido, "numero_documento": numero}

    # =========================================================================
    # NUEVAS FUNCIONES SOLICITADAS
    # =========================================================================

    def generar_fecha(self, dias_atras_max=365, formato="YYYY-MM-DD"):
        """
        Genera una fecha aleatoria hacia el pasado basada en un rango de días.
        Permite seleccionar dinámicamente el formato de salida.
        """
        dias_aleatorios = random.randint(0, dias_atras_max)
        fecha_calculada = datetime.now() - timedelta(days=dias_aleatorios)
        
        # Mapeo de formatos comunes a directivas de Python strftime
        if formato == "DD/MM/YYYY":
            return fecha_calculada.strftime("%d/%m/%Y")
        elif formato == "MM/DD/YYYY":
            return fecha_calculada.strftime("%m/%d/%Y")
        else:
            return fecha_calculada.strftime("%Y-%m-%d") # ISO estándar por defecto

    def generar_importe_transaccion(self, min_valor=10000, max_valor=5000000, tax=False, tax_rate=0.19):
        """
        Genera montos financieros aleatorios redondeados.
        Si 'tax' es True, calcula el impuesto basado en el 'tax_rate' (ej: 0.19 para el 19% de IVA).
        """
        # Generar importe base y redondearlo a 2 decimales
        importe_base = round(random.uniform(min_valor, max_valor), 2)
        
        resultado = {
            "subtotal": importe_base,
            "impuesto": 0.0,
            "total": importe_base
        }
        
        if tax:
            # Calcular impuesto y total
            resultado["impuesto"] = round(importe_base * tax_rate, 2)
            resultado["total"] = round(resultado["subtotal"] + resultado["impuesto"], 2)
            
        return resultado

    def generar_direccion(self):
        """
        Construye una dirección urbana estructurada de forma algorítmica.
        Garantiza consistencia: Si se genera una Torre, Bloque o Interior,
        se le obliga a tener un Apartamento, Oficina o Consultorio al final.
        """
        nom = self.source["nomenclaturas"]
        
        # 1. Elegir vía principal (Calle, Carrera, etc.)
        via_principal = random.choice(nom["vias_principales"])
        
        # 2. Generar el número principal y evaluar si lleva letra/bis/cuadrante
        num1 = random.randint(1, 150)
        letra1 = f" {random.choice(nom['vias_secundarias_y_complementos'])}" if random.random() < 0.4 else ""
        
        # 3. Generar número de cruce o puerta
        num2 = random.randint(1, 99)
        letra2 = f"{random.choice(['A', 'B', 'C', 'D']).lower()}" if random.random() < 0.25 else ""
        num3 = random.randint(1, 99)
        
        # Construcción de la grilla base
        direccion_base = f"{via_principal} {num1}{letra1} # {num2}{letra2} - {num3}"
        
        # 4. Decidir si se agrega un complemento de inmueble (50% de probabilidad)
        if random.random() < 0.50:
            tipo_inmueble = random.choice(nom["tipos_de_inmueble"])
            
            # CASO ESPECIAL: Si es un contenedor estructural (Torre, Bloque, Interior)
            if tipo_inmueble in ["Torre", "Bloque", "Interior"]:
                num_contenedor = random.randint(1, 15)
                # Elegimos un destino final lógico para albergar dentro de una torre/bloque
                sub_inmueble = random.choice(["Apartamento", "Oficina", "Consultorio"])
                num_final = random.randint(101, 1205) # Pisos del 1 al 12
                
                direccion_base += f" {tipo_inmueble} {num_contenedor} {sub_inmueble} {num_final}"
            
            # CASO COMÚN: Destinos directos sin contenedor previo
            else:
                if tipo_inmueble in ["Apartamento", "Oficina", "Consultorio"]:
                    num_inmueble = random.randint(101, 505) # Edificios pequeños sin torre especificada
                else:
                    num_inmueble = random.randint(1, 5) # Locales o bodegas a la calle
                    
                direccion_base += f" {tipo_inmueble} {num_inmueble}"
                
        return direccion_base
    
    def generar_celular(self):
        """Generar un número celular con prefijo real de Colombia."""
        prefijo = random.choice(self.source["prefijos_celular"])
        # Generar los 7 dígitos restantes
        cuerpo = "".join(str(random.choice(self.source["alfanumerico"]["numeros"])) for _ in range(7))
        return f"{prefijo}{cuerpo}"

    def generar_metodo_pago(self):
        """Elige un método de pago respetando los pesos del mercado."""
        metodos = [item["metodo"] for item in self.source["metodos_pago"]]
        pesos = [item["peso"] for item in self.source["metodos_pago"]]
        return random.choices(metodos, weights=pesos, k=1)[0]

    def generar_flag_boolean(self, modo_sucio=False):
        """Genera banderas de control. Si es sucio, altera los formatos del booleano."""
        valor_base = random.choice([True, False])
        
        if not modo_sucio:
            return valor_base
        else:
            # En modo sucio, rompe la consistencia del tipo de dato (Data Quality Nightmare)
            if valor_base:
                return random.choice(["true", "1", "S", "SI", "True"])
            else:
                return random.choice(["false", "0", "N", "NO", "False"])
    
    
# if __name__ == "__main__":
#     # Inicializamos el motor
#     generador = DataGenerator()
    
#     print("==================================================================")
#     print("      REGISTROS GENERADOS COMPLEJOS (ESTILO TRANSACCIONAL/ERP)   ")
#     print("==================================================================")
    
#     for i in range(1, 4):
#         nombre, genero = generador.generar_genero_y_nombre()
#         apellido = generador.generar_apellido()
        
#         # Datos Core ampliados
#         correo = generador.generar_correo(nombre, apellido)
#         doc = generador.generar_documento()
#         direccion = generador.generar_direccion()
#         fecha = generador.generar_fecha(dias_atras_max=180, formato="DD/MM/YYYY")
        
#         # Simulación financiera: Activar IVA (19%) de manera obligatoria o aleatoria
#         datos_financieros = generador.generar_importe_transaccion(tax=True, tax_rate=0.19)
        
#         print(f"\n[REGISTRO DE VENTA #{i}] - Fecha: {fecha}")
#         print(f"  Cliente:     {nombre} {apellido} | Identificación: {doc['tipo_documento']} {doc['numero_documento']}")
#         print(f"  Contacto:    {correo} | Dirección: {direccion}")
#         print(f"  Financiero:  Subtotal: ${datos_financieros['subtotal']:,} | IVA (19%): ${datos_financieros['impuesto']:,} | Total: ${datos_financieros['total']:,}")
#         print("-" * 66)