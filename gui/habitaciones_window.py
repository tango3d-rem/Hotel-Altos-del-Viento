import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class HabitacionesWindow:
    def __init__(self, master):
        self.ventana = tk.Toplevel(master)
        self.ventana.title("Gestión de Habitaciones")
        self.ventana.geometry("700x500")

        # Botones arriba
        frame_botones = tk.Frame(self.ventana)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Nueva Habitación", command=self.abrir_formulario_nueva_habitacion).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Editar Habitación", command=self.abrir_formulario_editar_habitacion).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Eliminar Habitación", command=self.eliminar_habitacion).grid(row=0, column=2, padx=5)

        # Tabla
        self.tree = ttk.Treeview(self.ventana, columns=("ID", "Número", "Tipo", "Precio", "Estado"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill="both")

        self.cargar_habitaciones()

    def cargar_habitaciones(self):
        self.tree.delete(*self.tree.get_children())
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, numero, tipo, precio, estado FROM habitaciones")
        for fila in cursor.fetchall():
            self.tree.insert("", tk.END, values=fila)
        conexion.close()

    def abrir_formulario_nueva_habitacion(self):
        FormularioHabitacion(self)

    def abrir_formulario_editar_habitacion(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar una habitación para editar")
            return
        valores = self.tree.item(seleccionado[0])['values']
        habitacion = {
            "id": valores[0],
            "numero": valores[1],
            "tipo": valores[2],
            "precio": valores[3],
            "estado": valores[4]
        }
        FormularioHabitacion(self, habitacion)

    def eliminar_habitacion(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar una habitación para eliminar")
            return
        habitacion_id = self.tree.item(seleccionado[0])['values'][0]

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta habitación?")
        if respuesta:
            conexion = sqlite3.connect("hotel.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM habitaciones WHERE id=?", (habitacion_id,))
            conexion.commit()
            conexion.close()
            self.cargar_habitaciones()

class FormularioHabitacion:
    def __init__(self, parent, habitacion=None):
        self.parent = parent
        self.habitacion = habitacion
        self.ventana = tk.Toplevel(parent.ventana)
        self.ventana.title("Formulario Habitación")
        self.ventana.geometry("300x400")

        # Número
        tk.Label(self.ventana, text="Número de Habitación:").pack(pady=5)
        self.numero = tk.Entry(self.ventana)
        self.numero.pack()

        # Tipo
        tk.Label(self.ventana, text="Tipo de Habitación:").pack(pady=5)
        self.tipo_var = tk.StringVar()
        self.tipo_combobox = ttk.Combobox(self.ventana, textvariable=self.tipo_var, state="readonly")
        self.tipo_combobox['values'] = ["simple", "doble", "suite"]
        self.tipo_combobox.pack()

        # Precio
        tk.Label(self.ventana, text="Precio por Noche:").pack(pady=5)
        self.precio = tk.Entry(self.ventana)
        self.precio.pack()

        # Estado
        tk.Label(self.ventana, text="Estado:").pack(pady=5)
        self.estado_var = tk.StringVar()
        self.estado_combobox = ttk.Combobox(self.ventana, textvariable=self.estado_var, state="readonly")
        self.estado_combobox['values'] = ["disponible", "ocupada"]
        self.estado_combobox.current(0)
        self.estado_combobox.pack()

        # Botón Guardar
        tk.Button(self.ventana, text="Guardar", command=self.guardar_habitacion).pack(pady=20)

        if self.habitacion:
            self.cargar_datos()

    def cargar_datos(self):
        self.numero.insert(0, self.habitacion["numero"])
        self.tipo_combobox.set(self.habitacion["tipo"])
        self.precio.insert(0, self.habitacion["precio"])
        self.estado_combobox.set(self.habitacion["estado"])

    def guardar_habitacion(self):
        numero = self.numero.get()
        tipo = self.tipo_var.get()
        precio = self.precio.get()
        estado = self.estado_var.get()

        if not numero or not tipo or not precio or not estado:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        try:
            if self.habitacion:
                cursor.execute("""
                    UPDATE habitaciones
                    SET numero=?, tipo=?, precio=?, estado=?
                    WHERE id=?
                """, (numero, tipo, precio, estado, self.habitacion["id"]))
            else:
                cursor.execute("""
                    INSERT INTO habitaciones (numero, tipo, precio, estado)
                    VALUES (?, ?, ?, ?)
                """, (numero, tipo, precio, estado))
            conexion.commit()
            messagebox.showinfo("Éxito", "Habitación guardada correctamente")
            self.ventana.destroy()
            self.parent.cargar_habitaciones()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conexion.close()
