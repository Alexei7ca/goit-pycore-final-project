# Personal Assistant - Graphical User Interface (GUI) Guide

This document provides specific instructions for setting up and running the graphical user interface for the Personal Assistant application.

## Table of Contents

- [GUI Overview](#gui-overview)
- [Critical Prerequisite: Python with Tkinter/Tcl Support](#critical-prerequisite-python-with-tkintertcl-support)
- [Step-by-Step Installation](#step-by-step-installation)
- [Running the Application](#running-the-application)
- [GUI Features](#gui-features)

## GUI Overview

The GUI provides a user-friendly, visual way to interact with your address book and notes. It is built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), which provides a modern look and feel. All functionality from the command-line version is available through an intuitive, clickable interface.

## Critical Prerequisite: Python with Tkinter/Tcl Support

The GUI depends on a Python library called **Tkinter**. Tkinter is a standard Python library, but it requires a separate toolkit called **Tcl/Tk** to be available on your operating system when Python is first installed.

Some installation methods, particularly using `pyenv` on a fresh macOS system, may build and install a version of Python that **does not include Tkinter support**, which will cause the GUI to fail on launch.

**The most reliable way to ensure you have the necessary toolkit is to use the official Python installer.**

## Step-by-Step Installation

Follow these steps to set up your environment correctly for the GUI.

### Step 1: Install Python from python.org

If you have encountered errors related to `_tkinter`, or to be safe, download and install Python directly from the official website. This will ensure the Tcl/Tk toolkit is correctly bundled.

- **Download Link**: [Python 3.14.0 macOS Installer](https://www.python.org/ftp/python/3.14.0/python-3.14.0-macos11.pkg) (or a newer version)

Run the downloaded installer and complete all its steps.

### Step 2: Identify the Path to the New Python

The official installer typically places the new Python executable in `/usr/local/bin/`. You can verify this by opening a **new** terminal window and running:

```sh
which python3.14
```

This should output a path like `/usr/local/bin/python3.14`. This is the path we will use to create our virtual environment.

### Step 3: Create and Activate the Virtual Environment

Navigate to the project directory and create a new virtual environment, explicitly telling it to use the Python you just installed.

```sh
# Navigate to your project folder
cd /path/to/your/goit-pycore-final-project

# Create the virtual environment using the specific Python path
/usr/local/bin/python3.14 -m venv venv

# Activate the new environment
source venv/bin/activate
```
Your terminal prompt should now start with `(venv)`.

### Step 4: Install the Project Dependencies

Now, inside the active virtual environment, install the project in editable mode. This command will read the `setup.py` file and install all necessary dependencies, including `customtkinter`.

```sh
pip install -e .
```

## Running the Application

Once the installation is complete, you can run the GUI with the following command:

```sh
assistant-gui
```

The application window should appear, ready to use.

## GUI Features

- **Tabbed Interface**: Contacts and Notes are neatly separated into their own tabs.
- **Live Search**: The lists automatically filter as you type in the search bars.
- **Interactive Lists**: Click any contact or note to see its full details. The selected item is highlighted.
- **Full CRUD Operations**:
  - **Add**: Click "Add" to open a pop-up window with fields for new data.
  - **Edit**: Select an item and click "Edit" to open a pre-filled pop-up to modify it.
  - **Delete**: Select an item and click "Delete" to remove it (a confirmation dialog will appear to prevent accidents).
- **Safe Error Handling**: If you enter invalid data (e.g., a bad phone number or tag), an error message will appear without closing the window, allowing you to correct the mistake.
- **Data Persistence**: All changes are automatically saved to `assistant_data.pkl` when you close the application.
