from tkinter import *

class CenterWidgetMixin:
    def center(self,):
        self.update()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))
        self.geometry(f"{w}x{h}+{x}+{y}")

class MainWindow(tk,CenterWidgetMixin):
    def __init__(self):
        super().__init__()
        self.title('Gestor de clientes')
        self.build()
        self.center()
    def build(self):
        button = Button(self.root, text="Hola", command=self.hola)
        button.pack()
    def hola(self):
        print("¡Hola mundo!")
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
