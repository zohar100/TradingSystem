import tkinter

class Viewer(tkinter.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)
        self.pack()

        self.text_input_label = tkinter.Label(text="Enter name")
        self.text_input_label.pack(padx=100)

        self.text_input = tkinter.Entry()
        self.text_input.pack()


root = tkinter.Tk()
root.geometry("400x400")
root.title("Viewer")

viewer = Viewer(root)
viewer.mainloop()