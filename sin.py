import ply.yacc as yacc
from lex import tokens, analizador
from graphviz import Digraph

# Lista global para almacenar mensajes de error
errores_sintacticos = []

def guardar_mensaje_error(mensaje):
    """Guarda el mensaje de error en una lista global"""
    errores_sintacticos.append(mensaje)

def guardar_errores_en_archivo():
    """Escribe los mensajes de error acumulados en un archivo"""
    ruta_archivo = "archivos_salida/errores.txt"
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as file:
            file.write("=== Lista de errores encontrados ===\n")
            for error in errores_sintacticos:
                file.write(f"{error}\n")        
    except Exception as e:
        print(f"Error al guardar el archivo de errores: {e}")

# Función para graficar el árbol sintáctico
def graficar_arbol(nodo, dot=None, parent=None):
    if dot is None:
        dot = Digraph(format='png')
        dot.attr(dpi='300')

    # Crear un nodo en el grafo para este Nodo
    etiqueta = f"{nodo.nombre}" + (f": {nodo.valor}" if nodo.valor else "")
    dot.node(str(id(nodo)), etiqueta)

    # Si hay un padre, conectar el padre con este nodo
    if parent:
        dot.edge(str(id(parent)), str(id(nodo)))

    # Recorrer los hijos y graficarlos
    for hijo in nodo.hijos:
        graficar_arbol(hijo, dot, nodo)

    return dot

class Nodo:
    def __init__(self, nombre, valor=None):
        self.nombre = nombre
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, hijo):
        if isinstance(hijo, Nodo):
            self.hijos.append(hijo)

    def imprimir(self, nivel=0):
        indentacion = "  " * nivel
        valor = f": {self.valor}" if self.valor else ""
        print(f"{indentacion}{self.nombre}{valor}")
        for hijo in self.hijos:
            hijo.imprimir(nivel + 1)

class ParserState:
    def __init__(self):
        self.error_found = False
        self.error_line = None
        self.error_message = None
    
    def set_error(self, line, message):
        # Solo guardar el primer error encontrado
        if not self.error_found:
            self.error_found = True
            self.error_line = line
            self.error_message = message
    
    def clear_error(self):
        self.error_found = False
        self.error_line = None
        self.error_message = None

# Crear una instancia global del estado del parser
parser_state = ParserState()

def reiniciar_parser():
    """Reinicia las variables del parser para un nuevo análisis."""
    global parser
    parser.error = False  # Reiniciar el indicador de errores
    parser_state.clear_error()  # Reiniciar el estado de errores del parser

# Definición de precedencia de operadores
precedence = (
    ('left', 'OR_COR', 'OR_LAR'),
    ('left', 'AND_COR', 'AND_LAR'),
    ('left', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DISTINTO'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
)

# Regla para <Programa>
def p_programa(p):
    '''Programa : PROGRAMA IDENTIFICADOR PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ Sentencias Terminar LLAVE_DER'''
    print(f"Línea {p.lineno(8)}: Programa '{p[2]}' procesado correctamente.")
    nodo = Nodo("Programa", p[2])  
    nodo.agregar_hijo(p[6])
    nodo.agregar_hijo(p[7])
    p[0] = nodo

def p_sentencias_vacia(p):
    '''Sentencias : '''
    p[0] = Nodo("Sentencias")  

# Regla para <Sentencias>
def p_sentencias_unica(p):
    '''Sentencias : Sentencia'''
    nodo = Nodo("Sentencias")
    nodo.agregar_hijo(p[1])
    p[0] = nodo

# Regla para <Sentencias>
def p_sentencias_multiples(p):
    '''Sentencias : Sentencias Sentencia'''
    p[1].agregar_hijo(p[2])
    p[0] = p[1]

def p_sentencia_declaracion(p):
    '''Sentencia : Declaracion'''
    p[0] = p[1]

def p_sentencia_asignacion(p):
    '''Sentencia : Asignacion'''
    p[0] = p[1]

def p_sentencia_imprimir(p):
    '''Sentencia : Imprimir'''
    p[0] = p[1]

def p_sentencia_leer(p):
    '''Sentencia : Leer'''
    p[0] = p[1]

def p_sentencia_mientras(p):
    '''Sentencia : Mientras'''
    p[0] = p[1]

def p_sentencia_si(p):
    '''Sentencia : Si'''
    p[0] = p[1]

# Regla para <Leer>
def p_leer(p):
    '''Leer : LEER IDENTIFICADOR PUNTO_Y_COMA'''
    print(f"Línea {p.lineno(2)}: Leer variable '{p[2]}'")
    nodo = Nodo("Leer")
    nodo.agregar_hijo(Nodo("Variable", p[2]))
    p[0] = nodo

# Regla para <Imprimir>
def p_imprimir(p):
    '''Imprimir : IMPRIMIR PARENTESIS_IZQ ContenidoImprimir PARENTESIS_DER PUNTO_Y_COMA'''
    print(f"Línea {p.lineno(1)}: Imprimir con contenido: {p[3]}")
    nodo = Nodo("Imprimir")
    for item in p[3]:
        nodo.agregar_hijo(Nodo("Contenido", item))
    p[0] = nodo

def p_imprimir_error_falta_punto_y_coma(p):
    '''Imprimir : IMPRIMIR PARENTESIS_IZQ ContenidoImprimir PARENTESIS_DER error'''
    mensaje_error = f"Error de sintaxis: Se esperaba un punto y coma después de 'imprimir' en línea {p.lineno(1)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)  # Marcar error en el estado global

def p_imprimir_error_argumentos(p):
    '''Imprimir : IMPRIMIR PARENTESIS_IZQ error PARENTESIS_DER PUNTO_Y_COMA'''
    mensaje_error = f"Error de sintaxis: Argumentos no válidos en 'imprimir' en línea {p.lineno(3)}. Verifica el contenido."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(3), mensaje_error)

