import ply.lex as lex

# Palabras reservadas
reservadas = {
    'imprimir': 'IMPRIMIR',
    'leer': 'LEER',
    'mientras': 'MIENTRAS',
    'programa': 'PROGRAMA',
    'si': 'SI',
    'sino': 'SINO',
    'terminar': 'TERMINAR',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR'
}

# Tokens
tokens = [
    'IDENTIFICADOR', 'PARENTESIS_IZQ', 'PARENTESIS_DER', 'LLAVE_IZQ', 'LLAVE_DER', 'PUNTO_Y_COMA', 'COMA',
    'NUMERO', 'IGUAL', 'CARACTER', 'FLOTANTE', 'TEXTO', 'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 'AND_COR',
    'AND_LAR', 'OR_COR', 'OR_LAR', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DISTINTO'
] + list(reservadas.values())

# Reglas para tokens simples
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_PUNTO_Y_COMA = r';'
t_COMA = r','
t_IGUAL = r'='
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_AND_COR = r'&&'
t_AND_LAR = r'and'
t_OR_COR = r'\|\|'
t_OR_LAR = r'or'
t_MENOR = r'<'
t_MENOR_IGUAL = r'<='
t_MAYOR = r'>'
t_MAYOR_IGUAL = r'>='
t_IGUAL_IGUAL = r'=='
t_DISTINTO = r'!='

# Reglas avanzadas para tokens específicos
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value.lower(), 'IDENTIFICADOR')
    return t

def t_NUMERO(t):
    r'\b\d+\b'
    t.value = int(t.value)
    return t

def t_FLOTANTE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CARACTER(t):
    r"'([^'\n])'"
    t.value = t.value[1:-1]
    return t

def t_TEXTO(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # Incrementar número de línea
    t.lexer.line_start = t.lexpos  # Actualizar el inicio de la nueva línea

# Ignorar espacios y tabulaciones
t_ignore = ' \t\r'

# Manejo de comentarios
def t_COMMENT(t):
    r'\#[^\n]*'
    pass

# Manejo de errores
def t_error(t):
    column = calcular_columna(t, t.lexer)
    print(f"Error léxico: Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}, columna {column}.")
    t.lexer.skip(1)

# Funciones auxiliares
def calcular_columna(t, lexer):
    line_start = lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
    return (t.lexpos - line_start) + 1  # Calcula la columna correctamente

# Crear el analizador
analizador = lex.lex()

# Inicializar variables del lexer
analizador.line_start = 0

# Función principal de análisis
def analizar(texto):
    analizador.lineno = 1  # Reinicia el número de línea
    analizador.line_start = 0  # Reinicia el inicio de la línea
    analizador.input(texto)
    print("\n=== Análisis Léxico ===\n")
    print("TOKEN            VALOR           LÍNEA            COLUMNA")
    print("-" * 50)
    while True:
        tok = analizador.token()
        if not tok:
            break
        tipo = tok.type.ljust(15)
        valor = str(tok.value).ljust(15)
        linea = str(tok.lineno).ljust(4)
        columna = str(calcular_columna(tok, analizador)).ljust(4)
        print(f"Token: {tipo} Valor: {valor} Línea: {linea} Columna: {columna}")