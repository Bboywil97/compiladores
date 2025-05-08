import re
import tkinter as tk
from tkinter import ttk
from collections import Counter

# Enumeración para los tipos de tokens
class TipoToken:
    IDENTIFICADOR = "IDENTIFICADOR"
    NUMERO = "NUMERO"
    OPERADOR = "OPERADOR"
    SIMBOLO = "SIMBOLO"
    PALABRA_RESERVADA = "PALABRA RESERVADA"
    DESCONOCIDO = "DESCONOCIDO"

# Lista de palabras reservadas
PALABRAS_RESERVADAS = {"int", "float", "if", "else", "for", "while", "return", "void", "char", "double", "switch", "case", "break", "continue", "default", "do", "goto", "sizeof", "typedef", "static", "extern", "const", "volatile", "register", "inline", "restrict", "auto", "enum", "struct", "union", "sizeof", "typedef", "asm", "goto", "volatile", "const"}

# Función para determinar si un carácter es un operador
def es_operador(c):
    return c in {'+', '-', '*', '/', '=', '>', '<', '!', '&', '|', '^', '%', '~', '+=', '-=', '*=', '/=', '==', '!=', '>=', '<=', '&&', '||'}

# Función para determinar si un carácter es un símbolo
def es_simbolo(c):
    return c in {'(', ')', '{', '}', '[', ']', ';', ','}

# Análisis léxico
def analizar_lexico(codigo):
    tokens = []
    tabla_simbolos = set()
    contador_tokens = Counter()
    i = 0
    line_number = 1  # Contador de líneas
    while i < len(codigo):
        if codigo[i] == '\n':
            line_number += 1  # Incrementar el número de línea cuando se encuentra un salto de línea
            i += 1
            continue

        if codigo[i].isspace():
            i += 1
            continue
        
        if codigo[i].isdigit():
            j = i
            while j < len(codigo) and (codigo[j].isdigit() or codigo[j] == '.'):
                j += 1
            lexema = codigo[i:j]
            tokens.append((TipoToken.NUMERO, lexema, line_number))
            tabla_simbolos.add((TipoToken.NUMERO, lexema))
            contador_tokens[TipoToken.NUMERO] += 1
            i = j
            continue
        
        if codigo[i].isalpha():
            j = i
            while j < len(codigo) and (codigo[j].isalnum() or codigo[j] == '_'):
                j += 1
            lexema = codigo[i:j]
            tipo = TipoToken.PALABRA_RESERVADA if lexema in PALABRAS_RESERVADAS else TipoToken.IDENTIFICADOR
            tokens.append((tipo, lexema, line_number))
            tabla_simbolos.add((tipo, lexema))
            contador_tokens[tipo] += 1
            i = j
            continue
        
        if es_operador(codigo[i]):
            tokens.append((TipoToken.OPERADOR, codigo[i], line_number))
            tabla_simbolos.add((TipoToken.OPERADOR, codigo[i]))
            contador_tokens[TipoToken.OPERADOR] += 1
            i += 1
            continue
        
        if es_simbolo(codigo[i]):
            tokens.append((TipoToken.SIMBOLO, codigo[i], line_number))
            tabla_simbolos.add((TipoToken.SIMBOLO, codigo[i]))
            contador_tokens[TipoToken.SIMBOLO] += 1
            i += 1
            continue
        
        tokens.append((TipoToken.DESCONOCIDO, codigo[i], line_number))
        tabla_simbolos.add((TipoToken.DESCONOCIDO, codigo[i]))
        contador_tokens[TipoToken.DESCONOCIDO] += 1
        i += 1
    
    return tokens, tabla_simbolos, contador_tokens

# Análisis sintáctico
def analizar_sintactico():
    codigo = entrada_texto.get("1.0", tk.END)
    tokens, _, _ = analizar_lexico(codigo)
    estructura_valida = any(t[0] == TipoToken.PALABRA_RESERVADA and t[1] in {"if", "for", "while"} for t in tokens)
    errores = []
    if not estructura_valida:
        for t in tokens:
            if t[0] == TipoToken.PALABRA_RESERVADA and t[1] not in {"if", "for", "while"}:
                errores.append(f"Error sintáctico en la línea {t[2]}: Se esperaba una estructura de control válida.")
    
    if errores:
        resultado_label.config(text="\n".join(errores), foreground="red")  # Color rojo para errores
    else:
        resultado_label.config(text="Análisis sintáctico: Estructura válida", foreground="green")  # Color verde para éxito

