# VisualSSH

A simple and clean graphical SSH client built with Python and Tkinter.

## Features
- Connect to remote SSH servers from a GUI window
- Enter host, port, username, password, and command
- Run commands and view the output directly in the app
- Lightweight and easy to use

## Files
- `ssh_gui_app.py` — the GUI application
- `test_ssh_gui_app.py` — basic verification test for the SSH logic

## Requirements
Install the SSH dependency:

```bash
pip install paramiko
```

## Run the app
```bash
python ssh_gui_app.py
```

## Notes
This app uses password-based SSH authentication and is intended as a simple desktop client for basic remote command execution.
