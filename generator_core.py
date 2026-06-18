import json
import random
from datetime import datetime, timedelta

class DataGenerator:
    """
    Componente central encargado de la síntesis y consistencia semántica de datos.

    Esta clase expone métodos modulares para generar atributos individuales de negocio
    (nombres coherentes por género, identificaciones, correos unívocos, direcciones complejas
    y transacciones financieras) basándose en colecciones de recursos cargadas desde un archivo JSON.
    """

    def __init__(self, json_path="datos_json/data_source.json"):
        """
        Inicializa el motor generador cargando el archivo de recursos en memoria.

        Args:
            json_path (str): Ruta relativa o absoluta hacia el archivo JSON de configuración.
        """
        with open(json_path, "r", encoding="utf-8") as f:
            self.source = json.load(f)

    def generar_genero_y_nombre(self):
        """
        Determina un género biológico aleatorio y extrae un nombre de pila coherente.

        Returns:
            tuple: Un par que contiene (nombre [str], genero [str]).
        """
        genero = random.choice(["Masculino", "Femenino"])
        if genero == "Masculino":
            nombre = random.choice(self.source["nombres"]["masculinos"])
        else:
            nombre = random.choice(self.source["nombres"]["femeninos"])
        return nombre, genero

    def generar_apellido(self):
        """
        Extrae un apellido aleatorio de la base de recursos distribuidos.

        Returns:
            str: Un apellido común latinoamericano.
        """
        return random.choice(self.source["apellidos"])

    def generar_correo(self, nombre, apellido):
        """
        Estructura una dirección de correo electrónico normalizada y pseudo-aleatoria.

        Normaliza las cadenas eliminando caracteres diacríticos (tildes) y añade un
        sufijo numérico variable para mitigar colisiones y garantizar restricciones de unicidad.

        Args:
            nombre (str): Nombre de pila del usuario objetivo.
            apellido (str): Apellido del usuario objetivo.

        Returns:
            str: Dirección de correo electrónico completamente sanitizada y formateada.
        """
        dominios = [item["dominio"] for item in self.source["correos"]]
        pesos = [item["peso"] for item in self.source["correos"]]
        dominio_elegido = random.choices(dominios, weights=pesos, k=1)[0]
        
        nombre_limpio = nombre.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        apellido_limpio = apellido.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        
        sufijo_numerico = random.randint(10, 999)
        
        formato = random.choice([
            f"{nombre_limpio}.{apellido_limpio}{sufijo_numerico}", 
            f"{nombre_limpio[0]}{apellido_limpio}{sufijo_numerico}"
        ])
        
        return f"{formato}@{dominio_elegido}"

    def generar_documento(self):
        """
        Selecciona un tipo de identificación oficial y genera un número estructurado real.

        Utiliza una distribución ponderada según el tipo de documento (Cédula, NIT, Pasaporte)
        y aplica máscaras alfanuméricas complejas de longitud variable según corresponda.

        Returns:
            dict: Un mapa con las llaves 'tipo_documento' (str) y 'numero_documento' (str).
        """
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

    def generar_fecha(self, dias_atras_max=365, formato="YYYY-MM-DD"):
        """
        Calcula un punto en el tiempo aleatorio desplazado hacia el pasado.

        Args:
            dias_atras_max (int, opcional): El límite máximo de días del intervalo retrospectivo.
            formato (str, opcional): Máscara visual deseada para el string de salida.
                Soporta 'DD/MM/YYYY', 'MM/DD/YYYY' e ISO estándar por defecto.

        Returns:
            str: Representación textual de la fecha calculada bajo el formato solicitado.
        """
        dias_aleatorios = random.randint(0, dias_atras_max)
        fecha_calculada = datetime.now() - timedelta(days=dias_aleatorios)
        
        if formato == "DD/MM/YYYY":
            return fecha_calculada.strftime("%d/%m/%Y")
        elif formato == "MM/DD/YYYY":
            return fecha_calculada.strftime("%m/%d/%Y")
        else:
            return fecha_calculada.strftime("%Y-%m-%d")

    def generar_importe_transaccion(self, min_valor=10000, max_valor=5000000, tax=False, tax_rate=0.19):
        """
        Ejecuta la simulación de un cobro financiero aplicando cálculos fiscales.

        Genera una distribución uniforme de valores numéricos de punto flotante
        y desglosa los componentes contables en caso de requerir retenciones impositivas.

        Args:
            min_valor (int/float, opcional): Cota mínima del importe transaccional.
            max_valor (int/float, opcional): Cota máxima del importe transaccional.
            tax (bool, opcional): Flag para activar el cálculo de impuestos comerciales.
            tax_rate (float, opcional): Alícuota aplicable (ej. 0.19 correspondiente al 19% de IVA).

        Returns:
            dict: Estructura financiera con llaves 'subtotal' (float), 'impuesto' (float) y 'total' (float).
        """
        importe_base = round(random.uniform(min_valor, max_valor), 2)
        
        resultado = {
            "subtotal": importe_base,
            "impuesto": 0.0,
            "total": importe_base
        }
        
        if tax:
            resultado["impuesto"] = round(importe_base * tax_rate, 2)
            resultado["total"] = round(resultado["subtotal"] + resultado["impuesto"], 2)
            
        return resultado

    def generar_direccion(self):
        """
        Ensambla de forma procedimental una nomenclatura de dirección urbana residencial o comercial.

        Implementa un flujo de validación jerárquica: si se selecciona una estructura de tipo contenedor
        (como una Torre, Interior o Bloque), obliga algorítmicamente al motor a anidar un destino
        final (Apartamento, Oficina o Consultorio) con el fin de evitar registros truncados e inválidos.

        Returns:
            str: Una dirección catastral estructurada y consistente.
        """
        nom = self.source["nomenclaturas"]
        
        via_principal = random.choice(nom["vias_principales"])
        
        num1 = random.randint(1, 150)
        letra1 = f" {random.choice(nom['vias_secundarias_y_complementos'])}" if random.random() < 0.4 else ""
        
        num2 = random.randint(1, 99)
        letra2 = f"{random.choice(['A', 'B', 'C', 'D']).lower()}" if random.random() < 0.25 else ""
        num3 = random.randint(1, 99)
        
        direccion_base = f"{via_principal} {num1}{letra1} # {num2}{letra2} - {num3}"
        
        if random.random() < 0.50:
            tipo_inmueble = random.choice(nom["tipos_de_inmueble"])
            
            if tipo_inmueble in ["Torre", "Bloque", "Interior"]:
                num_contenedor = random.randint(1, 15)
                sub_inmueble = random.choice(["Apartamento", "Oficina", "Consultorio"])
                num_final = random.randint(101, 1205) 
                
                direccion_base += f" {tipo_inmueble} {num_contenedor} {sub_inmueble} {num_final}"
            
            else:
                if tipo_inmueble in ["Apartamento", "Oficina", "Consultorio"]:
                    num_inmueble = random.randint(101, 505) 
                else:
                    num_inmueble = random.randint(1, 5)
                    
                direccion_base += f" {tipo_inmueble} {num_inmueble}"
                
        return direccion_base
    
    def generar_celular(self):
        """
        Construye una línea de telefonía celular móvil simulada.

        Garantiza consistencia regional utilizando exclusivamente prefijos asignados y activos
        dentro de los rangos de telecomunicaciones de Colombia.

        Returns:
            str: Una cadena numérica de 10 dígitos que emula un terminal móvil celular.
        """
        prefijo = random.choice(self.source["prefijos_celular"])
        cuerpo = "".join(str(random.choice(self.source["alfanumerico"]["numeros"])) for _ in range(7))
        return f"{prefijo}{cuerpo}"

    def generar_metodo_pago(self):
        """
        Determina una pasarela o medio de pago mercantil.

        Returns:
            str: Nombre de la modalidad de pago calculada estadísticamente.
        """
        metodos = [item["metodo"] for item in self.source["metodos_pago"]]
        pesos = [item["peso"] for item in self.source["metodos_pago"]]
        return random.choices(metodos, weights=pesos, k=1)[0]

    def generar_flag_boolean(self, modo_sucio=False):
        """
        Calcula estados binarios booleanos de control de procesos.

        Args:
            modo_sucio (bool, opcional): Determina si se corrompe intencionalmente el formato.
                Si es True, transforma los tipos booleanos estrictos en variantes textuales asíncronas
                para emular fallos de calidad de datos en bases estructuradas.

        Returns:
            bool/str: Valor booleano nativo o representación textual alterada de la bandera.
        """
        valor_base = random.choice([True, False])
        
        if not modo_sucio:
            return valor_base
        else:
            if valor_base:
                return random.choice(["true", "1", "S", "SI", "True"])
            else:
                return random.choice(["false", "0", "N", "NO", "False"])