# Análisis semántico
def analizar_semantico():
    codigo = entrada_texto.get("1.0", tk.END).strip()
    tokens, _, _ = analizar_lexico(codigo)
    tipos = {"int": "NUMERO", "float": "NUMERO", "char": "IDENTIFICADOR"}
    errores = []
    
    for i in range(len(tokens) - 2):
        if tokens[i][1] in tipos and tokens[i+1][0] == TipoToken.IDENTIFICADOR and tokens[i+2][1] != "=":
            error_pos = sum(len(t[1]) for t in tokens[:i])
            errores.append(f"Error semántico en la línea {tokens[i+1][2]}: Falta asignación en {tokens[i+1][1]}")
    
    if errores:
        resultado_label.config(text="\n".join(errores), foreground="red")  # Color rojo para errores
    else:
        resultado_label.config(text="Análisis semántico: Sin errores", foreground="green")  # Color verde para éxito

# Función para ejecutar el análisis léxico
def ejecutar_analisis_lexico():
    codigo = entrada_texto.get("1.0", tk.END)
    tokens, tabla_simbolos, contador_tokens = analizar_lexico(codigo)
    
    for item in tabla_tokens.get_children():
        tabla_tokens.delete(item)
    for item in tabla_simbolos_tree.get_children():
        tabla_simbolos_tree.delete(item)
    for item in tabla_contador.get_children():
        tabla_contador.delete(item)
    
    for token in tokens:
        tabla_tokens.insert("", "end", values=(token[0], token[1], token[2]))
    
    for simbolo in tabla_simbolos:
        tabla_simbolos_tree.insert("", "end", values=(simbolo[0], simbolo[1]))
    
    for tipo, cantidad in contador_tokens.items():
        tabla_contador.insert("", "end", values=(tipo, cantidad))

# Función para resetear los datos
def resetear_datos():
    entrada_texto.delete("1.0", tk.END)  # Limpiar el campo de entrada
    resultado_label.config(text="")  # Limpiar el texto de resultados
    for item in tabla_tokens.get_children():
        tabla_tokens.delete(item)  # Limpiar la tabla de tokens
    for item in tabla_simbolos_tree.get_children():
        tabla_simbolos_tree.delete(item)  # Limpiar la tabla de símbolos
    for item in tabla_contador.get_children():
        tabla_contador.delete(item)  # Limpiar la tabla de contador

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Analizador Léxico, Sintáctico y Semántico")
ventana.geometry("1200x700")  # Ventana más grande para acomodar el diseño

# Crear marco para el encabezado con nombre
marco_encabezado = tk.Frame(ventana, bg="#3a7ca5")
marco_encabezado.pack(fill=tk.X)

# Agregar nombre en el encabezado
nombre_label = tk.Label(
    marco_encabezado, 
    text="Jose Alejandro Castillo Balboa 6to M", 
    font=("Arial", 14, "bold"),
    fg="white",
    bg="#3a7ca5",
    pady=10
)
nombre_label.pack()

# Crear un marco principal para organizar todo
marco_principal = tk.Frame(ventana)
marco_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Marco izquierdo para entrada y controles
marco_izquierdo = tk.Frame(marco_principal, width=500)
marco_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# Marco derecho para las tablas
marco_derecho = tk.Frame(marco_principal, width=500)
marco_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Componentes en el marco izquierdo
entrada_label = tk.Label(marco_izquierdo, text="Ingrese el código:", font=("Arial", 12))
entrada_label.pack(anchor=tk.W, pady=(0, 5))

# Campo de entrada para el código
entrada_texto = tk.Text(marco_izquierdo, height=15, width=50, font=("Consolas", 11))
entrada_texto.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Marco para botones
marco_botones = tk.Frame(marco_izquierdo)
marco_botones.pack(fill=tk.X, pady=10)

# Botones de análisis con mejor estilo
estilo_boton = {"padx": 10, "pady": 5, "font": ("Arial", 10), "width": 15}

boton_lexico = tk.Button(marco_botones, text="Análisis Léxico", command=ejecutar_analisis_lexico, **estilo_boton)
boton_lexico.pack(side=tk.LEFT, padx=(0, 5))

boton_sintactico = tk.Button(marco_botones, text="Análisis Sintáctico", command=analizar_sintactico, **estilo_boton)
boton_sintactico.pack(side=tk.LEFT, padx=5)

