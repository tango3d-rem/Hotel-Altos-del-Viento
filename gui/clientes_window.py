import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ClientesWindow:
    def __init__(self, master):
        self.ventana = tk.Toplevel(master)
        self.ventana.title("Gestión de Clientes")
        self.ventana.geometry("700x500")

        # Botones arriba
        frame_botones = tk.Frame(self.ventana)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Nuevo Cliente", command=self.abrir_formulario_cliente).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Editar Cliente", command=self.editar_cliente).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=0, column=2, padx=5)

        # Tabla
        self.tree = ttk.Treeview(self.ventana, columns=("ID", "Nombre", "Apellido", "DNI", "Teléfono", "Email"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill="both")

        self.cargar_clientes()

    def cargar_clientes(self):
        self.tree.delete(*self.tree.get_children())
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, apellido, dni, telefono, email FROM clientes")
        for fila in cursor.fetchall():
            self.tree.insert("", tk.END, values=fila)
        conexion.close()

    def abrir_formulario_cliente(self, cliente=None):
        FormularioCliente(self, cliente)

    def eliminar_cliente(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar un cliente")
            return
        cliente_id = self.tree.item(seleccionado[0])['values'][0]
        
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este cliente?")
        if respuesta:
            conexion = sqlite3.connect("hotel.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
            conexion.commit()
            conexion.close()
            self.cargar_clientes()

    def editar_cliente(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar un cliente")
            return
        valores = self.tree.item(seleccionado[0])['values']
        cliente = {
            "id": valores[0],
            "nombre": valores[1],
            "apellido": valores[2],
            "dni": valores[3],
            "telefono": valores[4],
            "email": valores[5],
        }
        self.abrir_formulario_cliente(cliente)


class FormularioCliente:
    def __init__(self, parent, cliente=None):
        self.parent = parent
        self.cliente = cliente
        self.ventana = tk.Toplevel(parent.ventana)
        self.ventana.title("Formulario Cliente")
        self.ventana.geometry("300x500")

        # Campos
        tk.Label(self.ventana, text="Nombre:").pack(pady=5)
        self.nombre = tk.Entry(self.ventana)
        self.nombre.pack()

        tk.Label(self.ventana, text="Apellido:").pack(pady=5)
        self.apellido = tk.Entry(self.ventana)
        self.apellido.pack()

        tk.Label(self.ventana, text="DNI:").pack(pady=5)
        self.dni = tk.Entry(self.ventana)
        self.dni.pack()

        tk.Label(self.ventana, text="Teléfono:").pack(pady=5)
        self.telefono = tk.Entry(self.ventana)
        self.telefono.pack()

        tk.Label(self.ventana, text="Email:").pack(pady=5)
        self.email = tk.Entry(self.ventana)
        self.email.pack()

        # Botón guardar
        tk.Button(self.ventana, text="Guardar", command=self.guardar_cliente).pack(pady=20)

        # Si estamos editando, cargamos los datos
        if self.cliente:
            self.cargar_datos()

    def cargar_datos(self):
        self.nombre.insert(0, self.cliente["nombre"])
        self.apellido.insert(0, self.cliente["apellido"])
        self.dni.insert(0, self.cliente["dni"])
        self.telefono.insert(0, self.cliente["telefono"])
        self.email.insert(0, self.cliente["email"])

    def guardar_cliente(self):
        nombre = self.nombre.get()
        apellido = self.apellido.get()
        dni = self.dni.get()
        telefono = self.telefono.get()
        email = self.email.get()

        if not nombre or not apellido or not dni:
            messagebox.showwarning("Campos obligatorios", "Nombre, Apellido y DNI son obligatorios")
            return

        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        try:
            if self.cliente:  # Editar
                cursor.execute("""
                    UPDATE clientes
                    SET nombre=?, apellido=?, dni=?, telefono=?, email=?
                    WHERE id=?
                """, (nombre, apellido, dni, telefono, email, self.cliente["id"]))
            else:  # Nuevo
                cursor.execute("""
                    INSERT INTO clientes (nombre, apellido, dni, telefono, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, apellido, dni, telefono, email))
            conexion.commit()
            messagebox.showinfo("Éxito", "Datos guardados correctamente")
            self.ventana.destroy()
            self.parent.cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conexion.close()