# Regla para <ContenidoImprimir>
def p_contenido_imprimir_texto(p):
    '''ContenidoImprimir : TEXTO'''
    p[0] = [p[1]]

def p_contenido_imprimir_variable(p):
    '''ContenidoImprimir : IDENTIFICADOR'''
    p[0] = [p[1]]

def p_contenido_imprimir_multiples(p):
    '''ContenidoImprimir : ContenidoImprimir COMA ContenidoImprimir'''
    p[0] = p[1] + p[3]

# Regla para <Declaracion>
def p_declaracion_simple(p):
    '''Declaracion : Tipo ListaIdentificadores PUNTO_Y_COMA'''
    print(f"Línea {p.lineno(3)}: Declaración de variables '{p[1].valor}': {', '.join(p[2])}")
    nodo = Nodo("Declaracion", p[1].valor)
    for identificador in p[2]:
        nodo.agregar_hijo(Nodo("Variable", identificador))
    p[0] = nodo

def p_declaracion_asignacion(p):
    '''Declaracion : Tipo IDENTIFICADOR IGUAL Expresion PUNTO_Y_COMA'''
    print(f"Línea {p.lineno(2)}: Declaración con asignación ({p[1].valor}): {p[2]} = {p[4].valor}")
    nodo = Nodo("Declaracion y Asignacion", p[1].valor)
    nodo.agregar_hijo(Nodo("Variable", p[2]))
    nodo.agregar_hijo(p[4])
    p[0] = nodo

def p_declaracion_error_identificador(p):
    '''Declaracion : Tipo error PUNTO_Y_COMA'''
    mensaje_error = f"Error de sintaxis: Identificadores no válidos en declaración en línea {p.lineno(2)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(2), mensaje_error)

def p_declaracion_error_punto_y_coma(p):
    '''Declaracion : Tipo IDENTIFICADOR error'''
    mensaje_error = f"Error de sintaxis: Se esperaba un punto y coma al final de la línea {p.lineno(2)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(2), mensaje_error)

# Regla para <Tipo>
def p_tipo(p):
    '''Tipo : INT
            | FLOAT
            | CHAR'''
    p[0] = Nodo("Tipo", p[1])

# Regla para <ListaIdentificadores>
def p_lista_identificadores_unico(p):
    '''ListaIdentificadores : IDENTIFICADOR'''
    p[0] = [p[1]]

def p_lista_identificadores_multiples(p):
    '''ListaIdentificadores : ListaIdentificadores COMA IDENTIFICADOR'''
    p[0] = p[1] + [p[3]]

# Regla para <Asignacion>
def p_asignacion(p):
    '''Asignacion : IDENTIFICADOR IGUAL Expresion PUNTO_Y_COMA'''
    print(f"Línea {p.lineno(1)}: Asignación: {p[1]} = {p[3].valor}")
    nodo = Nodo("Asignacion", p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_asignacion_error_identificador(p):
    '''Asignacion : error IGUAL Expresion PUNTO_Y_COMA'''
    mensaje_error = f"Error de sintaxis: Identificador no válido en línea {p.lineno(1)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)

def p_asignacion_error_faltante(p):
    '''Asignacion : IDENTIFICADOR IGUAL error PUNTO_Y_COMA'''
    mensaje_error = f"Error de sintaxis: Valor faltante en asignación en línea {p.lineno(2)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(2), mensaje_error)

# Regla para <Expresion>
def p_expresion_numero(p):
    '''Expresion : NUMERO'''
    p[0] = Nodo("Numero", p[1])

def p_expresion_identificador(p):
    '''Expresion : IDENTIFICADOR'''
    p[0] = Nodo("Variable", p[1])

def p_expresion_suma(p):
    '''Expresion : Expresion SUMA Expresion'''
    descripcion = f"{p[1].valor} + {p[3].valor}"  # Representación textual
    nodo = Nodo("Suma", descripcion)  # Incluye la descripción como valor del nodo
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_resta(p):
    '''Expresion : Expresion RESTA Expresion'''
    descripcion = f"{p[1].valor} - {p[3].valor}"
    nodo = Nodo("Resta", descripcion)
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_multiplicacion(p):
    '''Expresion : Expresion MULTIPLICACION Expresion'''
    descripcion = f"{p[1].valor} * {p[3].valor}"
    nodo = Nodo("Multiplicacion", descripcion)
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_division(p):
    '''Expresion : Expresion DIVISION Expresion'''
    descripcion = f"{p[1].valor} / {p[3].valor}"
    nodo = Nodo("Division", descripcion)
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_error_operador(p):
    '''Expresion : error SUMA Expresion
                 | Expresion SUMA error
                 | error RESTA Expresion
                 | Expresion RESTA error
                 | error MULTIPLICACION Expresion
                 | Expresion MULTIPLICACION error
                 | error DIVISION Expresion
                 | Expresion DIVISION error'''
    mensaje_error = f"Error de sintaxis: Operación errónea en línea {p.lineno(2)}. Falta un operando."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(2), mensaje_error)

