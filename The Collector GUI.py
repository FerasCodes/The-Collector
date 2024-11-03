import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

# Load JSON data from commands.json
def load_commands():
    file_path = os.path.join(os.path.dirname(__file__), "src", "Windows_commands.json")
    with open(file_path, "r") as file:
        return json.load(file)

commands_data = load_commands()
must_commands = []
basic_commands = []
advanced_commands = []
hashing_command = []
for cmd in commands_data:
    if cmd["Command_Name"] == "Creating a directory":
        must_commands.append(cmd)
    elif cmd["Command_Name"] == "Hashing generated files":
        hashing_command.append(cmd)
    elif cmd["category"] == "Basic":
        basic_commands.append(cmd)
    elif cmd["category"] == "Advance":
        advanced_commands.append(cmd)

basic_commands.sort(key=lambda x: x["Command_Name"])
advanced_commands.sort(key=lambda x: x["Command_Name"])

def convert_to_batch(command):
    if isinstance(command, list):
        return command
    return command

class CommandGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Generator")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2

        root.geometry(f"{window_width}x{window_height}")

        self.basic_vars = []
        self.advanced_vars = []


        basic_frame = tk.Frame(root)
        basic_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        tk.Label(basic_frame, text="Basic Commands", font=("Times New Romens", 12, "bold")).pack()
        for cmd in basic_commands:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(basic_frame, text=cmd["Command_Name"], variable=var)
            chk.pack(anchor='w')
            self.basic_vars.append(var)


        advanced_frame = tk.Frame(root)
        advanced_frame.grid(row=0, column=1, sticky="nsew")
        root.grid_columnconfigure(1, weight=1)

        tk.Label(advanced_frame, text="Advanced Commands", font=("Times New Romens", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky='n', pady=10)


        for index, cmd in enumerate(advanced_commands):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(advanced_frame, text=cmd["Command_Name"], variable=var)
            chk.grid(row=(index // 4) + 1, column=index % 4, sticky='w', padx=10, pady=5)
            self.advanced_vars.append(var)


        buttons_frame = tk.Frame(root)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        tk.Button(buttons_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(buttons_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(buttons_frame, text="Generate Batch", command=self.generate_batch).pack(side=tk.RIGHT, padx=5, pady=5)

    def select_all(self):
        for var in self.basic_vars + self.advanced_vars:
            var.set(True)

    def select_none(self):
        for var in self.basic_vars + self.advanced_vars:
            var.set(False)

    def generate_batch(self):
        selected_commands = ["@echo off"]


        for cmd in must_commands:
            selected_commands.extend(convert_to_batch(cmd["Command"]))

        for var, cmd in zip(self.basic_vars, basic_commands):
            if var.get():
                selected_commands.extend(convert_to_batch(cmd["Command"]))

        for var, cmd in zip(self.advanced_vars, advanced_commands):
            if var.get():
                selected_commands.extend(convert_to_batch(cmd["Command"]))


        for cmd in hashing_command:
            selected_commands.extend(convert_to_batch(cmd["Command"]))

        selected_commands.append("@pause")


        file_path = filedialog.asksaveasfilename(defaultextension=".bat", filetypes=[("Batch files", "*.bat")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("\n".join(selected_commands))

            messagebox.showinfo("Success", f"Batch script generated as {file_path}")


root = tk.Tk()
app = CommandGenerator(root)
root.mainloop()