boton_semantico = tk.Button(marco_botones, text="Análisis Semántico", command=analizar_semantico, **estilo_boton)
boton_semantico.pack(side=tk.LEFT, padx=5)

boton_resetear = tk.Button(marco_botones, text="Resetear", command=resetear_datos, **estilo_boton)
boton_resetear.pack(side=tk.LEFT, padx=(5, 0))

# Label para mostrar resultados con mejor estilo
resultado_frame = tk.Frame(marco_izquierdo, relief=tk.GROOVE, borderwidth=2)
resultado_frame.pack(fill=tk.BOTH, expand=True, pady=10)

resultado_titulo = tk.Label(resultado_frame, text="Resultados del análisis:", font=("Arial", 11, "bold"), anchor=tk.W)
resultado_titulo.pack(fill=tk.X, padx=5, pady=5)

resultado_label = tk.Label(resultado_frame, text="", font=("Arial", 10), justify=tk.LEFT, anchor=tk.W, wraplength=450)
resultado_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Componentes en el marco derecho (tablas)
# Estilo para las tablas
estilo = ttk.Style()
estilo.configure("Treeview", font=("Arial", 9))
estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Marco para la tabla de tokens
marco_tabla_tokens = tk.Frame(marco_derecho)
marco_tabla_tokens.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

tk.Label(marco_tabla_tokens, text="Tabla de Tokens", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))

tabla_tokens = ttk.Treeview(marco_tabla_tokens, columns=("Tipo", "Lexema", "Línea"), show="headings", height=8)
tabla_tokens.heading("Tipo", text="Tipo de Token")
tabla_tokens.heading("Lexema", text="Lexema")
tabla_tokens.heading("Línea", text="Línea")
tabla_tokens.column("Tipo", width=150)
tabla_tokens.column("Lexema", width=150)
tabla_tokens.column("Línea", width=80)
tabla_tokens.pack(fill=tk.BOTH, expand=True)

# Scrollbar para la tabla de tokens
scrollbar_tokens = ttk.Scrollbar(tabla_tokens, orient="vertical", command=tabla_tokens.yview)
tabla_tokens.configure(yscrollcommand=scrollbar_tokens.set)
scrollbar_tokens.pack(side=tk.RIGHT, fill=tk.Y)

# Marco para la tabla de símbolos
marco_tabla_simbolos = tk.Frame(marco_derecho)
marco_tabla_simbolos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

tk.Label(marco_tabla_simbolos, text="Tabla de Símbolos", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))

tabla_simbolos_tree = ttk.Treeview(marco_tabla_simbolos, columns=("Tipo", "Lexema"), show="headings", height=8)
tabla_simbolos_tree.heading("Tipo", text="Tipo")
tabla_simbolos_tree.heading("Lexema", text="Lexema")
tabla_simbolos_tree.column("Tipo", width=150)
tabla_simbolos_tree.column("Lexema", width=150)
tabla_simbolos_tree.pack(fill=tk.BOTH, expand=True)

# Scrollbar para la tabla de símbolos
scrollbar_simbolos = ttk.Scrollbar(tabla_simbolos_tree, orient="vertical", command=tabla_simbolos_tree.yview)
tabla_simbolos_tree.configure(yscrollcommand=scrollbar_simbolos.set)
scrollbar_simbolos.pack(side=tk.RIGHT, fill=tk.Y)

# Marco para la tabla de contador
marco_tabla_contador = tk.Frame(marco_derecho)
marco_tabla_contador.pack(fill=tk.BOTH, expand=True)

tk.Label(marco_tabla_contador, text="Contador de Tokens", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))

tabla_contador = ttk.Treeview(marco_tabla_contador, columns=("Tipo", "Cantidad"), show="headings", height=8)
tabla_contador.heading("Tipo", text="Tipo de Token")
tabla_contador.heading("Cantidad", text="Cantidad")
tabla_contador.column("Tipo", width=150)
tabla_contador.column("Cantidad", width=150)
tabla_contador.pack(fill=tk.BOTH, expand=True)

# Scrollbar para la tabla de contador
scrollbar_contador = ttk.Scrollbar(tabla_contador, orient="vertical", command=tabla_contador.yview)
tabla_contador.configure(yscrollcommand=scrollbar_contador.set)
scrollbar_contador.pack(side=tk.RIGHT, fill=tk.Y)

ventana.mainloop()