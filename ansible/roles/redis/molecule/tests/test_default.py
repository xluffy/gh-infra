import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_redis_service_is_running(host):
    """
    Test redis service is running and enabled
    """
    _s_redis = host.service('redis-6371')

    assert _s_redis.is_running
    assert _s_redis.is_enabled


def test_random_redis_server_config(host):
    """
    Test redis server config
    """
    _c_redis = host.file('/etc/redis/6371.conf')

    assert _c_redis.contains('maxclients')


def test_redis_binary_file_exist(host):
    """
    Check redis binary file was exists
    """
    _f_locale = host.file('/usr/local/bin/redis-server')

    assert _f_locale.exists
    assert _f_locale.is_file


def test_kernel_parameter(host):
    """
    Check set kernel parameter
    """
    _vm_overcommit_memory = host.sysctl('vm.overcommit_memory')
    assert _vm_overcommit_memory == 1


def test_disable_thp(host):
    """
    Test disabled THP
    """

    _f_thp_defrag = host.file('/sys/kernel/mm/transparent_hugepage/defrag')
    assert _f_thp_defrag.exists
    assert _f_thp_defrag.contains('[never]')

    _f_thp_enabled = host.file('/sys/kernel/mm/transparent_hugepage/enabled')
    assert _f_thp_enabled.exists
    assert _f_thp_enabled.contains('[never]')
