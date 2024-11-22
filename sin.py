import ply.yacc as yacc
from lex import tokens
from graphviz import Digraph

# Función para graficar el árbol sintáctico
def graficar_arbol(nodo, dot=None, parent=None):
    """
    Graficar el árbol sintáctico usando Graphviz.
    :param nodo: Nodo raíz del árbol a graficar.
    :param dot: Objeto Graphviz Digraph.
    :param parent: Nodo padre en el grafo.
    :return: Objeto Digraph con el árbol generado.
    """
    if dot is None:
        dot = Digraph(format='png')
        dot.attr(dpi='300')  # Opcional: Mejora la resolución

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
        else:
            raise ValueError("El hijo debe ser una instancia de Nodo.")

    def imprimir(self, nivel=0):
        indentacion = "  " * nivel
        valor = f": {self.valor}" if self.valor else ""
        print(f"{indentacion}{self.nombre}{valor}")
        for hijo in self.hijos:
            hijo.imprimir(nivel + 1)

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
    print(f"Programa '{p[2]}' procesado correctamente.")
    nodo = Nodo("Programa", p[2])  
    nodo.agregar_hijo(p[6])
    nodo.agregar_hijo(p[7])
    p[0] = nodo

# Regla para <Sentencias>
def p_sentencias_unica(p):
    '''Sentencias : Sentencia'''
    nodo = Nodo("Sentencias")
    nodo.agregar_hijo(p[1])
    p[0] = nodo

def p_sentencias_multiples(p):
    '''Sentencias : Sentencias Sentencia'''
    p[1].agregar_hijo(p[2])
    p[0] = p[1]

# Regla para <Sentencia>
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
    print(f"Leer: variable '{p[2]}'")
    nodo = Nodo("Leer")
    nodo.agregar_hijo(Nodo("Variable", p[2]))
    p[0] = nodo

# Regla para <Imprimir>
def p_imprimir(p):
    '''Imprimir : IMPRIMIR PARENTESIS_IZQ ContenidoImprimir PARENTESIS_DER PUNTO_Y_COMA'''
    print(f"Imprimir: {p[3]}")
    nodo = Nodo("Imprimir")
    for item in p[3]:
        nodo.agregar_hijo(Nodo("Contenido", item))
    p[0] = nodo

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
    print(f"Declaración de variables ({p[1].valor}): {', '.join(p[2])}")
    nodo = Nodo("Declaracion", p[1].valor)
    for identificador in p[2]:
        nodo.agregar_hijo(Nodo("Variable", identificador))
    p[0] = nodo

def p_declaracion_asignacion(p):
    '''Declaracion : Tipo IDENTIFICADOR IGUAL Expresion PUNTO_Y_COMA'''
    print(f"Declaración con asignación ({p[1].valor}): {p[2]} = {p[4].valor}")
    nodo = Nodo("Declaracion y Asignacion", p[1].valor)
    nodo.agregar_hijo(Nodo("Variable", p[2]))
    nodo.agregar_hijo(p[4])
    p[0] = nodo

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
    print(f"Asignación: {p[1]} = {p[3].valor}")
    nodo = Nodo("Asignacion", p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

# Regla para <Expresion>
def p_expresion_numero(p):
    '''Expresion : NUMERO'''
    print(f"Expresión detectada: {p[1]}")
    p[0] = Nodo("Numero", p[1])

def p_expresion_identificador(p):
    '''Expresion : IDENTIFICADOR'''
    print(f"Expresión detectada: Variable {p[1]}")
    p[0] = Nodo("Variable", p[1])

def p_expresion_suma(p):
    '''Expresion : Expresion SUMA Expresion'''
    print(f"Expresión detectada: {p[1].valor} + {p[3].valor}")
    nodo = Nodo("Suma")
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_resta(p):
    '''Expresion : Expresion RESTA Expresion'''
    print(f"Expresión detectada: {p[1].valor} - {p[3].valor}")
    nodo = Nodo("Resta")
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_multiplicacion(p):
    '''Expresion : Expresion MULTIPLICACION Expresion'''
    print(f"Expresión detectada: {p[1].valor} * {p[3].valor}")
    nodo = Nodo("Multiplicacion")
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

def p_expresion_division(p):
    '''Expresion : Expresion DIVISION Expresion'''
    print(f"Expresión detectada: {p[1].valor} / {p[3].valor}")
    nodo = Nodo("Division")
    nodo.agregar_hijo(p[1])
    nodo.agregar_hijo(p[3])
    p[0] = nodo

# Regla para <Mientras>
def p_mientras(p):
    '''Mientras : MIENTRAS PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Bloque mientras procesado con condición: {p[3].valor}")
    nodo = Nodo("Mientras")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    p[0] = nodo

# Regla para <Si>
def p_si(p):
    '''Si : SI PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Estructura si procesada con condición: {p[3].valor}")
    nodo = Nodo("Si")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    p[0] = nodo

def p_si_sino(p):
    '''Si : SI PARENTESIS_IZQ Condicion PARENTESIS_DER LLAVE_IZQ Sentencias LLAVE_DER SINO LLAVE_IZQ Sentencias LLAVE_DER'''
    print(f"Estructura si-sino procesada con condición: {p[3].valor}")
    nodo = Nodo("Si-Sino")
    nodo.agregar_hijo(p[3])
    nodo.agregar_hijo(p[6])
    nodo.agregar_hijo(p[10])
    p[0] = nodo

# Regla para <Condicion>
def p_condicion_comparacion(p):
    '''Condicion : Expresion MENOR Expresion
                 | Expresion MENOR_IGUAL Expresion
                 | Expresion MAYOR Expresion
                 | Expresion MAYOR_IGUAL Expresion
                 | Expresion IGUAL_IGUAL Expresion
                 | Expresion DISTINTO Expresion'''
    nodo = Nodo("Condicion", p[2])
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

# Regla para <Terminar>
def p_terminar(p):
    '''Terminar : TERMINAR PUNTO_Y_COMA'''
    p[0] = Nodo("Terminar")

# Manejo de errores
def p_error(p):
    if p:
        print(f"Error de sintaxis en token: {p.type} ('{p.value}') en línea {p.lineno}.")
    else:
        print("Error de sintaxis: fin inesperado del archivo.")

# Construir el parser
parser = yacc.yacc()