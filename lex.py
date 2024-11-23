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
def t_INVALIDO_NUMERO_IDENTIFICADOR(t):
    r'\d+[a-zA-Z_][a-zA-Z0-9_]*'
    column = calcular_columna(t, t.lexer)
    print(f"Error léxico: Identificador inválido '{t.value}' en línea {t.lexer.lineno}, columna {column} - Los identificadores no pueden comenzar con números.")
    
    i = 0
    while i < len(t.value):
        char = t.value[i]
        if char in ",;":
            t.type = 'COMA' if char == ',' else 'PUNTO_Y_COMA'
            t.value = char
            t.lexpos = t.lexpos + i
            t.lexer.skip(i + 1)
            return t
        i += 1

    # Verificar caracteres inmediatamente después del token
    if t.lexer.lexpos < len(t.lexer.lexdata):
        siguiente = t.lexer.lexdata[t.lexer.lexpos]
        if siguiente in ",;":
            t.type = 'COMA' if siguiente == ',' else 'PUNTO_Y_COMA'
            t.value = siguiente
            t.lexpos = t.lexer.lexpos 
            t.lexer.skip(1)
            return t

    # Avanzar el lexer completamente si no hay separadores
    t.lexer.skip(len(t.value))

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value.lower(), 'IDENTIFICADOR')
    return t

# Manejo de números mal formados
def t_INVALIDO_NUMERO(t):
    r'\d+\.\.+\d*|\d+\.\.$|\.\d+\.\d*'
    column = calcular_columna(t, t.lexer)
    print(f"Error léxico: Número mal formado '{t.value}' en línea {t.lexer.lineno}, columna {column}.")
    t.lexer.skip(len(t.value))  # Saltar toda la secuencia inválida

# Manejo de números enteros válidos
def t_NUMERO(t):
    r'\b\d+\b'
    t.value = int(t.value)
    return t

# Manejo de números flotantes válidos
def t_FLOTANTE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CARACTER(t):
    r"'([^'\n])'"
    t.value = t.value[1:-1]
    return t

def t_INVALIDO_CARACTER(t):
    r"'[^'\n]*'"  # Detecta cualquier cosa entre comillas simples (incluidos casos inválidos)
    column = calcular_columna(t, t.lexer)

    # Limpieza del valor para evitar incluir saltos de línea en el mensaje
    valor_limpio = t.value.replace('\n', '\\n')

    # Identificar el tipo de error
    if '\n' in t.value:
        print(f"Error léxico: Literal de carácter no cerrado en línea {t.lexer.lineno}, columna {column}.")
    elif len(t.value) > 3:
        print(f"Error léxico: Literal de carácter inválido '{valor_limpio}' en línea {t.lexer.lineno}, columna {column} - Solo un carácter permitido.")
    else:
        print(f"Error léxico: Literal de carácter inválido '{valor_limpio}' en línea {t.lexer.lineno}, columna {column} - Falta el cierre o está vacío.")

    # Procesar separadores después del literal inválido
    if t.lexer.lexpos < len(t.lexer.lexdata):
        siguiente = t.lexer.lexdata[t.lexer.lexpos]
        if siguiente in ",;":
            t.type = 'COMA' if siguiente == ',' else 'PUNTO_Y_COMA'
            t.value = siguiente
            t.lexer.skip(1)
            return t

    # Avanzar completamente si no hay separadores
    t.lexer.skip(len(t.value))

def t_TEXTO(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t\r'
def t_COMMENT(t):
    r'\#[^\n]*'
    pass

def t_INVALIDO_OPERADOR(t):
    r'([+\-*/&|^!]{2,}|\*\*|&{3,}|[+\-*/&|^!]=+)'
    column = calcular_columna(t, t.lexer)
    print(f"Error léxico: Operador inválido '{t.value}' en línea {t.lexer.lineno}, columna {column}.")
    t.lexer.skip(len(t.value))

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.line_start = t.lexpos

# Manejo general de errores
def t_error(t):
    column = calcular_columna(t, t.lexer)
    print(f"Error léxico: Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}, columna {column}.")
    t.lexer.skip(1)

# Funciones auxiliares
def calcular_columna(t, lexer):
    line_start = lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
    return t.lexpos - line_start

# Crear el analizador
analizador = lex.lex()

# Función principal de análisis
def analizar(texto):
    analizador.lineno = 1
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