from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askokcancel, WARNING
import database as db
import helpers

class CenterWidgetMixin:
    def center(self):
        self.update()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

class MainWindow(Tk, CenterWidgetMixin):
    def __init__(self):
        super().__init__()
        self.title('Gestor de clientes')
        self.build()
        self.center()

    def build(self):
        frame = Frame(self)
        frame.pack()

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        treeview = ttk.Treeview(frame, yscrollcommand=scrollbar.set)
        treeview['columns'] = ('DNI', 'Nombre', 'Apellido')
        treeview.column("#0", width=0, stretch=NO)
        treeview.column("DNI", anchor=CENTER)
        treeview.column("Nombre", anchor=CENTER)
        treeview.column("Apellido", anchor=CENTER)

        treeview.heading("#0", anchor=CENTER)
        treeview.heading("DNI", text="DNI", anchor=CENTER)
        treeview.heading("Nombre", text="Nombre", anchor=CENTER)
        treeview.heading("Apellido", text="Apellido", anchor=CENTER)

        for cliente in db.Clientes.lista:
            treeview.insert('', 'end', iid=cliente.dni,
                            values=(cliente.dni, cliente.nombre, cliente.apellido))

        treeview.pack()
        scrollbar.config(command=treeview.yview)
        self.treeview = treeview

        frame = Frame(self)
        frame.pack(pady=20)
        Button(frame, text="Crear", command=self.create_client_window).grid(row=1, column=0)
        Button(frame, text="Modificar", command=self.edit_client_window).grid(row=1, column=1)
        Button(frame, text="Borrar", command=self.delete).grid(row=1, column=2)

    def create_client_window(self):
        CreateClientWindow(self)

    def edit_client_window(self):
        if self.treeview.focus():
            EditClientWindow(self)

    def delete(self):
        cliente = self.treeview.focus()
        if cliente:
            campos = self.treeview.item(cliente, 'values')
            confirmar = askokcancel(title='Confirmación', message=f'¿Borrar a {campos[1]} {campos[2]}?', icon=WARNING)
            if confirmar:
                self.treeview.delete(cliente)
                db.Clientes.borrar(campos[0])

class CreateClientWindow(Toplevel, CenterWidgetMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Crear cliente')
        self.build()
        self.center()
        self.transient(parent)
        self.grab_set()

    def build(self):
        frame_datos = Frame(self)
        frame_datos.pack(padx=20, pady=10)

        Label(frame_datos, text="DNI (2 ints y 1 upper char)").grid(row=0, column=0)
        Label(frame_datos, text="Nombre (2 a 30 chars)").grid(row=0, column=1)
        Label(frame_datos, text="Apellido (2 a 30 chars)").grid(row=0, column=2)

        self.dni = Entry(frame_datos)
        self.dni.grid(row=1, column=0)
        self.dni.bind("<KeyRelease>", lambda ev: self.validate(ev, 0))

        self.nombre = Entry(frame_datos)
        self.nombre.grid(row=1, column=1)
        self.nombre.bind("<KeyRelease>", lambda ev: self.validate(ev, 1))

        self.apellido = Entry(frame_datos)
        self.apellido.grid(row=1, column=2)
        self.apellido.bind("<KeyRelease>", lambda ev: self.validate(ev, 2))

        frame_botones = Frame(self)
        frame_botones.pack(pady=10)

        self.crear = Button(frame_botones, text="Crear", command=self.create_client, state=DISABLED)
        self.crear.grid(row=0, column=0)
        Button(frame_botones, text="Cancelar", command=self.close).grid(row=0, column=1)

        self.validaciones = [0, 0, 0]

    def validate(self, event, index):
        valor = event.widget.get()
        valido = helpers.dni_valido(valor, db.Clientes.lista) if index == 0 \
            else (valor.isalpha() and 2 <= len(valor) <= 30)
        event.widget.configure({"bg": "Green" if valido else "Red"})
        self.validaciones[index] = valido
        self.crear.config(state=NORMAL if self.validaciones == [1, 1, 1] else DISABLED)

    def create_client(self):
        self.master.treeview.insert('', 'end', iid=self.dni.get(),
                                    values=(self.dni.get(), self.nombre.get(), self.apellido.get()))
        db.Clientes.crear(self.dni.get(), self.nombre.get(), self.apellido.get())
        self.close()

    def close(self):
        self.destroy()
        self.update()

class EditClientWindow(Toplevel, CenterWidgetMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Actualizar cliente')
        self.build()
        self.center()
        self.transient(parent)
        self.grab_set()

    def build(self):
        frame = Frame(self)
        frame.pack(padx=20, pady=10)

        Label(frame, text="DNI (no editable)").grid(row=0, column=0)
        Label(frame, text="Nombre (2 a 30 chars)").grid(row=0, column=1)
        Label(frame, text="Apellido (2 a 30 chars)").grid(row=0, column=2)

        self.dni = Entry(frame)
        self.dni.grid(row=1, column=0)
        self.dni.config(state=DISABLED)

        self.nombre = Entry(frame)
        self.nombre.grid(row=1, column=1)
        self.nombre.bind("<KeyRelease>", lambda ev: self.validate(ev, 0))

        self.apellido = Entry(frame)
        self.apellido.grid(row=1, column=2)
        self.apellido.bind("<KeyRelease>", lambda ev: self.validate(ev, 1))

        cliente = self.master.treeview.focus()
        campos = self.master.treeview.item(cliente, 'values')
        self.dni.insert(0, campos[0])
        self.nombre.insert(0, campos[1])
        self.apellido.insert(0, campos[2])

        frame_botones = Frame(self)
        frame_botones.pack(pady=10)

        self.actualizar = Button(frame_botones, text="Actualizar", command=self.update_client)
        self.actualizar.grid(row=0, column=0)
        Button(frame_botones, text="Cancelar", command=self.close).grid(row=0, column=1)

        self.validaciones = [1, 1]

    def validate(self, event, index):
        valor = event.widget.get()
        valido = valor.isalpha() and 2 <= len(valor) <= 30
        event.widget.configure({"bg": "Green" if valido else "Red"})
        self.validaciones[index] = valido
        self.actualizar.config(state=NORMAL if self.validaciones == [1, 1] else DISABLED)

    def update_client(self):
        cliente = self.master.treeview.focus()
        self.master.treeview.item(cliente,
                                  values=(self.dni.get(), self.nombre.get(), self.apellido.get()))
        db.Clientes.modificar(self.dni.get(), self.nombre.get(), self.apellido.get())
        self.close()

    def close(self):
        self.destroy()
        self.update()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
