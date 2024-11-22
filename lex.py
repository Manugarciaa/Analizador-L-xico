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

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t

def t_FLOTANTE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CARACTER(t):
    r"'[^']*'"
    if len(t.value) != 3:
        print(f"Error léxico: Literal de CHAR inválido '{t.value}' en línea {t.lexer.lineno}")
        t.lexer.skip(len(t.value))  # Salta todo el literal inválido
        return None
    t.value = t.value[1]  # Extrae el carácter central
    return t

def t_TEXTO(t):
    r'\"([^\\"]|\\.)*\"'
    t.value = t.value[1:-1]
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\#.*'
    pass  # Ignorar comentarios

def t_error(t):
    print(f"Error léxico: Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}, posición {t.lexpos}")
    t.lexer.skip(1)

analizador = lex.lex()