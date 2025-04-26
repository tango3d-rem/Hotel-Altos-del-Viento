import tkinter as tk
from tkinter import messagebox
import sqlite3

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Login - Hotel Reservas")
        master.geometry("300x200")
        master.resizable(False, False)

        # Etiquetas y entradas
        tk.Label(master, text="Usuario").pack(pady=5)
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        tk.Label(master, text="Contraseña").pack(pady=5)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        # Botón
        tk.Button(master, text="Iniciar sesión", command=self.verificar_login).pack(pady=15)

    def verificar_login(self):
        usuario = self.username_entry.get()
        contrasena = self.password_entry.get()

        conexion = sqlite3.connect("hotel.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (usuario, contrasena))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            messagebox.showinfo("Éxito", f"Bienvenido, {usuario}")
            self.master.destroy()
            # Acá podemos lanzar la ventana principal más adelante
            from gui.main_window import MainWindow
            root = tk.Tk()
            app = MainWindow(root, usuario)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
