from Tkinter import Tk, Label, Button, StringVar

class oscGUI:
    LABEL_TEXT = [
        "hellu! do not worry, i am a very nice computer, i am here to help",
        "please be more careful where u click, that hurt"
    ]
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label_index = 0
        self.label_text = StringVar()
        self.label_text.set(self.LABEL_TEXT[self.label_index])
        self.label = Label(master, textvariable=self.label_text)
        self.label.bind("<Button-1>", self.cycle_label_text)
        self.label.pack()

        self.greet_button = Button(
        	self.master, text="Greet", command=self.greet
        )
        self.greet_button.pack()

        self.close_button = Button(
        	self.master, text="Close", command=self.master.quit
        )
        self.close_button.pack()

        self.ipAddresses = []
        self.ipLabels = []

        self.master.after(0, self.update)

    def greet(self):
        print("Greetings!")

    def cycle_label_text(self, event):
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT) # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])

    def update(self):
    	self.ipLabels.append(Label(
    		self.master, text="new ting"
    	))
        self.ipLabels[-1].pack()
        self.master.after(1000, self.update)

root = Tk()
my_gui = oscGUI(root)
root.mainloop()