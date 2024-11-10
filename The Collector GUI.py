import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import shutil

# Dictionary to map OS choices to JSON file paths
os_json_files = {
    "Windows": "plugins/Windows_commands.json",
    "Debian-based Linux": "plugins/Debian_commands.json",
    "RedHat-based Linux": "plugins/RedHat_commands.json"
}

def load_commands(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def categorize_commands(commands_data):
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

    return must_commands, basic_commands, advanced_commands, hashing_command

def convert_to_batch(command):
    if isinstance(command, list):
        return command
    return command

def copy_modules_to_folder(folder_path):
    source_folder = os.path.join(os.path.dirname(__file__), "modules")
    destination_folder = os.path.join(folder_path, "modules")
    shutil.copytree(source_folder, destination_folder)

class CommandGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Generator")

        self.basic_vars = []
        self.advanced_vars = []

        self.basic_commands = []
        self.advanced_commands = []
        self.must_commands = []
        self.hashing_command = []

        self.selected_os = tk.StringVar(value="Windows")
        self.select_os_and_load_commands()

    def select_os_and_load_commands(self):
        os_selection_dialog = tk.Toplevel(self.root)
        os_selection_dialog.title("Select OS")
        tk.Label(os_selection_dialog, text="Select your OS:", font=("Segoe UI", 10)).pack(pady=10)

        os_menu = tk.OptionMenu(os_selection_dialog, self.selected_os, *os_json_files.keys())
        os_menu.config(font=("Segoe UI", 10))
        os_menu.pack(pady=10)

        tk.Button(os_selection_dialog, text="OK", command=lambda: self.load_selected_os(os_selection_dialog), font=("Segoe UI", 10)).pack(pady=10)

        os_selection_dialog.transient(self.root)
        os_selection_dialog.grab_set()
        self.root.wait_window(os_selection_dialog)

    def load_selected_os(self, dialog):
        selected_os = self.selected_os.get()
        if selected_os in os_json_files:
            file_path = os.path.join(os.path.dirname(__file__), os_json_files[selected_os])
            commands_data = load_commands(file_path)
            self.must_commands, self.basic_commands, self.advanced_commands, self.hashing_command = categorize_commands(commands_data)
            dialog.destroy()
            self.setup_full_gui()
        else:
            self.show_custom_message("Error", "Invalid OS selected.")
            dialog.destroy()
            self.root.destroy()

    def setup_full_gui(self):
        num_basic = len(self.basic_commands)
        num_advanced = len(self.advanced_commands)
        rows_needed = max((num_basic + 1), ((num_advanced + 3) // 4) + 1)
        
        window_height = 100 + rows_needed * 30
        window_width = 800
        self.root.geometry(f"{window_width}x{window_height}")

        self.basic_frame = tk.Frame(self.root)
        self.basic_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        tk.Label(self.basic_frame, text="Basic Commands", font=("Segoe UI", 10, "bold")).pack()
        self.basic_vars.clear()
        for cmd in self.basic_commands:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.basic_frame, text=cmd["Command_Name"], variable=var, font=("Segoe UI", 9))
            chk.pack(anchor='w', padx=10, pady=2)
            self.basic_vars.append(var)

        self.advanced_frame = tk.Frame(self.root)
        self.advanced_frame.grid(row=0, column=1, sticky="nsew")
        self.root.grid_columnconfigure(1, weight=1)

        tk.Label(self.advanced_frame, text="Advanced Commands", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=4)

        self.advanced_vars.clear()
        for index, cmd in enumerate(self.advanced_commands):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.advanced_frame, text=cmd["Command_Name"], variable=var, font=("Segoe UI", 9))
            chk.grid(row=(index // 4) + 1, column=index % 4, sticky='w', padx=10, pady=2)
            self.advanced_vars.append(var)

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        tk.Button(self.buttons_frame, text="Select All", command=self.select_all, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Select None", command=self.select_none, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Generate Batch", command=self.generate_batch, font=("Segoe UI", 10)).pack(side=tk.RIGHT, padx=5, pady=5)

        self.footer_label = tk.Label(self.root, text="Created by Feras Faqeeh", font=("Segoe UI", 9))
        self.footer_label.grid(row=2, column=0, columnspan=2, pady=10)

    def select_all(self):
        for var in self.basic_vars + self.advanced_vars:
            var.set(True)

    def select_none(self):
        for var in self.basic_vars + self.advanced_vars:
            var.set(False)

    def generate_batch(self):
        selected_commands = ["@echo off"]

        for cmd in self.must_commands:
            selected_commands.extend(convert_to_batch(cmd["Command"]))

        for var, cmd in zip(self.basic_vars, self.basic_commands):
            if var.get():
                selected_commands.extend(convert_to_batch(cmd["Command"]))

        for var, cmd in zip(self.advanced_vars, self.advanced_commands):
            if var.get():
                selected_commands.extend(convert_to_batch(cmd["Command"]))

        for cmd in self.hashing_command:
            selected_commands.extend(convert_to_batch(cmd["Command"]))

        selected_commands.append("@pause")

        folder_path = filedialog.asksaveasfilename(
            title="Save Batch File",
            defaultextension="",
            filetypes=[("Folder", "")],
            initialfile="NewFolder"
        )
        
        if folder_path:
            folder_dir = os.path.splitext(folder_path)[0]
            os.makedirs(folder_dir, exist_ok=True)
            batch_file_path = os.path.join(folder_dir, f"{os.path.basename(folder_dir)}.bat")
            with open(batch_file_path, "w") as file:
                file.write("\n".join(selected_commands))
            
            copy_modules_to_folder(folder_dir)

            self.show_custom_message("Success", f"Batch script generated in {folder_dir}")

    def show_custom_message(self, title, message):
        custom_dialog = tk.Toplevel(self.root)
        custom_dialog.title(title)
        custom_dialog.geometry("600x200")  # Adjust width and height as needed
        tk.Label(custom_dialog, text=message, font=("Segoe UI", 10)).pack(padx=20, pady=20)
        tk.Button(custom_dialog, text="OK", command=custom_dialog.destroy, font=("Segoe UI", 10)).pack(pady=10)
        custom_dialog.transient(self.root)
        custom_dialog.grab_set()
        self.root.wait_window(custom_dialog)

root = tk.Tk()
app = CommandGenerator(root)
root.mainloop()
