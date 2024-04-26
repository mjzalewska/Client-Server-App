import json
import socket

"""
Serwer ma obsługiwać następujące polecenia (i zwracać odpowiedź w JSONie).
""uptime"" - zwraca czas życia serwera
""info"" - zwraca numer wersji serwera, datę jego utworzenia
""help"" - zwraca listę dostępnych komend z krótkim opisem (tych komend, z tej listy, którą właśnie czytasz, czyli inaczej, komend realizowanych przez serwer)
""stop"" - zatrzymuje jednocześnie serwer i klienta
"""

class Server:
    def __init__(self, port, version):
        self.host = "127.0.0.1"
        self.port = port
        self.version = version
        self.uptime = 0

    def initialize(self):
        pass

    def show_help(self):
        pass

    def show_uptime(self):
        pass

    def show_info(self):
        pass



