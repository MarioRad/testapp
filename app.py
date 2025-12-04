import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pymupdf
import os
from pprint import pprint


# --- Configuración de la Base de Datos ---

def setup_database():
    """Crea la base de datos y la tabla de ebooks si no existen."""
    conn = sqlite3.connect('ebook_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            file_path TEXT NOT NULL UNIQUE,
            pages INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# --- Ventana del Lector de PDF ---

class PDFViewer(tk.Toplevel):
    """Una ventana para mostrar y navegar por un archivo PDF."""
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.title("Lector de PDF")
        self.geometry("800x1000")
        self.file_path = file_path
        self.current_page = 0

        try:
            self.doc = pymupdf.open(self.file_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo PDF:\n{e}")
            self.destroy()
            return
            
        self.total_pages = len(self.doc)

        # --- Widgets de la Interfaz ---
        
        # Frame de control (botones y etiqueta de página)
        control_frame = ttk.Frame(self)
        control_frame.pack(side="bottom", fill="x", pady=5)

        self.prev_button = ttk.Button(control_frame, text="Anterior", command=self.prev_page)
        self.prev_button.pack(side="left", padx=10)

        self.page_label = ttk.Label(control_frame, text="")
        self.page_label.pack(side="left", expand=True)

        self.next_button = ttk.Button(control_frame, text="Siguiente", command=self.next_page)
        self.next_button.pack(side="right", padx=10)

        # Canvas para mostrar la página del PDF
        self.canvas = tk.Canvas(self, bg="gray")
        self.canvas.pack(expand=True, fill="both")

        self.display_page()

    def display_page(self):
        """Renderiza y muestra la página actual en el canvas."""
        if not self.doc or self.current_page < 0 or self.current_page >= self.total_pages:
            return

        # Renderizar la página del PDF a una imagen
        page = self.doc.load_page(self.current_page)
        pix = page.get_pixmap()
        self.photo = tk.PhotoImage(data=pix.tobytes("ppm"))
        
        # Limpiar canvas y mostrar la nueva imagen
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        # Actualizar la etiqueta y el estado de los botones
        self.page_label.config(text=f"Página {self.current_page + 1} de {self.total_pages}")
        self.prev_button.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        self.update_idletasks() # Asegura que la UI se actualice
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def next_page(self):
        """Va a la página siguiente."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        """Va a la página anterior."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def destroy(self):
        """Cierra el documento PDF antes de destruir la ventana."""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
        super().destroy()


# --- Ventana Principal de la Aplicación ---

class EbookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mi Biblioteca de Ebooks")
        self.root.geometry("800x600")

        # --- Estilo ---
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TFrame", background="#f0f0f0")

        # --- Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Widgets ---
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        import_button = ttk.Button(button_frame, text="Importar Nuevo Ebook", command=self.import_ebook)
        import_button.pack(side="left", padx=(0, 10))
        
        read_button = ttk.Button(button_frame, text="Leer Ebook Seleccionado", command=self.read_ebook)
        read_button.pack(side="left")
        
        delete_button = ttk.Button(button_frame, text="Eliminar Ebook", command=self.delete_ebook)
        delete_button.pack(side="right")


        # Vista de árbol para mostrar los ebooks
        self.tree = ttk.Treeview(main_frame, columns=("Title", "Author", "Paginas"), show="headings")
        self.tree.heading("Title", text="Título")
        self.tree.heading("Author", text="Autor")
        self.tree.heading("Paginas", text="Paginas")
        self.tree.pack(fill="both", expand=True)
        
        # Diccionario para mapear IDs del Treeview a IDs de la base de datos
        self.tree_item_to_db_id = {}

        self.load_ebooks()

    def load_ebooks(self):
        """Carga los ebooks desde la BD y los muestra en la lista."""
        # Limpiar vista de árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_item_to_db_id.clear()

        # Cargar desde la base de datos
        conn = sqlite3.connect('ebook_library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, pages FROM ebooks ORDER BY title")
        
        for row in cursor.fetchall():
            db_id, title, author, pages = row
            # Insertar en el Treeview
            item_id = self.tree.insert("", "end", values=(title, author, pages or "Desconocido"))
            # Mapear el ID del item del Treeview al ID de la base de datos
            self.tree_item_to_db_id[item_id] = db_id

        conn.close()

    def import_ebook(self):
        """Abre un diálogo para seleccionar un PDF y guardarlo en la BD."""
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if not file_path:
            return

        try:
            doc = pymupdf.open(file_path)
            meta = doc.metadata
            title = meta.get('title', os.path.basename(file_path).replace('.pdf', ''))
            author = meta.get('author', 'Autor Desconocido')
            pages = meta.get('page_count', 0)
            doc.close()
            
            if not title: # Si el título está vacío
                 title = os.path.basename(file_path).replace('.pdf', '')

            conn = sqlite3.connect('ebook_library.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ebooks (title, author, file_path, pages) VALUES (?, ?, ?, ?)",
                           (title, author, file_path, pages))
            conn.commit()
            conn.close()
            pprint(meta)

            self.load_ebooks()
            messagebox.showinfo("Éxito", f"'{title}' ha sido importado.")

        except sqlite3.IntegrityError:
             messagebox.showwarning("Duplicado", "Este libro ya existe en tu biblioteca.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar el archivo:\n{e}")

    def read_ebook(self):
        """Abre la ventana del lector para el ebook seleccionado."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un libro para leer.")
            return

        db_id = self.tree_item_to_db_id.get(selected_item)
        
        conn = sqlite3.connect('ebook_library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM ebooks WHERE id = ?", (db_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            file_path = result[0]
            if os.path.exists(file_path):
                PDFViewer(self.root, file_path)
            else:
                messagebox.showerror("Error", f"El archivo no se encontró en la ruta:\n{file_path}\nPuede que haya sido movido o eliminado.")
        else:
            messagebox.showerror("Error", "No se pudo encontrar el libro en la base de datos.")
            
    def delete_ebook(self):
        """Elimina el ebook seleccionado de la base de datos."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un libro para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este libro de tu biblioteca?"):
            db_id = self.tree_item_to_db_id.get(selected_item)
            conn = sqlite3.connect('ebook_library.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ebooks WHERE id = ?", (db_id,))
            conn.commit()
            conn.close()
            self.load_ebooks()
            messagebox.showinfo("Eliminado", "El libro ha sido eliminado de la biblioteca.")


if __name__ == "__main__":
    setup_database()  # Asegura que la BD esté lista
    root = tk.Tk()
    app = EbookApp(root)
    root.mainloop()
