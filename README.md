# Personal Assistant Bot

A sophisticated command-line application designed to streamline personal information management. This assistant helps you manage a digital address book and a notebook, ensuring your data is always organized, accessible, and persistent.

## Table of Contents

- [About The Project](#about-the-project)
- [Core Features](#core-features)
- [Architectural Overview](#architectural-overview)
  - [Data Modeling (`models.py`)](#data-modeling-modelspy)
  - [Command Handling (`main.py`)](#command-handling-mainpy)
  - [Error Handling](#error-handling)
  - [Data Persistence](#data-persistence)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Python Version Management (Advanced)](#python-version-management-advanced)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Command Reference](#command-reference)
- [Testing](#testing)

## About The Project

The Personal Assistant Bot is a powerful tool for managing contacts and notes directly from your terminal. It was built to provide a fast, efficient, and keyboard-driven interface for common organizational tasks. The application saves all data locally, ensuring privacy and offline access. It is designed with a clean, modular architecture, making it both easy to use and straightforward to extend.

## Core Features

- **Contact Management**: Full CRUD (Create, Read, Update, Delete) functionality for contacts, including support for multiple phone numbers, email, and a physical address.
- **Birthday Tracking**: Add birthdays to contacts and get a list of upcoming birthdays within a specified number of days, with intelligent handling for weekend dates.
- **Note Organization**: Full CRUD functionality for notes, which include a title, content, and searchable tags.
- **Powerful Search**: Search contacts by name, phone number, or email. Search notes by tag.
- **Input Validation**: Ensures data integrity by validating inputs like phone numbers (10 digits), email formats, and birthday dates.
- **Data Persistence**: Automatically saves all contacts and notes to a local file (`assistant_data.pkl`) upon exit and reloads them at the start of a new session.
- **End-to-End Testing**: Includes a comprehensive test script (`demo.py`) that verifies all application functionality, edge cases, and error handling.

## Architectural Overview

The application is built on a modular and object-oriented architecture, separating concerns into distinct components for clarity and maintainability.

### Data Modeling (`models.py`)

The core logic resides in the data models, which are responsible for representing and validating all information.

- **Field Classes**: Generic `Field` class with specialized subclasses like `Name`, `Phone`, `Email`, and `Birthday`. Each subclass contains its own validation logic (e.g., `Phone` ensures a 10-digit number, `Birthday` validates the date format and ensures it's not in the future). This design makes it easy to add new validated fields.
- **Record Class**: Represents a single contact. It composes `Field` objects (one `Name`, a list of `Phone` objects, one `Email`, etc.) and contains the business logic for contact-related operations like adding/editing phones or birthdays.
- **AddressBook Class**: A dictionary-like container that manages a collection of `Record` objects. It provides high-level methods for adding, finding, and deleting contacts, as well as more complex operations like `get_upcoming_birthdays`.
- **Note & NoteBook Classes**: Similar to the contact models, a `Note` class represents a single note with a title, content, and a set of tags. The `NoteBook` class manages the collection of notes.

### Command Handling (`main.py`)

The main entry point handles the user-facing command-line interface.

- **Main Loop**: A `while True` loop continuously prompts the user for input.
- **Input Parsing (`parse_input`)**: User input is split into a command and its arguments. This function is responsible for interpreting the user's intent.
- **Command Dispatcher**: A dictionary (`commands_map`) maps command strings (e.g., "add", "show") to their corresponding handler functions. This provides a clean and scalable way to manage commands.
- **Handler Functions**: Each command has a dedicated function (e.g., `add_contact`, `show_all_notes`) that takes the user's arguments and interacts with the `AddressBook` or `NoteBook` to perform the requested action.

### Error Handling

Robust error handling is achieved via a custom decorator and a hierarchy of specific exceptions.

- **`@input_error` Decorator**: This decorator wraps almost all command handler functions. It provides a centralized try-except block to catch anticipated errors (e.g., `ValueError` for wrong argument count, `ContactNotFoundError`) and prints a user-friendly message instead of crashing the application.
- **Custom Exceptions**: Defined in `models.py`, exceptions like `InvalidPhoneFormatError`, `ContactNotFoundError`, and `NoteNotFoundError` allow for specific error conditions to be caught and handled gracefully.

### Data Persistence

The application state is saved and loaded using Python's `pickle` module in `serialization_utils.py`.

- **`save_data()`**: This function takes the `AddressBook` and `NoteBook` objects, bundles them into a tuple, and serializes them to the `assistant_data.pkl` file. It is called automatically when the user exits the application.
- **`load_data()`**: This function is called at startup. It attempts to open and deserialize `assistant_data.pkl`. If the file doesn't exist or is corrupted, it gracefully returns new, empty `AddressBook` and `NoteBook` instances, ensuring the application can always start.

## Project Structure

The project is organized into a Python package for clean separation of concerns and proper installability.

```
.
├── assistant/
│   ├── __init__.py      # Makes 'assistant' a Python package
│   ├── main.py          # Main application logic, CLI, and command handlers
│   ├── models.py        # Core data models and business logic (Record, Note, etc.)
│   └── serialization_utils.py # Handles saving/loading data
├── demo.py              # End-to-end test script
├── README.md            # This file
├── setup.py             # Package installation script
└── .gitignore           # Git ignore file
```

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.10 or newer

### Python Version Management (Advanced)

If your system's default Python version is older than 3.10, you can use a tool like `pyenv` to install and manage different Python versions without interfering with your system.

1.  **Install `pyenv`**: Follow the official installation guide for your OS.
2.  **Install a specific Python version**:
    ```sh
    pyenv install 3.10.12
    ```
3.  **Set the local Python version for the project**: Navigate to the project directory and run:
    ```sh
    pyenv local 3.10.12
    ```
    This creates a `.python-version` file, and `pyenv` will automatically use this version whenever you are in this directory.

### Installation

1.  **Clone the repository**:
    ```sh
    git clone <your-repository-url>
    cd goit-pycore-final-project
    ```
2.  **Create and activate a virtual environment**:
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install the project in editable mode**:
    This command uses `setup.py` to install the `assistant` package and its dependencies, creating the `assistant-bot` command-line entry point. The `-e` flag makes the installation "editable," so any changes you make to the source code will be immediately effective without needing to reinstall.
    ```sh
    pip install -e .
    ```

## Usage

### Running the Application

Once installed, you can run the assistant from anywhere in your terminal (as long as the virtual environment is active):

```sh
assistant-bot
```

You will be greeted with a welcome message and a prompt to enter a command.

### Command Reference

Here is a complete list of available commands.

| Command             | Arguments                         | Example                               | Description                                        |
| :------------------ | :-------------------------------- | :------------------------------------ | :------------------------------------------------- |
| `hello`             |                                   | `hello`                               | Displays the command manual.                       |
| `add`               | `<Name> <Phone> [Email] [Address]`| `add John 1234567890 john@mail.com`   | Adds a new contact or phone.                       |
| `change`            | `<Name> <Old Phone> <New Phone>`  | `change John 1234567890 0987654321`   | Updates an existing contact's phone.               |
| `show`              | `<Name>`                          | `show John`                           | Shows a contact's full details.                    |
| `all`               |                                   | `all`                                 | Lists all saved contacts.                          |
| `delete`            | `<Name>`                          | `delete John`                         | Deletes a contact.                                 |
| `add-birthday`      | `<Name> <DD.MM.YYYY>`             | `add-birthday John 01.01.1990`        | Adds a contact's birthday.                         |
| `show-birthday`     | `<Name>`                          | `show-birthday John`                  | Shows a contact's birthday.                        |
| `birthdays`         | `[days]`                          | `birthdays 14`                        | Shows upcoming birthdays (default: 7 days).        |
| `search`            | `<query>`                         | `search John`                         | Searches contacts by name, phone, or email.        |
| `add-note`          | `<title> <content> [#tags]`       | `add-note Shopping Eggs Milk #urgent` | Adds a new note with optional tags.                |
| `edit-note`         | `<title> <new_content>`           | `edit-note Shopping Milk, Tea`        | Edits an existing note's content.                  |
| `delete-note`       | `<title>`                         | `delete-note Shopping`                | Deletes a note.                                    |
| `add-tag`           | `<title> [#tag1] [#tag2]`         | `add-tag Shopping #urgent #home`      | Adds tags to an existing note.                     |
| `remove-tag`        | `<title> <#tag>`                  | `remove-tag Shopping #urgent`         | Removes a tag from an existing note.               |
| `find-notes-by-tag` | `<#tag>`                          | `find-notes-by-tag #urgent`           | Shows notes filtered by a specific tag.            |
| `show-notes-sorted` | `[title/tags]`                    | `show-notes-sorted tags`              | Shows all notes sorted by title or tag count.      |
| `show-all-notes`    |                                   | `show-all-notes`                      | Lists all notes.                                   |
| `close` / `exit`    |                                   | `close`                               | Exits the bot and saves all data.                  |

## Testing

The project includes a comprehensive end-to-end test script that simulates user commands and verifies the entire application's functionality, including error conditions and data persistence.

To run the test script, execute the following command from the project's root directory:

```sh
python demo.py
```

The script will perform a series of operations, printing its progress and indicating whether the results are successful or are expected exceptions. It cleans up any existing data file before it runs to ensure a consistent test environment.
