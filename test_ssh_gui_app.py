import unittest
from unittest.mock import Mock, patch

import ssh_gui_app


class SshGuiAppTests(unittest.TestCase):
    def test_connect_ssh_client_uses_connection_details(self):
        with patch("ssh_gui_app.paramiko.SSHClient") as client_cls:
            client = client_cls.return_value

            result = ssh_gui_app.connect_ssh_client(
                host="example.com",
                port=22,
                username="root",
                password="secret",
            )

            self.assertIs(result, client)
            client.connect.assert_called_once_with(
                hostname="example.com",
                port=22,
                username="root",
                password="secret",
                timeout=10,
                banner_timeout=20,
            )

    def test_run_shell_command_sends_command_to_channel(self):
        channel = Mock()
        channel.recv_ready.return_value = False

        output = ssh_gui_app.run_shell_command(channel, "cd VisualSSH")

        self.assertEqual(output, "")
        channel.send.assert_called_once_with("cd VisualSSH\n")


if __name__ == "__main__":
    unittest.main()
