#!/usr/bin/env python3
import json
import os
import argparse
import shutil
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

os_json_files = {
    "Windows": os.path.join(script_dir, "plugins", "Windows_commands.json"),
    "Linux": os.path.join(script_dir, "plugins", "Linux_commands.json")
}

def load_commands(os_choice):
    file_path = os_json_files.get(os_choice)
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file for {os_choice} not found at {file_path}.")
    with open(file_path, "r") as file:
        return json.load(file)

def convert_to_batch(command):
    if isinstance(command, list):
        return command
    return command

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

def copy_modules_to_folder(folder_path):
    source_folder = os.path.join(os.path.dirname(__file__), "modules")
    destination_folder = os.path.join(folder_path, "modules")
    shutil.copytree(source_folder, destination_folder)

def generate_script_file(selected_basic, selected_advanced, folder_name, must_commands, hashing_command, os_choice):
    folder_path = os.path.abspath(folder_name)
    os.makedirs(folder_path, exist_ok=True)


    extension = ".bat" if os_choice == "Windows" else ".sh"
    script_file_path = os.path.join(folder_path, f"{os.path.basename(folder_name)}{extension}")

 
    if os_choice == "Windows":
        selected_commands = ["@echo off"]
    else:
        selected_commands = ["#!/bin/bash"]

    for cmd in must_commands:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in selected_basic:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in selected_advanced:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in hashing_command:
        selected_commands.extend(convert_to_batch(cmd["Command"]))

    if os_choice == "Windows":
        selected_commands.append("@pause")

    with open(script_file_path, "w") as file:
        file.write("\n".join(selected_commands))

    if os_choice != "Windows":
        os.chmod(script_file_path, 0o755)  

    copy_modules_to_folder(folder_path)
    print(f"Script and modules copied to {folder_path}")

def list_commands(basic_commands, advanced_commands):
    basic_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(basic_commands))
    advanced_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(advanced_commands))
    return f"Basic Commands:\n{basic_list}\n\nAdvanced Commands:\n{advanced_list}"

def handle_help_with_os(args):
    """Handles the case where -h is used with -o."""
    if args.os:
        try:
            commands_data = load_commands(args.os)
            _, basic_commands, advanced_commands, _ = categorize_commands(commands_data)
            print("Available Commands:\n")
            print(list_commands(basic_commands, advanced_commands))
        except FileNotFoundError as e:
            print(str(e))
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Command Generator",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False  
    )
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
    parser.add_argument('-o', '--os', choices=os_json_files.keys(), help='Select the operating system')
    parser.add_argument('-b', '--basic', nargs='*', type=int, default=[], help='Select basic commands by index (e.g., 1 2 3)')
    parser.add_argument('-a', '--advanced', nargs='*', type=int, default=[], help='Select advanced commands by index (e.g., 1 2 3)')
    parser.add_argument('-n', '--name', help='Name for the folder and script file')

    args = parser.parse_args()

    if args.help:
        if args.os:
            handle_help_with_os(args)
        else:
            parser.print_help()
            print("\nHint: Use -o to specify the OS for a list of available commands.")
            sys.exit(0)

    if not args.os:
        parser.error("The -o/--os argument is required.")

    if not args.name:
        parser.error("The -n/--name argument is required.")

    commands_data = load_commands(args.os)
    must_commands, basic_commands, advanced_commands, hashing_command = categorize_commands(commands_data)

    selected_basic = [basic_commands[i - 1] for i in args.basic]
    selected_advanced = [advanced_commands[i - 1] for i in args.advanced]

    generate_script_file(selected_basic, selected_advanced, args.name, must_commands, hashing_command, args.os)

if __name__ == "__main__":
    main()
