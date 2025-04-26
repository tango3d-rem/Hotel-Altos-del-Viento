import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ReservasWindow:
    def __init__(self, master):
        self.ventana = tk.Toplevel(master)
        self.ventana.title("Gestión de Reservas")
        self.ventana.geometry("700x500")

        # Botones arriba
        frame_botones = tk.Frame(self.ventana)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Nueva Reserva", command=self.abrir_formulario_nueva_reserva).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Editar Reserva", command=self.abrir_formulario_editar_reserva).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Eliminar Reserva", command=self.eliminar_reserva).grid(row=0, column=2, padx=5)

        # Tabla
        self.tree = ttk.Treeview(self.ventana, columns=("ID", "Cliente", "Habitación", "Entrada", "Salida", "Estado"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill="both")

        self.cargar_reservas()

    def cargar_reservas(self):
        self.tree.delete(*self.tree.get_children())
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT r.id, c.nombre || ' ' || c.apellido, h.numero, r.fecha_entrada, r.fecha_salida, r.estado
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN habitaciones h ON r.habitacion_id = h.id
        """)
        for fila in cursor.fetchall():
            self.tree.insert("", tk.END, values=fila)
        conexion.close()

    def abrir_formulario_nueva_reserva(self):
        FormularioReserva(self)

    def abrir_formulario_editar_reserva(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar una reserva para editar")
            return
        valores = self.tree.item(seleccionado[0])['values']
        reserva = {
            "id": valores[0],
            "cliente": valores[1],
            "habitacion": valores[2],
            "fecha_entrada": valores[3],
            "fecha_salida": valores[4],
            "estado": valores[5]
        }
        FormularioReserva(self, reserva)

    def eliminar_reserva(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar", "Debe seleccionar una reserva para eliminar")
            return
        reserva_id = self.tree.item(seleccionado[0])['values'][0]

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta reserva?")
        if respuesta:
            conexion = sqlite3.connect("hotel.db")
            cursor = conexion.cursor()
            # Cambiar habitación a disponible antes de eliminar
            cursor.execute("""
                UPDATE habitaciones
                SET estado = 'disponible'
                WHERE id = (SELECT habitacion_id FROM reservas WHERE id = ?)
            """, (reserva_id,))
            cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
            conexion.commit()
            conexion.close()
            self.cargar_reservas()

class FormularioReserva:
    def __init__(self, parent, reserva=None):
        self.parent = parent
        self.reserva = reserva
        self.ventana = tk.Toplevel(parent.ventana)
        self.ventana.title("Formulario Reserva")
        self.ventana.geometry("300x500")

        # Cargar clientes y habitaciones
        self.clientes = self.obtener_clientes()
        self.habitaciones = self.obtener_habitaciones()

        # Cliente
        tk.Label(self.ventana, text="Cliente:").pack(pady=5)
        self.cliente_var = tk.StringVar()
        self.cliente_combobox = ttk.Combobox(self.ventana, textvariable=self.cliente_var, state="readonly")
        self.cliente_combobox['values'] = [f"{c[1]} {c[2]}" for c in self.clientes]
        self.cliente_combobox.pack()

        # Habitación
        tk.Label(self.ventana, text="Habitación:").pack(pady=5)
        self.habitacion_var = tk.StringVar()
        self.habitacion_combobox = ttk.Combobox(self.ventana, textvariable=self.habitacion_var, state="readonly")
        self.habitacion_combobox['values'] = [h[1] for h in self.habitaciones]
        self.habitacion_combobox.pack()

        # Fechas
        tk.Label(self.ventana, text="Fecha entrada (YYYY-MM-DD):").pack(pady=5)
        self.fecha_entrada = tk.Entry(self.ventana)
        self.fecha_entrada.pack()

        tk.Label(self.ventana, text="Fecha salida (YYYY-MM-DD):").pack(pady=5)
        self.fecha_salida = tk.Entry(self.ventana)
        self.fecha_salida.pack()

        # Estado
        tk.Label(self.ventana, text="Estado:").pack(pady=5)
        self.estado_var = tk.StringVar()
        self.estado_combobox = ttk.Combobox(self.ventana, textvariable=self.estado_var, state="readonly")
        self.estado_combobox['values'] = ["activa", "cancelada", "finalizada"]
        self.estado_combobox.current(0)
        self.estado_combobox.pack()

        # Botón Guardar
        tk.Button(self.ventana, text="Guardar", command=self.guardar_reserva).pack(pady=20)

        if self.reserva:
            self.cargar_datos()

    def obtener_clientes(self):
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, apellido FROM clientes")
        clientes = cursor.fetchall()
        conexion.close()
        return clientes

    def obtener_habitaciones(self):
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, numero FROM habitaciones")
        habitaciones = cursor.fetchall()
        conexion.close()
        return habitaciones

    def cargar_datos(self):
        self.cliente_combobox.set(self.reserva["cliente"])
        self.habitacion_combobox.set(self.reserva["habitacion"])
        self.fecha_entrada.insert(0, self.reserva["fecha_entrada"])
        self.fecha_salida.insert(0, self.reserva["fecha_salida"])
        self.estado_combobox.set(self.reserva["estado"])

    def guardar_reserva(self):
        cliente_nombre = self.cliente_var.get()
        habitacion_numero = self.habitacion_var.get()
        entrada = self.fecha_entrada.get()
        salida = self.fecha_salida.get()
        estado = self.estado_var.get()

        if not cliente_nombre or not habitacion_numero or not entrada or not salida or not estado:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        # Buscar IDs
        cliente_id = next((c[0] for c in self.clientes if f"{c[1]} {c[2]}" == cliente_nombre), None)
        habitacion_id = next((h[0] for h in self.habitaciones if h[1] == habitacion_numero), None)

        if cliente_id is None or habitacion_id is None:
            messagebox.showerror("Error", "Error al seleccionar cliente o habitación")
            return

        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        try:
            if self.reserva:
                # Si cambió de habitación, actualizar estados
                cursor.execute("SELECT habitacion_id FROM reservas WHERE id=?", (self.reserva["id"],))
                habitacion_actual = cursor.fetchone()[0]
                if habitacion_actual != habitacion_id:
                    cursor.execute("UPDATE habitaciones SET estado='disponible' WHERE id=?", (habitacion_actual,))
                    cursor.execute("UPDATE habitaciones SET estado='ocupada' WHERE id=?", (habitacion_id,))
                
                cursor.execute("""
                    UPDATE reservas
                    SET cliente_id=?, habitacion_id=?, fecha_entrada=?, fecha_salida=?, estado=?
                    WHERE id=?
                """, (cliente_id, habitacion_id, entrada, salida, estado, self.reserva["id"]))
            else:
                cursor.execute("""
                    INSERT INTO reservas (cliente_id, habitacion_id, fecha_entrada, fecha_salida, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (cliente_id, habitacion_id, entrada, salida, estado))
                cursor.execute("UPDATE habitaciones SET estado='ocupada' WHERE id=?", (habitacion_id,))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Reserva guardada correctamente")
            self.ventana.destroy()
            self.parent.cargar_reservas()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conexion.close()
