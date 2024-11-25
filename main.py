import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import io
from lex import analizador, analizar
from sin import parser, graficar_arbol
from PIL import Image, ImageTk

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Lenguajes")
        self.root.geometry("1700x800")

        # Frame principal con bordes
        main_frame = ttk.Frame(root, padding="5")
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Dividir en sección superior e inferior
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=4)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Dividir sección superior en izquierda, centro y derecha
        left_frame = ttk.LabelFrame(top_frame, text="Entrada de Código", padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        center_frame = ttk.LabelFrame(top_frame, text="Resultados del Análisis", padding="5")
        center_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 5))
        right_frame = ttk.LabelFrame(top_frame, text="Árbol Sintáctico", padding="5")
        right_frame.grid(row=0, column=2, sticky="nsew")

        # Ajustar pesos de las columnas para distribuir espacio
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=4)
        top_frame.grid_columnconfigure(2, weight=5)
        top_frame.grid_rowconfigure(0, weight=1)

        # Prevenir propagación automática
        left_frame.grid_propagate(False)
        center_frame.grid_propagate(False)
        right_frame.grid_propagate(False)

        # Área de texto para código con fondo blanco
        self.code_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD,
                                                   width=40, bg="white", fg="black",
                                                   font=("Consolas", 11))
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Área de texto para resultados con fondo blanco
        self.output_text = scrolledtext.ScrolledText(center_frame, wrap=tk.WORD,
                                                     width=60, bg="white", fg="black",
                                                     font=("Consolas", 11))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Canvas para mostrar imágenes
        self.image_canvas = tk.Canvas(right_frame, bg="white", width=600, height=400)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # Frame inferior para mensajes del sistema
        system_frame = ttk.LabelFrame(bottom_frame, text="Mensajes del Sistema", padding="5")
        system_frame.pack(fill=tk.BOTH, expand=True)

        # Área de texto para mensajes del sistema
        self.system_text = scrolledtext.ScrolledText(system_frame, wrap=tk.WORD,
                                                     height=6, bg="white", fg="black",
                                                     font=("Consolas", 10))
        self.system_text.pack(fill=tk.BOTH, expand=True)

        # Frame para botones en la parte inferior
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # Definir estilos de botones
        button_styles = [
            ("Cargar Archivo", self.load_file, "#007acc", "white"),
            ("Análisis Léxico", self.analisis_lexico, "#28a745", "white"),
            ("Análisis Sintáctico", self.analisis_sintactico, "#ffa500", "white"),
            ("Generar Árbol", self.generar_arbol, "#dc3545", "white")
        ]

        # Crear botones con los estilos definidos
        for text, command, bg_color, fg_color in button_styles:
            self.create_button(buttons_frame, text, command, bg_color, fg_color)

        # Redireccionar stdout
        self.stdout_redirector = io.StringIO()
        self.original_stdout = sys.stdout

    def create_button(self, parent, text, command, bg_color, fg_color):
        """Crear botón con estilo personalizado"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=self.adjust_color(bg_color, -20),
            activeforeground=fg_color,
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            padx=20,
            pady=8
        )
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Bind hover events
        btn.bind("<Enter>", lambda e: e.widget.config(
            bg=self.adjust_color(bg_color, -20)))
        btn.bind("<Leave>", lambda e: e.widget.config(
            bg=bg_color))

        return btn

    def adjust_color(self, color, amount):
        """Ajustar el color para efectos hover"""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))

        return f"#{r:02x}{g:02x}{b:02x}"

    def redirect_stdout(self):
        sys.stdout = self.stdout_redirector
        self.stdout_redirector.seek(0)
        self.stdout_redirector.truncate()

    def restore_stdout(self):
        sys.stdout = self.original_stdout
        output = self.stdout_redirector.getvalue()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.system_text.insert(tk.END, "Análisis ejecutado correctamente.\n")
        self.system_text.see(tk.END)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_text.delete(1.0, tk.END)
                    self.code_text.insert(tk.END, content)
                self.system_text.insert(tk.END, f"Archivo cargado: {file_path}\n")
                self.system_text.see(tk.END)
            except Exception as e:
                self.system_text.insert(tk.END, f"Error al cargar el archivo: {str(e)}\n")

    def analisis_lexico(self):
        try:
            codigo = self.code_text.get(1.0, tk.END)
            self.redirect_stdout()
            analizar(codigo)
            self.restore_stdout()
        except Exception as e:
            self.restore_stdout()
            self.system_text.insert(tk.END, f"Error en el análisis léxico: {str(e)}\n")
            self.system_text.see(tk.END)

    def analisis_sintactico(self):
        try:
            codigo = self.code_text.get(1.0, tk.END)
            self.redirect_stdout()
            analizador.lineno = 1
            analizador.line_start = 0
            arbol = parser.parse(codigo, lexer=analizador)
            if arbol:
                pass
            else:
                print("No se pudo construir el árbol sintáctico.")
            self.restore_stdout()
        except Exception as e:
            self.restore_stdout()
            self.system_text.insert(tk.END, f"Error en el análisis sintáctico: {str(e)}\n")
            self.system_text.see(tk.END)

    def generar_arbol(self):
        try:
            codigo = self.code_text.get(1.0, tk.END)
            self.redirect_stdout()
            analizador.lineno = 1
            analizador.line_start = 0
            arbol = parser.parse(codigo, lexer=analizador)
            if arbol:
                dot = graficar_arbol(arbol)
                dot_path = 'arbol_sintactico.dot'
                output_path = dot.render(dot_path, format='png', cleanup=False)

                with open(dot_path, 'r', encoding='utf-8') as file:
                    dot_content = file.read()
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, f"=== Contenido de {dot_path} ===\n")
                    self.output_text.insert(tk.END, dot_content)

                self.show_image_in_canvas(output_path)
            else:
                print("No se pudo construir el árbol sintáctico.")
            self.restore_stdout()
        except Exception as e:
            self.restore_stdout()
            self.system_text.insert(tk.END, f"Error al generar el árbol: {str(e)}\n")
            self.system_text.see(tk.END)

    def show_image_in_canvas(self, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            self.image_tk = ImageTk.PhotoImage(img)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(200, 200, image=self.image_tk, anchor=tk.CENTER)
            self.system_text.insert(tk.END, f"Imagen mostrada en el Canvas: {image_path}\n")
            self.system_text.see(tk.END)
        except Exception as e:
            self.system_text.insert(tk.END, f"Error al mostrar la imagen en el Canvas: {str(e)}\n")
            self.system_text.see(tk.END)


def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()