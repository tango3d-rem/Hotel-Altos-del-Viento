import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class FacturacionWindow:
    def __init__(self, master):
        self.ventana = tk.Toplevel(master)
        self.ventana.title("Generar Factura")
        self.ventana.geometry("400x400")

        # Selector de reserva
        tk.Label(self.ventana, text="Seleccionar Reserva:").pack(pady=5)
        self.reserva_var = tk.StringVar()
        self.reserva_combobox = ttk.Combobox(self.ventana, textvariable=self.reserva_var, state="readonly")
        self.reserva_combobox.pack(pady=5)
        
        # Cargar reservas disponibles
        self.cargar_reservas()
        
        # Botón para generar factura
        tk.Button(self.ventana, text="Generar Factura", command=self.generar_factura).pack(pady=10)

        # Información de la factura
        self.factura_text = tk.Text(self.ventana, height=10, width=40)
        self.factura_text.pack(pady=10)

    def cargar_reservas(self):
        """Cargar las reservas activas para que el usuario pueda seleccionarlas"""
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT r.id, c.nombre || ' ' || c.apellido, h.numero, r.fecha_entrada, r.fecha_salida
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN habitaciones h ON r.habitacion_id = h.id
            WHERE r.estado = 'activa'
        """)
        reservas = cursor.fetchall()
        self.reserva_combobox['values'] = [f"Reserva {r[0]} - {r[1]} - Hab {r[2]}" for r in reservas]
        self.reservas_data = {f"Reserva {r[0]} - {r[1]} - Hab {r[2]}": r for r in reservas}
        conexion.close()

    def generar_factura(self):
        """Generar la factura para la reserva seleccionada"""
        reserva_seleccionada = self.reserva_var.get()
        
        if not reserva_seleccionada:
            messagebox.showwarning("Selección necesaria", "Por favor, selecciona una reserva")
            return
        
        # Obtener datos de la reserva seleccionada
        reserva_id, cliente_nombre, habitacion_numero, fecha_entrada, fecha_salida = self.reservas_data[reserva_seleccionada]

        # Calcular el total de la estancia
        precio_habitacion = self.obtener_precio_habitacion(habitacion_numero)
        dias_estancia = self.calcular_dias_estancia(fecha_entrada, fecha_salida)
        total = precio_habitacion * dias_estancia
        
        # Mostrar los detalles de la factura
        factura = f"Factura - Reserva #{reserva_id}\n"
        factura += f"Cliente: {cliente_nombre}\n"
        factura += f"Habitación: {habitacion_numero}\n"
        factura += f"Fecha Entrada: {fecha_entrada}\n"
        factura += f"Fecha Salida: {fecha_salida}\n"
        factura += f"Días de Estancia: {dias_estancia} días\n"
        factura += f"Precio por Noche: ${precio_habitacion}\n"
        factura += f"Total: ${total}\n"
        
        self.factura_text.delete(1.0, tk.END)  # Limpiar el contenido anterior
        self.factura_text.insert(tk.END, factura)
        
        # Aquí podrías agregar una funcionalidad para imprimir o guardar como PDF si es necesario

    def obtener_precio_habitacion(self, habitacion_numero):
        """Obtener el precio de la habitación desde la base de datos"""
        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT precio FROM habitaciones WHERE numero = ?", (habitacion_numero,))
        precio = cursor.fetchone()[0]
        conexion.close()
        return precio

    def calcular_dias_estancia(self, fecha_entrada, fecha_salida):
        """Calcular los días de estancia entre las fechas de entrada y salida"""
        fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d")
        fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%d")
        return (fecha_salida - fecha_entrada).days
