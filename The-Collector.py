#!/usr/bin/env python3
import json
import os
import argparse

def load_commands():
    file_path = os.path.join(os.path.dirname(__file__), "plugins", "Windows_commands.json")
    with open(file_path, "r") as file:
        return json.load(file)

def convert_to_batch(command):
    if isinstance(command, list):
        return command
    return command

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

def generate_batch_file(selected_basic, selected_advanced, file_path):
    selected_commands = ["@echo off"]
    for cmd in must_commands:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in selected_basic:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in selected_advanced:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    for cmd in hashing_command:
        selected_commands.extend(convert_to_batch(cmd["Command"]))
    selected_commands.append("@pause")
    with open(file_path, "w") as file:
        file.write("\n".join(selected_commands))

def list_commands():
    basic_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(basic_commands))
    advanced_list = "\n".join(f"{i+1}. {cmd['Command_Name']}" for i, cmd in enumerate(advanced_commands))
    return f"Basic Commands:\n{basic_list}\n\nAdvanced Commands:\n{advanced_list}"

def main():
    parser = argparse.ArgumentParser(
        description="Command Generator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--basic', nargs='*', type=int, default=[], help='Select basic commands by index (e.g., 1 2 3)')
    parser.add_argument('--advanced', nargs='*', type=int, default=[], help='Select advanced commands by index (e.g., 1 2 3)')
    parser.add_argument('--output', required=True, help='Output file path for the batch script')

    parser.epilog = list_commands()

    args = parser.parse_args()

    selected_basic = [basic_commands[i - 1] for i in args.basic]
    selected_advanced = [advanced_commands[i - 1] for i in args.advanced]

    generate_batch_file(selected_basic, selected_advanced, args.output)

if __name__ == "__main__":
    main()
