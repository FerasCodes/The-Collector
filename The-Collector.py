#!/usr/bin/env python3
import json
import os
import argparse
import shutil

# Dictionary to map OS choices to JSON file paths
os_json_files = {
    "Windows": "plugins/Windows_commands.json",
    "Debian-based Linux": "plugins/Debian_commands.json",
    "RedHat-based Linux": "plugins/RedHat_commands.json"
}

def load_commands(os_choice):
    file_path = os_json_files.get(os_choice)
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file for {os_choice} not found.")
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

    # Determine file extension based on OS
    extension = ".bat" if os_choice == "Windows" else ".sh"
    script_file_path = os.path.join(folder_path, f"{os.path.basename(folder_name)}{extension}")

    # Start commands based on OS
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
        os.chmod(script_file_path, 0o755)  # Make the script executable

    copy_modules_to_folder(folder_path)
    print(f"Script and modules copied to {folder_path}")

def list_commands(basic_commands, advanced_commands):
    basic_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(basic_commands))
    advanced_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(advanced_commands))
    return f"Basic Commands:\n{basic_list}\n\nAdvanced Commands:\n{advanced_list}"

def main():
    parser = argparse.ArgumentParser(
        description="Command Generator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-o', '--os', choices=os_json_files.keys(), required=True, help='Select the operating system')
    parser.add_argument('-b', '--basic', nargs='*', type=int, default=[], help='Select basic commands by index (e.g., 1 2 3)')
    parser.add_argument('-a', '--advanced', nargs='*', type=int, default=[], help='Select advanced commands by index (e.g., 1 2 3)')
    parser.add_argument('-n', '--name', required=True, help='Name for the folder and script file')

    args = parser.parse_args()

    commands_data = load_commands(args.os)
    must_commands, basic_commands, advanced_commands, hashing_command = categorize_commands(commands_data)

    parser.epilog = list_commands(basic_commands, advanced_commands)

    selected_basic = [basic_commands[i - 1] for i in args.basic]
    selected_advanced = [advanced_commands[i - 1] for i in args.advanced]

    generate_script_file(selected_basic, selected_advanced, args.name, must_commands, hashing_command, args.os)

if __name__ == "__main__":
    main()
