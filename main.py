from ui.app import App
import tkinter as tk
import ui.controls
print(ui.controls.__file__)

root = tk.Tk()
app = App(root)
root.mainloop()