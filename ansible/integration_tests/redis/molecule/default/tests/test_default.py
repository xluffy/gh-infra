import os
import re
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize("sockets", [
    "tcp://0.0.0.0:22",
    "tcp://0.0.0.0:6371",
    "tcp://0.0.0.0:9100"
])
def test_socket_is_listening(host, sockets):
    """
    Test socket is listening
    """
    _sk_service = host.socket(sockets)

    assert _sk_service.is_listening
