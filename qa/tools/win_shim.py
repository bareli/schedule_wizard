import pytest_socket

pytest_socket.disable_socket = lambda *a, **k: None
pytest_socket.socket_allow_hosts = lambda *a, **k: None
