from tkinter import *
from tkinter import filedialog

def browseFiles(var):
    print(var)

    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Image files",
                                                      "*.png*"),
                                                     ("all files",
                                                      "*.*")))

    if var==("PY_VAR3"):
        filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Video files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    label_file_explorer.configure(text="Wybrano plik: " + filename)

def startprogram(var):
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))
    label_file_explorer.configure(text="Wybrano plik: " + filename)


# Create the root window
window = Tk()

var = IntVar()

# Set window title
window.title('Aplikacja to rozpoznawania i tłumaczenia języka migowego')

# Set window size
window.geometry("600x200")

# Set window background color
window.config(background="white")

# Create a File Explorer label
label_file_explorer = Label(window,
                            text="Nie wybrano pliku",
                            width=60, height=2,
                            fg="blue")

button_explore = Button(window,
                        text="Wybierz plik",
                        command=lambda: browseFiles(var))

button_start = Button(window,
                        text="Uruchom tłumaczenie",
                        command=lambda: startprogram(IntVar()))

button_exit = Button(window,
                     text="Wyjście",
                     command=exit)


label_file_explorer.grid(column=1, row=1)

button_explore.grid(column=1, row=2)

button_start.grid(column=1, row=4)

button_exit.grid(column=1, row=6)


rad1 = Radiobutton(window,text='Zdjęcie',variable=var, value=1)

rad2 = Radiobutton(window,text='Nagranie wideo',variable=var, value=2)

rad3 = Radiobutton(window,text='Obraz z kamery', variable=var, value=3)

rad1.grid(column=0, row=0)

rad2.grid(column=1, row=0)

rad3.grid(column=2, row=0)

# Let the window wait for any events
print(IntVar().get())
window.mainloop()





