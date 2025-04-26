import tkinter as tk
from tkinter import messagebox

class MainWindow:
    def __init__(self, master, usuario):
        self.master = master
        master.title("Sistema de Reservas - Hotel")
        master.geometry("400x300")
        master.resizable(False, False)

        tk.Label(master, text=f"Bienvenido, {usuario}", font=("Arial", 12, "bold")).pack(pady=10)

        # Botones de navegación
        tk.Button(master, text="Reservas", width=25, command=self.abrir_reservas).pack(pady=5)
        tk.Button(master, text="Habitaciones", width=25, command=self.abrir_habitaciones).pack(pady=5)
        tk.Button(master, text="Clientes", width=25, command=self.abrir_clientes).pack(pady=5)
        tk.Button(master, text="Facturación", width=25, command=self.abrir_facturacion).pack(pady=5)
        tk.Button(master, text="Salir", width=25, command=master.quit).pack(pady=15)

    # Métodos que podríamos conectar a ventanas específicas más adelante
    def abrir_reservas(self):
        from gui.reservas_window import ReservasWindow
        ReservasWindow(self.master)
    def abrir_habitaciones(self):
        from gui.habitaciones_window import HabitacionesWindow
        HabitacionesWindow(self.master)
    def abrir_clientes(self):
        from gui.clientes_window import ClientesWindow
        ClientesWindow(self.master)
    def abrir_facturacion(self):
        messagebox.showinfo("Facturación", "Aquí irá la ventana de facturación")