# Regla para <Mientras>
def p_mientras(p):
    '''Mientras : MIENTRAS PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Líneas {p.lineno(1)}-{p.lineno(7)}: Bloque 'mientras' procesado con condición: {p[3].valor}")
    nodo = Nodo("Mientras")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    p[0] = nodo

def p_mientras_error(p):
    '''Mientras : MIENTRAS PARENTESIS_IZQ error PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    mensaje_error = f"Error de sintaxis en la condición del bloque 'mientras' en línea {p.lineno(1)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)  # Marcar error en el estado global

# Regla para <Si>
def p_si(p):
    '''Si : SI PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Líneas {p.lineno(1)}-{p.lineno(7)}: Estructura 'si' procesada con condición: {p[3].valor}")
    nodo = Nodo("Si")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    p[0] = nodo

def p_si_error_incompleto(p):
    '''Si : SI PARENTESIS_IZQ error PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    mensaje_error = f"Error de sintaxis: Condición mal formada en 'si' en línea {p.lineno(3)}. Verifica la condición."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(3), mensaje_error)

def p_si_sino(p):
    '''Si : SI PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER SINO LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Líneas {p.lineno(1)}-{p.lineno(11)}: Estructura 'si-sino' procesada con condición: {p[3].valor}")
    nodo = Nodo("Si-Sino")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    nodo.agregar_hijo(p[10])
    p[0] = nodo

def p_si_sino_error(p):
    '''Si : SINO LLAVE_IZQ Sentencias LLAVE_DER'''
    mensaje_error = f"Error de sintaxis: 'sino' no puede existir sin un bloque 'si' en línea {p.lineno(1)}."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)

# Regla para <Condicion>
def p_condicion_comparacion(p):
    '''Condicion : Expresion MENOR Expresion
                 | Expresion MENOR_IGUAL Expresion
                 | Expresion MAYOR Expresion
                 | Expresion MAYOR_IGUAL Expresion
                 | Expresion IGUAL_IGUAL Expresion
                 | Expresion DISTINTO Expresion'''
    descripcion = f"{p[1].valor} {p[2]} {p[3].valor}" 
    nodo = Nodo("Condicion", descripcion)
    nodo.agregar_hijo(p[1])  
    nodo.agregar_hijo(p[3])  
    p[0] = nodo

def p_condicion_logica(p):
    '''Condicion : Condicion AND_COR Condicion
                 | Condicion AND_LAR Condicion
                 | Condicion OR_COR Condicion
                 | Condicion OR_LAR Condicion'''
    nodo = Nodo("Condicion Logica", p[2])
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_condicion_error_operador(p):
    '''Condicion : Expresion MENOR error'''
    mensaje_error = f"Error de sintaxis: Condición errónea en línea {p.lineno(2)}. Verifica los operandos."
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)

# Regla para <Terminar>
def p_terminar(p):
    '''Terminar : TERMINAR PUNTO_Y_COMA'''
    columna = calcular_columna(p.slice[1], analizador)
    print(f"Línea {p.lineno(1)}: Instrucción 'terminar'")
    nodo = Nodo("Terminar")
    p[0] = nodo

def p_error_terminar_punto_y_coma(p):
    '''Terminar : TERMINAR error'''
    mensaje_error = f"Error de sintaxis: Se esperaba un punto y coma al final de la línea {p.lineno(1)}"
    print(mensaje_error)
    guardar_mensaje_error(mensaje_error)
    parser_state.set_error(p.lineno(1), mensaje_error)  # Marcar error

def calcular_columna(p, lexer):
    line_start = lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
    return (p.lexpos - line_start) + 1

# Manejo de errores
def p_error(p):
    if p:
        # Sincronización general si no se alcanzó una regla específica
        while True:
            tok = parser.token()  # Obtener el siguiente token
            if not tok or tok.type in ('PUNTO_Y_COMA', 'LLAVE_DER'):
                break  # Sincronizar con tokens seguros
    else:
        # Error al final del archivo
        guardar_mensaje_error("Error de sintaxis: fin inesperado del archivo.")
        parser.error = True

def parse(input_text):
    parser_state.clear_error()  # Limpiar el estado de errores
    result = parser.parse(input_text)  # Ejecutar el parser

    # Mostrar resultado del análisis
    if parser_state.error_found:
        print(f"Análisis sintáctico finalizado con errores. Último error: {parser_state.error_message}")
    else:
        print("El análisis sintáctico finalizó correctamente.")

    return result

# Construir el parser
parser = yacc.yacc()