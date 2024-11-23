import codecs
from lex import analizador, analizar
from sin import parser, graficar_arbol

def main():
    # Ruta del archivo de prueba
    archivo = "./test/test.txt"

    try:
        # Leer el contenido del archivo
        with codecs.open(archivo, "r", "utf-8") as fp:
            cadena = fp.read()

        # Análisis Léxico con formato mejorado
        analizar(cadena)

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
            
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{archivo}'")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()