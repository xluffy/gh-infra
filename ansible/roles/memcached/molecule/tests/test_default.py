import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize("fbins", [
    "/usr/local/bin/memcached",
    "/usr/local/bin/memcache-top",
    "/usr/local/bin/memcached-tool-ng",
    "/usr/local/bin/memcached_exporter"
])
def test_fbins_memcached(host, fbins):
    """
    Test file binary memcached is exist
    """
    _f_bin_memcached = host.file(fbins)

    assert _f_bin_memcached.is_file
    assert _f_bin_memcached.exists
    assert oct(_f_bin_memcached.mode) == "0o755"
    assert _f_bin_memcached.user == "root"
    assert _f_bin_memcached.group == "root"


@pytest.mark.parametrize("fconfs", [
    "/usr/local/bin/memcached",
    "/usr/local/bin/memcache-top",
    "/usr/local/bin/memcached-tool-ng",
    "/etc/memcached/memcached.conf",
    "/etc/default/memcached",
    "/etc/systemd/system/memcached.service",
    "/etc/systemd/system/memcached_exporter.service"
])
def test_fconf_memcached(host, fconfs):
    """
    Test file config memcached is exist
    """
    _f_conf_memcached = host.file(fconfs)

    assert _f_conf_memcached.is_file
    assert _f_conf_memcached.exists


@pytest.mark.parametrize("services", [
    "memcached",
    "memcached_exporter"
])
def test_memcached_service_is_running(host, services):
    """
    Test memcached service is running and enabled
    """
    _s_memcached = host.service(services)

    assert _s_memcached.is_running
    assert _s_memcached.is_enabled


def test_libmemcached_tools_is_installed(host):
    """
    Test libmemcached-tools is installed
    """
    _p_libmemcached_tools = host.package("libmemcached-tools")

    assert _p_libmemcached_tools.is_installed


def test_random_memcached_server_config(host):
    """
    Test memcached server config
    """
    _c_memcached = host.file("/etc/memcached/memcached.conf")

    assert _c_memcached.contains("CACHESIZE")


@pytest.mark.parametrize("users", [
    "memcached",
    "memcached_exporter"
])
def test_users(host, users):
    """
    Test create user/group
    """
    _u_memcached = host.user(users)

    assert _u_memcached.exists
