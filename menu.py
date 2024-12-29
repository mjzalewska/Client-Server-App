import logging
from utilities import load_menu_config


class Menu:
    """
    Manages server menus and command execution. Each menu has its own state
    and available commands based on the user's role and login status.
    """

    def __init__(self, server):
        self.server = server
        self.current_commands = {}

        self.logged_out_commands = {
            "log in": self._handle_login,
            "register": self._handle_registration,
            "exit": self._handle_exit
        }

        self.user_commands = {
            "inbox": self._handle_inbox,
            "info": self._handle_user_info,
            "help": self._handle_help,
            "log out": self._handle_logout,
            "exit": self._handle_exit
        }

        self.admin_commands = {
            "inbox": self._handle_inbox,
            "info": self._handle_server_info,
            "uptime": self._handle_uptime_display,
            "users": self._handle_users_management,
            "help": self._handle_help,
            "log out": self._handle_log_out,
            "exit": self._handle_server_shutdown
        }

        self.user_management_commands = {
            "add": self._handle_user_addition,
            "delete": self._handle_user_deletion,
            "user info": self._handle_user_info,
            "user info -a": self._handle_user_info,
            "help": self._handle_help,
            "back": self._handle_return
        }

    def update_menu_state(self):
        """Update menu commands based on current user state (logged in, logged out)"""
        if not self.server.user:
            self._set_logged_out_state()
        elif self.server.user.role == "admin":
            self._set_admin_state()
        else:
            self._set_user_state()

    def _set_logged_out_state(self):
        """Configure menu for logged-out users"""
        self.current_commands = load_menu_config("menu", "logged_out", "user")
        self.server.send("Please log in or register", (self.current_commands, "list"))

    def _set_admin_state(self):
        """Configure menu for admins"""
        self.current_commands = load_menu_config("menu", "logged_in", "admin")
        self.server.send("Administrator Main Menu", (self.current_commands, "list"))

    def _set_user_state(self):
        """Configure menu for regular users"""
        self.current_commands = load_menu_config("menu", "logged_in", "user")
        self.server.send("User Main Menu", (self.current_commands, "list"))

    def _enter_user_management_menu(self):
        """Switch to user management menu state"""
        self.current_commands = load_menu_config( "manage_users_menu","logged_in","admin")
        self.server.send("User management menu", (self.current_commands, "list"))

    def _is_valid_command(self, command):
        if command in self.current_commands:
            return True
        return False

    def _get_command_handler(self, command):
        """Get appropriate handler for current menu state"""
        if not self.server.user:
            return self.logged_out_commands[command]
        elif self.server.user.role == "admin":
            return self.admin_commands[command]
        else:
            return self.user_commands[command]

    def handle_command(self, command):
        """
        Execute command based on the current menu state
        Returns True if command executed successfully, False otherwise
          """
        command = command.casefold()
        if not self._is_valid_command(command):
            logging.error(f"Bad request received from {self.server.address}")
            self.server.send("Unknown request. Choose correct command!", (self.current_commands, "list"), "error")
            return False
        try:
            handler = self._get_command_handler(command)
            handler()
            return True
        except Exception as e:
            logging.error(f"Error executing command '{command}': {e}")
            self.server.send("An error occurred. Please try again.", status="error")


