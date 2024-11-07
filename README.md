# The-Collector

The Collector is a bash generator. It categorizes commands from a JSON file and allows users to select which commands to include in the generated bash script.

## Features

- **Command Loading**: Reads commands from a `Windows_commands.json` file.
- **Categorization**: Commands are organized into must-have, basic, and advanced categories.
- **User-Friendly Interface**: GUI for selecting commands or cmd using The-collector.py.
- **Batch Script Generation**: Creates a batch file with selected commands.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/FerasCodes/The-Collector.git
   cd The-Collector
2. **Ensure Python is Installed**:
The application requires Python 3.x.

## Usage

1. **Run the Application**:
   
  a. For the GUI 
   ```bash
   python The Collector GUI.py
```
  b. For the terminal 
  ```bash
  python The-Collector.py

```

4. **Interact with the GUI**:
Select basic and advanced commands.
Use "Select All" or "Select None" for convenience.
Click "Generate Batch" to create your batch file.


## Example `Windows_commands.json` Structure and how to add your own commands

```json
[
  {
    "Command_Name": "Creating a directory",
    "Category": "Must",
    "Command": []
  },
  {
    "Command_Name": "Network information",
    "Category": "Basic",
    "Command": []
  }
]
```
1- Add your command within the "Command" array for the relevant "Command_Name".
2- Ensure each command is a string and placed within quotes.

Example:

```json
{
  "Command_Name": "List directory contents",
  "Category": "Optional",
  "Command": [
    "dir"
    ]
}
```
## File Structure

- `the_collector.py`: Main application script.
- `Windows_commands.json`: JSON file containing command definitions.

## GUI 
![image](https://github.com/user-attachments/assets/8affe9b1-bdb8-4c5a-80db-f2799774258d)


## Contributing

This repository serves as a place for community to add their source in the json file for use with The-Collector

## License

This project is licensed under the MIT License.


