import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font 
from nfa_code import NFAfromRegex, Automata, BuildAutomata
import graphviz
from PIL import Image, ImageTk
import os

def build_nfa():
    regex = regex_entry.get()
    if regex:
        nfa_builder = NFAfromRegex(regex)
        nfa = nfa_builder.getNFA()
        output_label.config(text="NFA Built Successfully.")

        # Generate DOT code
        dot_code = nfa.to_dot()

        # Render DOT code to PNG image
        graph = graphviz.Source(dot_code, format='png')
        graph.render(filename='nfa_diagram', directory='.')

        # Display the image in GUI
        nfa_image = Image.open('nfa_diagram.png')
        nfa_image = nfa_image.resize((400, 400), Image.ANTIALIAS)  # Resize the image as needed
        nfa_photo = ImageTk.PhotoImage(nfa_image)

        # Create a label to display the image
        nfa_image_label = tk.Label(root, image=nfa_photo)
        nfa_image_label.image = nfa_photo  # Keep a reference to prevent garbage collection
        nfa_image_label.pack()
    else:
        messagebox.showerror("Error", "Please enter a regex.")

def test_string():
    test_input = test_entry.get()
    if test_input:
        nfa_builder = NFAfromRegex(regex_entry.get())  # Create an NFA builder from the regex
        nfa = nfa_builder.getNFA()  # Get the NFA from the builder
        if nfa.test_string(test_input):
            output_label.config(text=f"'{test_input}' is valid for the regex '{regex_entry.get()}'.")
        else:
            output_label.config(text=f"'{test_input}' is not valid for the regex '{regex_entry.get()}'.")
    else:
        messagebox.showerror("Error", "Please enter a string to test.")

# Create the main window
root = tk.Tk()
root.title("NFA Builder")

# Set window size
window_width = 800
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width / 2) - (window_width / 2)
y_coordinate = (screen_height / 2) - (window_height / 2)
root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

# Set background color
root.config(bg='#223D60')  # Change the hex value to the color you desire

# Create and place widgets
font_style = Font(family="Helvetica", size=20, weight="bold")  # Create a Font object
regex_label = tk.Label(root, text="Enter the regex:", font=font_style, bg="#223D60",fg="white")  # Set background color
regex_label.pack(padx=20, pady=10) 

regex_entry = tk.Entry(root, width=30)  # Increase width of the text field
regex_entry.pack()

font_style1 = Font(family="Helvetica", size=15)
build_button = tk.Button(root, text="Build NFA",font=font_style1, command=build_nfa, bg="#ae202c", fg="white")
build_button.pack(padx=20, pady=20)

font_style = Font(family="Helvetica", size=20, weight="bold",)  # Create a Font object
regex_label = tk.Label(root, text="Please Enter a string to test!:",  font=font_style, bg="#223D60",fg="white")  # Set background color
regex_label.pack(padx=20, pady=10) 

test_entry = tk.Entry(root, width=30)  # Increase width and height
test_entry.pack()

font_style = Font(family="Helvetica", size=15,)
test_button = tk.Button(root, text="Test String", command=test_string, font=font_style, bg="#ae202c",fg="white")
test_button.pack(padx=20, pady=30)

output_label = tk.Label(root, text="",bg="#223D60",font=font_style,fg="#F5EA05")
output_label.pack()

# Start the main loop
root.mainloop()

