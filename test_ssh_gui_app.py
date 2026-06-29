import unittest
from unittest.mock import patch

import ssh_gui_app


class SshGuiAppTests(unittest.TestCase):
    def test_run_ssh_command_uses_connection_details(self):
        with patch("ssh_gui_app.paramiko.SSHClient") as client_cls:
            client = client_cls.return_value
            client.exec_command.return_value = (None, "hello\n", "")

            output = ssh_gui_app.run_ssh_command(
                host="example.com",
                port=22,
                username="root",
                password="secret",
                command="uname -a",
            )

            self.assertEqual(output, "hello\n")
            client.connect.assert_called_once_with(
                hostname="example.com",
                port=22,
                username="root",
                password="secret",
                timeout=10,
                banner_timeout=20,
            )
            client.exec_command.assert_called_once_with("uname -a")


if __name__ == "__main__":
    unittest.main()
