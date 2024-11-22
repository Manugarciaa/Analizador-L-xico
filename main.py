import codecs
from lex import analizador
from sin import parser, graficar_arbol

# Ruta del archivo de prueba
archivo = "./test/test.txt"

# Leer el contenido del archivo
with codecs.open(archivo, "r", "utf-8") as fp:
    cadena = fp.read()

# Análisis Léxico
print("=== Análisis Léxico ===")
analizador.input(cadena)
while True:
    tok = analizador.token()
    if not tok:
        break
    print(tok)

# Análisis Sintáctico
print("\n=== Análisis Sintáctico ===")
arbol = parser.parse(cadena)
if arbol:
    print("\n=== Árbol Sintáctico ===")
    arbol.imprimir()

    print("\n=== Generando Gráfico del Árbol Sintáctico ===")
    dot = graficar_arbol(arbol)
    dot.render('arbol_sintactico', view=True)
    print("Gráfico guardado como 'arbol_sintactico.png'")
else:
    print("No se pudo construir el árbol sintáctico.")
