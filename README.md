# The-Collector

The Collector a bash Generator. It categorizes commands from a JSON file and allows users to select which commands to include in the generated bash script.

## Features

- **Command Loading**: Reads commands from a `commands.json` file.
- **Categorization**: Commands are organized into must-have, basic, and advanced categories.
- **User-Friendly Interface**: GUI for selecting commands.
- **Batch Script Generation**: Creates a batch file with selected commands.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/FerasCodes/The-Collector.git
   cd The-Collector
2. **Ensure Python is Installed**:
The application requires Python 3.x.

## Usage

1. **Prepare `commands.json`**:
   - Place `commands.json` in the same directory as the script.
   - Ensure it contains commands and their categories.

2. **Run the Application**:
   ```bash
   python the_collector.py

3. **Interact with the GUI**:
Select basic and advanced commands.
Use "Select All" or "Select None" for convenience.
Click "Generate Batch" to create your batch file.


## Example `commands.json` Structure

```json
[
  {
    "Command_Name": "Creating a directory",
    "Command": ["mkdir example"],
    "category": "Basic"
  },
  {
    "Command_Name": "Hashing generated files",
    "Command": ["certutil -hashfile example.txt SHA256"],
    "category": "Advance"
  }
]
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


