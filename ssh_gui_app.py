import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import paramiko


def run_ssh_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        timeout=10,
        banner_timeout=20,
    )
    try:
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read() if hasattr(stdout, "read") else stdout
        error_output = stderr.read() if hasattr(stderr, "read") else stderr
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        if isinstance(error_output, bytes):
            error_output = error_output.decode("utf-8", errors="replace")
        if error_output:
            return output + error_output
        return output
    finally:
        client.close()


class SshGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SSH GUI Client")
        self.geometry("820x620")
        self.minsize(780, 560)

        self.configure(padx=16, pady=16)

        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        form = ttk.LabelFrame(main, text="Connection")
        form.pack(fill="x", padx=4, pady=(0, 10))

        fields = [
            ("Host", "host"),
            ("Port", "port"),
            ("Username", "username"),
            ("Password", "password"),
        ]

        self.entries = {}
        for index, (label_text, key) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=index, column=0, sticky="w", padx=8, pady=6)
            if key == "password":
                entry = ttk.Entry(form, show="*")
            else:
                entry = ttk.Entry(form)
            entry.grid(row=index, column=1, sticky="ew", padx=8, pady=6)
            self.entries[key] = entry

        form.columnconfigure(1, weight=1)

        command_frame = ttk.Frame(main)
        command_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(command_frame, text="Command").pack(anchor="w")
        self.command_entry = ttk.Entry(command_frame)
        self.command_entry.pack(fill="x", pady=(4, 0))
        self.command_entry.insert(0, "uname -a")

        button_row = ttk.Frame(main)
        button_row.pack(fill="x", pady=(6, 8))
        ttk.Button(button_row, text="Connect and Run", command=self.run_command).pack(side="left")
        ttk.Button(button_row, text="Clear Output", command=self.clear_output).pack(side="left", padx=(8, 0))

        output_frame = ttk.LabelFrame(main, text="Output")
        output_frame.pack(fill="both", expand=True)
        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=6, pady=6)

    def clear_output(self):
        self.output.delete("1.0", tk.END)

    def run_command(self):
        host = self.entries["host"].get().strip()
        port_text = self.entries["port"].get().strip()
        username = self.entries["username"].get().strip()
        password = self.entries["password"].get()
        command = self.command_entry.get().strip()

        if not host or not username or not command:
            messagebox.showerror("Missing data", "Host, username, and command are required.")
            return

        try:
            port = int(port_text) if port_text else 22
        except ValueError:
            messagebox.showerror("Invalid port", "Port must be a number.")
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Connecting to {host}:{port}...\n")
        self.update_idletasks()

        try:
            result = run_ssh_command(host, port, username, password, command)
            self.output.insert(tk.END, result)
        except Exception as exc:
            self.output.insert(tk.END, f"ERROR: {exc}\n")
            messagebox.showerror("Connection failed", str(exc))


if __name__ == "__main__":
    app = SshGuiApp()
    app.mainloop()
