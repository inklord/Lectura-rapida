import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import PyPDF2
import docx
import time
import threading
import re

class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector Rápido RSVP")
        self.root.geometry("900x600")
        self.root.configure(bg='black')
        
        # Configuración responsiva de la ventana raíz
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Variables de estado
        self.words = []
        self.current_index = 0
        self.is_running = False
        self.wpm = 300
        self.font_family = "Arial" # Fuente por defecto más moderna
        self.font_size = 60        # Texto más grande por defecto
        self.pivot_color = "#ff3333" # Rojo brillante por defecto
        self.pivot_x = 450
        self.pivot_y = 300

        # --- Layout Principal ---
        # Contenedor principal que se expande
        self.main_container = tk.Frame(root, bg='black')
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.rowconfigure(0, weight=1) # El canvas ocupa todo el espacio vertical disponible
        self.main_container.rowconfigure(1, weight=0) # La barra de control tiene altura fija
        self.main_container.columnconfigure(0, weight=1)

        # 1. Área de visualización (Canvas)
        self.canvas = tk.Canvas(self.main_container, bg='black', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Evento para manejar el redimensionado de ventana
        self.canvas.bind("<Configure>", self.on_resize)

        # Mensaje de bienvenida inicial en el canvas
        self.canvas_msg = self.canvas.create_text(450, 300, text="Importa un archivo para comenzar", 
                                                fill="#444", font=("Arial", 20), anchor="center")

        # 2. Barra de Controles Inferior (Estilo Media Player)
        self.controls = tk.Frame(self.main_container, bg='#111', pady=15, padx=20)
        self.controls.grid(row=1, column=0, sticky="ew")
        
        # Grid interno de controles: 3 columnas (Config | Play | Velocidad)
        self.controls.columnconfigure(0, weight=1) # Izquierda
        self.controls.columnconfigure(1, weight=0) # Centro (fijo para botón play)
        self.controls.columnconfigure(2, weight=1) # Derecha

        # --- SECCIÓN IZQUIERDA (Configuración) ---
        frame_left = tk.Frame(self.controls, bg='#111')
        frame_left.grid(row=0, column=0, sticky="w")

        btn_style_subtle = {"bg": "#222", "fg": "#ddd", "font": ("Segoe UI", 9), "relief": tk.FLAT, "padx": 10, "pady": 4}

        self.btn_import = tk.Button(frame_left, text="📂 Importar", command=self.load_file, **btn_style_subtle)
        self.btn_import.pack(side=tk.LEFT, padx=5)

        self.btn_color = tk.Button(frame_left, text="🎨 Color", command=self.choose_color, **btn_style_subtle)
        self.btn_color.pack(side=tk.LEFT, padx=5)

        # Selector de fuentes simplificado
        self.font_var = tk.StringVar(value=self.font_family)
        self.available_fonts = sorted(list(set(tk.font.families())))
        # Estilo para combobox oscuro requiere un poco de truco, usamos estilo por defecto por simplicidad
        self.combo_font = ttk.Combobox(frame_left, textvariable=self.font_var, values=self.available_fonts, 
                                       state="readonly", width=15)
        self.combo_font.pack(side=tk.LEFT, padx=5)
        self.combo_font.bind("<<ComboboxSelected>>", self.change_font)

        # --- SECCIÓN CENTRAL (Reproducción) ---
        frame_center = tk.Frame(self.controls, bg='#111')
        frame_center.grid(row=0, column=1)

        # Botón Play más grande y destacado
        self.btn_toggle = tk.Button(frame_center, text="▶ INICIAR", command=self.toggle_reading, 
                                   bg="#007acc", fg="white", font=("Segoe UI", 12, "bold"), 
                                   relief=tk.FLAT, padx=20, pady=8, activebackground="#005f9e", activeforeground="white")
        self.btn_toggle.pack()

        # --- SECCIÓN DERECHA (Velocidad e Info) ---
        frame_right = tk.Frame(self.controls, bg='#111')
        frame_right.grid(row=0, column=2, sticky="e")

        self.lbl_info = tk.Label(frame_right, text="0 / 0", bg='#111', fg='#666', font=("Consolas", 10))
        self.lbl_info.pack(side=tk.TOP, anchor="e", padx=5)

        wpm_container = tk.Frame(frame_right, bg='#111')
        wpm_container.pack(side=tk.BOTTOM, anchor="e", pady=5)
        
        tk.Label(wpm_container, text="Velocidad:", bg='#111', fg='#888', font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        self.wpm_var = tk.IntVar(value=self.wpm)
        self.slider = tk.Scale(wpm_container, from_=60, to=1000, orient=tk.HORIZONTAL, 
                               variable=self.wpm_var, bg='#111', fg='white', bd=0,
                               troughcolor='#333', highlightthickness=0, length=150, command=self.update_speed)
        self.slider.pack(side=tk.LEFT, padx=5)
        
        self.lbl_wpm_val = tk.Label(wpm_container, text=f"{self.wpm} WPM", bg='#111', fg='white', width=8)
        self.lbl_wpm_val.pack(side=tk.LEFT)

    def on_resize(self, event):
        """Recalcula el centro cuando la ventana cambia de tamaño."""
        self.pivot_x = event.width // 2
        self.pivot_y = event.height // 2
        
        # Mover mensaje de bienvenida si existe
        self.canvas.coords(self.canvas_msg, self.pivot_x, self.pivot_y)
        
        # Redibujar palabra si estamos leyendo o pausados
        if self.words and self.current_index < len(self.words):
            self.show_word_on_canvas(self.words[self.current_index])

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Documentos", "*.pdf *.docx"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                text = self.extract_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                text = self.extract_docx(file_path)
            else:
                messagebox.showerror("Error", "Formato no soportado")
                return
            
            clean_text = text.replace('\n', ' ').replace('\r', ' ')
            self.words = re.findall(r'\w+', clean_text)
            
            if not self.words:
                messagebox.showwarning("Aviso", "No se encontró texto en el documento.")
                return

            self.current_index = 0
            self.canvas.delete(self.canvas_msg) # Borrar mensaje de bienvenida
            self.lbl_info.config(text=f"1 / {len(self.words)}")
            self.show_word_on_canvas(self.words[0])
            self.is_running = False
            self.btn_toggle.config(text="▶ INICIAR", bg="#007acc")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def choose_color(self):
        color = colorchooser.askcolor(title="Color de letra central", color=self.pivot_color)[1]
        if color:
            self.pivot_color = color
            if self.words and self.current_index < len(self.words):
                self.show_word_on_canvas(self.words[self.current_index])

    def change_font(self, event=None):
        self.font_family = self.font_var.get()
        if self.words and self.current_index < len(self.words):
            self.show_word_on_canvas(self.words[self.current_index])

    def extract_pdf(self, path):
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
        return text

    def extract_docx(self, path):
        doc = docx.Document(path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return " ".join(text)

    def get_pivot_index(self, word):
        length = len(word)
        if length <= 1: return 0
        if length >= 2 and length <= 5: return 1
        if length >= 6 and length <= 9: return 2
        if length >= 10 and length <= 13: return 3
        return 4

    def show_word_on_canvas(self, word):
        self.canvas.delete("all")
        
        pivot_idx = self.get_pivot_index(word)
        
        left_part = word[:pivot_idx]
        pivot_char = word[pivot_idx]
        right_part = word[pivot_idx+1:]

        font_config = (self.font_family, self.font_size, "bold")
        
        # Dibujar letra pivote
        self.canvas.create_text(self.pivot_x, self.pivot_y, text=pivot_char, 
                                fill=self.pivot_color, font=font_config, anchor="center")

        # Dibujar partes laterales
        pivot_width = self.measure_text_width(pivot_char, font_config)
        
        if left_part:
            self.canvas.create_text(self.pivot_x - (pivot_width / 2), self.pivot_y, 
                                    text=left_part, fill="white", font=font_config, anchor="e")

        if right_part:
            self.canvas.create_text(self.pivot_x + (pivot_width / 2), self.pivot_y, 
                                    text=right_part, fill="white", font=font_config, anchor="w")

    def measure_text_width(self, text, font):
        temp_font = tk.font.Font(family=font[0], size=font[1], weight=font[2])
        return temp_font.measure(text)

    def toggle_reading(self):
        if not self.words:
            self.load_file() # Si no hay archivo, el botón actúa como "Importar"
            return
            
        if self.is_running:
            self.is_running = False
            self.btn_toggle.config(text="▶ CONTINUAR", bg="#007acc")
        else:
            self.is_running = True
            self.btn_toggle.config(text="⏸ PAUSA", bg="#cc3300")
            threading.Thread(target=self.reading_loop, daemon=True).start()

    def update_speed(self, val):
        self.wpm = int(val)
        self.lbl_wpm_val.config(text=f"{self.wpm} WPM")

    def reading_loop(self):
        while self.is_running and self.current_index < len(self.words):
            word = self.words[self.current_index]
            
            self.root.after(0, self.show_word_on_canvas, word)
            self.root.after(0, self.update_progress_label)
            
            delay = 60.0 / self.wpm
            if len(word) > 8:
                delay *= 1.3
            
            time.sleep(delay)
            self.current_index += 1
            
        if self.current_index >= len(self.words):
            self.is_running = False
            self.root.after(0, lambda: self.btn_toggle.config(text="↺ REINICIAR", bg="#28a745"))
            self.current_index = 0

    def update_progress_label(self):
        self.lbl_info.config(text=f"{self.current_index + 1} / {len(self.words)}")

import tkinter.font

if __name__ == "__main__":
    root = tk.Tk()
    # Intentar establecer icono si existe, si no ignorar
    # root.iconbitmap('icon.ico') 
    app = SpeedReaderApp(root)
    root.mainloop()
