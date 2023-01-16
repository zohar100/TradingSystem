import tkinter
from viewer import Viewer

root = tkinter.Tk()
root.geometry("750x750")
root.title("Viewer")

viewer = Viewer(root)
viewer.mainloop()