import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import paramiko


def connect_ssh_client(host, port, username, password):
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
    return client


def start_shell_session(client):
    channel = client.invoke_shell(term="xterm", width=120, height=40)
    channel.settimeout(0.2)
    return channel


def run_shell_command(channel, command):
    channel.send(command + "\n")
    output_parts = []
    deadline = time.time() + 1.5
    while time.time() < deadline:
        if channel.recv_ready():
            data = channel.recv(4096)
            if isinstance(data, bytes):
                data = data.decode("utf-8", errors="replace")
            output_parts.append(data)
            deadline = time.time() + 1.5
        else:
            time.sleep(0.05)
    return "".join(output_parts)


class SshGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VisualSSH")
        self.geometry("900x680")
        self.minsize(820, 600)
        self.configure(bg="#0f172a")
        self.client = None
        self.shell_channel = None
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0f172a")
        style.configure("TLabelframe", background="#0f172a", foreground="#e2e8f0")
        style.configure("TLabelframe.Label", background="#0f172a", foreground="#e2e8f0")
        style.configure("TLabel", background="#0f172a", foreground="#e2e8f0")
        style.configure("TEntry", fieldbackground="#111827", foreground="#f8fafc")
        style.configure("TButton", background="#2563eb", foreground="#ffffff")
        style.map("TButton", background=[("active", "#1d4ed8")])

        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="VisualSSH", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text="A polished GUI for running SSH commands", foreground="#94a3b8").pack(anchor="w")

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
        self.command_entry.bind("<Return>", self.on_enter_pressed)

        button_row = ttk.Frame(main)
        button_row.pack(fill="x", pady=(6, 8))
        ttk.Button(button_row, text="Connect / Run", command=self.run_command).pack(side="left")
        ttk.Button(button_row, text="Disconnect", command=self.disconnect).pack(side="left", padx=(8, 0))
        ttk.Button(button_row, text="Clear Output", command=self.clear_output).pack(side="left", padx=(8, 0))

        output_frame = ttk.LabelFrame(main, text="Output")
        output_frame.pack(fill="both", expand=True)
        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#020617", fg="#f8fafc", insertbackground="#f8fafc")
        self.output.pack(fill="both", expand=True, padx=6, pady=6)

    def clear_output(self):
        self.output.delete("1.0", tk.END)

    def on_enter_pressed(self, event=None):
        self.run_command()

    def disconnect(self):
        if self.shell_channel is not None:
            self.shell_channel.close()
            self.shell_channel = None
        if self.client is not None:
            self.client.close()
            self.client = None
        self.output.insert(tk.END, "Disconnected.\n")

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

        try:
            if self.client is None:
                self.output.delete("1.0", tk.END)
                self.output.insert(tk.END, f"Connecting to {host}:{port}...\n")
                self.update_idletasks()
                self.client = connect_ssh_client(host, port, username, password)
                self.shell_channel = start_shell_session(self.client)
                self.output.insert(tk.END, "Connected.\n")
            elif self.shell_channel is None:
                self.shell_channel = start_shell_session(self.client)

            self.output.insert(tk.END, f"$ {command}\n")
            result = run_shell_command(self.shell_channel, command)
            self.output.insert(tk.END, result)
        except Exception as exc:
            self.output.insert(tk.END, f"ERROR: {exc}\n")
            messagebox.showerror("Connection failed", str(exc))


if __name__ == "__main__":
    app = SshGuiApp()
    app.mainloop()
