# The-Collector
# The Collector

The Collector is a Python application that generates batch scripts using a GUI interface. It categorizes commands from a JSON file and allows users to select which commands to include in the generated script.

## Features

- **Command Loading**: Reads commands from a `commands.json` file.
- **Categorization**: Commands are organized into must-have, basic, and advanced categories.
- **User-Friendly Interface**: GUI for selecting commands.
- **Batch Script Generation**: Creates a batch file with selected commands.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
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


## File Structure

- `the_collector.py`: Main application script.
- `commands.json`: JSON file containing command definitions.

## Contributing

Contributions are welcome! Please submit issues or pull requests.

## License

This project is licensed under the MIT License.


