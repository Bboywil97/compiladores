import tkinter as tk
from tkinter import ttk, messagebox
import re
from tkinter import font as tkfont

class NodoArbol:
    def __init__(self, valor):
        self.valor = valor
        self.izquierdo = None
        self.derecho = None

class AnalizadorExpresiones:
    def __init__(self):
        # Definir prioridades de operadores
        self.prioridad = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    
    def es_operador(self, caracter):
        return caracter in '+-*/^'
    
    def es_mayor_prioridad(self, op1, op2):
        if op2 == '(' or op2 == ')':
            return False
        return self.prioridad.get(op1, 0) >= self.prioridad.get(op2, 0)
    
    def infix_a_postfix(self, expresion):
        tokens = self._tokenizar(expresion)
        resultado = []
        pila = []
        
        for token in tokens:
            if token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(':
                    resultado.append(pila.pop())
                if pila and pila[-1] == '(':
                    pila.pop()  # Descartar el paréntesis izquierdo
            elif self.es_operador(token):
                while pila and pila[-1] != '(' and self.es_mayor_prioridad(pila[-1], token):
                    resultado.append(pila.pop())
                pila.append(token)
            else:
                # Token es un operando
                resultado.append(token)
        
        # Vaciar la pila
        while pila:
            resultado.append(pila.pop())
            
        return resultado
    
    def infix_a_prefix(self, expresion):
        tokens = self._tokenizar(expresion)
        # Invertir la expresión y los paréntesis
        tokens_invertidos = []
        for token in reversed(tokens):
            if token == '(':
                tokens_invertidos.append(')')
            elif token == ')':
                tokens_invertidos.append('(')
            else:
                tokens_invertidos.append(token)
        
        # Convertir a postfija la expresión invertida
        postfija_invertida = []
        pila = []
        
        for token in tokens_invertidos:
            if token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(':
                    postfija_invertida.append(pila.pop())
                if pila and pila[-1] == '(':
                    pila.pop()
            elif self.es_operador(token):
                while (pila and pila[-1] != '(' and 
                       self.prioridad.get(token, 0) < self.prioridad.get(pila[-1], 0)):
                    postfija_invertida.append(pila.pop())
                pila.append(token)
            else:
                postfija_invertida.append(token)
                
        while pila:
            postfija_invertida.append(pila.pop())
            
        # Invertir el resultado para obtener la notación prefija
        return list(reversed(postfija_invertida))
    
    def construir_arbol(self, expresion):
        tokens = self.infix_a_postfix(expresion)
        pila = []
        
        for token in tokens:
            if not self.es_operador(token):
                pila.append(NodoArbol(token))
            else:
                nodo = NodoArbol(token)
                # Cuidado con el orden: el segundo operando sale primero
                nodo.derecho = pila.pop()
                nodo.izquierdo = pila.pop()
                pila.append(nodo)
                
        return pila[0] if pila else None
    
    def _tokenizar(self, expresion):
        # Eliminar espacios
        expresion = expresion.replace(' ', '')
        
        # Agregar espacios alrededor de operadores y paréntesis para facilitar la tokenización
        for simbolo in '+-*/^()':
            expresion = expresion.replace(simbolo, f' {simbolo} ')
        
        # Dividir en tokens y eliminar espacios vacíos
        tokens = [token for token in expresion.split() if token]
        return tokens
    
    def arbol_a_cadena(self, nodo, prefijo="", es_ultimo=True, es_raiz=True):
        if nodo is None:
            return ""
            
        # Para la raíz no mostramos líneas
        if es_raiz:
            resultado = nodo.valor + "\n"
        else:
            # Línea que conecta al nodo (├── o └──)
            conector = "└── " if es_ultimo else "├── "
            resultado = prefijo + conector + nodo.valor + "\n"
        
        # Prefijo para los hijos
        prefijo_hijos = prefijo
        if not es_raiz:
            prefijo_hijos += "    " if es_ultimo else "│   "
        
        # Procesar hijo izquierdo
        if nodo.izquierdo:
            tiene_hijo_derecho = nodo.derecho is not None
            resultado += self.arbol_a_cadena(nodo.izquierdo, prefijo_hijos, not tiene_hijo_derecho, False)
        
        # Procesar hijo derecho
        if nodo.derecho:
            resultado += self.arbol_a_cadena(nodo.derecho, prefijo_hijos, True, False)
            
        return resultado

class InterfazApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Expresiones Matemáticas")
        self.root.geometry("900x700")
        
        self.analizador = AnalizadorExpresiones()
        
        # Verificar si la fuente Consolas está disponible
        fuentes_disponibles = tkfont.families()
        self.fuente_mono = "Consolas" if "Consolas" in fuentes_disponibles else "Courier"
        
        # Configuración de la interfaz
        self.crear_widgets()
        
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Entrada de expresión
        ttk.Label(main_frame, text="Expresión matemática:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entrada_expr = ttk.Entry(main_frame, width=50)
        self.entrada_expr.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.entrada_expr.insert(0, "3 + 4 * 2 / ( 1 - 5 ) ^ 2")
        
        # Botón para analizar
        ttk.Button(main_frame, text="Analizar", command=self.analizar_expresion).grid(row=0, column=2, padx=5, pady=5)
        
        # Notebook para las diferentes representaciones
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W), pady=10)
        
        # Pestaña para notación polaca (prefija)
        self.frame_prefija = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_prefija, text="Notación Polaca (Prefija)")
        
        # Pestaña para notación polaca inversa (postfija)
        self.frame_postfija = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_postfija, text="Notación Polaca Inversa (Postfija)")
        
        # Pestaña para el árbol de expresiones
        self.frame_arbol = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_arbol, text="Árbol de Expresiones")
        
        # Áreas de texto para mostrar resultados
        self.texto_prefija = tk.Text(self.frame_prefija, height=20, width=80, wrap=tk.WORD)
        self.texto_prefija.pack(fill=tk.BOTH, expand=True)
        
        self.texto_postfija = tk.Text(self.frame_postfija, height=20, width=80, wrap=tk.WORD)
        self.texto_postfija.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para visualización gráfica del árbol
        self.canvas_frame = ttk.Frame(self.frame_arbol)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear canvas con scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        
        # Scrollbars para el canvas
        scrollbar_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Crear también área de texto para representación ASCII del árbol
        self.texto_arbol = tk.Text(self.notebook, height=20, width=80, wrap=tk.NONE, font=(self.fuente_mono, 11))
        scrollbar_texto = ttk.Scrollbar(self.notebook, orient="vertical", command=self.texto_arbol.yview)
        self.texto_arbol.configure(yscrollcommand=scrollbar_texto.set)
        
        # Añadir nueva pestaña para la vista de texto del árbol
        self.frame_texto_arbol = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_texto_arbol, text="Árbol (Texto)")
        
        scrollbar_texto.pack(side="right", fill="y")
        self.texto_arbol.pack(side="left", fill="both", expand=True)
        
        # Mover elementos al frame correcto
        self.texto_arbol.pack_forget()
        scrollbar_texto.pack_forget()
        
        self.texto_arbol.pack(in_=self.frame_texto_arbol, side="left", fill="both", expand=True)
        scrollbar_texto.pack(in_=self.frame_texto_arbol, side="right", fill="y")
        
        # Configurar el redimensionamiento
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def dibujar_arbol_grafico(self, canvas, nodo, x, y, horizontal_space, nivel=0):
        if nodo is None:
            return
            
        # Tamaño del nodo
        radio = 20
        
        # Colores según tipo de nodo
        if self.analizador.es_operador(nodo.valor):
            color_fondo = "#FFD700"  # Dorado para operadores
        else:
            color_fondo = "#90EE90"  # Verde claro para operandos
            
        # Dibujar nodo (círculo con texto)
        canvas.create_oval(x-radio, y-radio, x+radio, y+radio, fill=color_fondo, outline="black")
        canvas.create_text(x, y, text=nodo.valor, font=(self.fuente_mono, 11, "bold"))
        
        # Calcular espacio para nivel siguiente
        nuevo_espacio = horizontal_space / 2
        
        # Dibujar hijos y conectarlos
        if nodo.izquierdo:
            # Calcular posición del hijo izquierdo
            hijo_x = x - nuevo_espacio
            hijo_y = y + 60
            
            # Dibujar línea conectora
            canvas.create_line(x, y+radio, hijo_x, hijo_y-radio, fill="black")
            
            # Dibujar hijo izquierdo
            self.dibujar_arbol_grafico(canvas, nodo.izquierdo, hijo_x, hijo_y, nuevo_espacio, nivel+1)
            
        if nodo.derecho:
            # Calcular posición del hijo derecho
            hijo_x = x + nuevo_espacio
            hijo_y = y + 60
            
            # Dibujar línea conectora
            canvas.create_line(x, y+radio, hijo_x, hijo_y-radio, fill="black")
            
            # Dibujar hijo derecho
            self.dibujar_arbol_grafico(canvas, nodo.derecho, hijo_x, hijo_y, nuevo_espacio, nivel+1)
    
    def calcular_altura_arbol(self, nodo):
        if nodo is None:
            return 0
        return 1 + max(self.calcular_altura_arbol(nodo.izquierdo), 
                       self.calcular_altura_arbol(nodo.derecho))
    
    def analizar_expresion(self):
        try:
            expresion = self.entrada_expr.get()
            
            # Obtener notaciones y árbol
            notacion_prefija = self.analizador.infix_a_prefix(expresion)
            notacion_postfija = self.analizador.infix_a_postfix(expresion)
            arbol = self.analizador.construir_arbol(expresion)
            
            # Mostrar resultados
            self.texto_prefija.delete(1.0, tk.END)
            self.texto_prefija.insert(tk.END, f"Notación Polaca (Prefija):\n\n{' '.join(notacion_prefija)}")
            
            self.texto_postfija.delete(1.0, tk.END)
            self.texto_postfija.insert(tk.END, f"Notación Polaca Inversa (Postfija):\n\n{' '.join(notacion_postfija)}")
            
            # Mostrar árbol en formato texto
            self.texto_arbol.delete(1.0, tk.END)
            if arbol:
                representacion_arbol = self.analizador.arbol_a_cadena(arbol)
                self.texto_arbol.insert(tk.END, "Árbol de Expresiones:\n\n")
                self.texto_arbol.insert(tk.END, representacion_arbol, "arbol")
                # Configurar etiquetas para colorear el árbol
                self.texto_arbol.tag_configure("arbol", foreground="blue", font=(self.fuente_mono, 11))
                
                # Dibujar árbol gráfico
                self.canvas.delete("all")
                
                # Calcular dimensiones necesarias
                altura = self.calcular_altura_arbol(arbol)
                ancho_canvas = 2 ** (altura + 1) * 30
                alto_canvas = altura * 100 + 50
                
                # Configurar región de desplazamiento del canvas
                self.canvas.config(scrollregion=(0, 0, ancho_canvas, alto_canvas))
                
                # Dibujar árbol gráfico
                self.dibujar_arbol_grafico(self.canvas, arbol, ancho_canvas/2, 50, ancho_canvas/4)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar la expresión: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazApp(root)
    root.mainloop()