import os
import re
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('files', [
    '/etc/hostname',
    '/etc/default/locale',
    '/etc/systemd/journald.conf',
    '/etc/systemd/system.conf',
    '/etc/systemd/user.conf',
    '/etc/logrotate.conf',
    '/var/log/commands.log',
    '/etc/rsyslog.d/30-bash.conf',
    '/etc/chrony/chrony.conf'
])
def test_config_files_exist(host, files):
    """
    Test config files is exist
    """
    _f_configs = host.file(files)

    assert _f_configs.is_file
    assert _f_configs.exists


def test_journald(host):
    """
    Check update journald config
    """
    _f_journald_ctn = host.file('/etc/systemd/journald.conf').content_string
    _regex = re.compile('ForwardToSyslog=yes')

    assert re.findall(_regex, _f_journald_ctn)


def test_systemd_system(host):
    """
    Check update systemd system config
    """
    _f_sytemd_system_ctn = host.file('/etc/systemd/system.conf').content_string
    _regex = re.compile('DefaultLimitNOFILE=65535')

    assert re.findall(_regex, _f_sytemd_system_ctn)


def test_systemd_user(host):
    """
    Check update systemd user config
    """
    _f_sytemd_user_ctn = host.file('/etc/systemd/user.conf').content_string
    _regex = re.compile('DefaultLimitNPROC=65535')

    assert re.findall(_regex, _f_sytemd_user_ctn)


def test_timezone(host):
    """
    Check timezone PST is set on server
    """
    _c_tz = host.check_output('date +%Z')

    assert _c_tz == 'PST'


def test_kernel_parameter(host):
    """
    Check set kernel parameter
    """
    _ipv4_forward = host.sysctl('net.ipv4.ip_forward')
    _so_max_conn = host.sysctl('net.core.somaxconn')
    _vm_min_free_kb = host.sysctl('vm.min_free_kbytes')
    _kernel_pid_max = host.sysctl('kernel.pid_max')

    assert _ipv4_forward == 0
    assert _so_max_conn == 32768
    assert _vm_min_free_kb == 131072
    assert _kernel_pid_max == 65535


def test_hugepage(host):
    """
    Check disable hugepage on redis/mongodb
    """
    _hostname = os.uname()[1]

    if 'redis' in _hostname or 'mongodb' in _hostname:
        _f_rc_local = host.file('/etc/rc.local')
        _s_rc_local = host.service('rc.local')

        assert _f_rc_local.exists
        assert _f_rc_local.is_file
        assert _s_rc_local.is_running
        assert _s_rc_local.is_enabled


def test_logrotate(host):
    """
    Check to update logrotate config (enable compress with xz)
    """
    _f_logrotate_cnt = host.file('/etc/logrotate.conf').content_string
    _regex = re.compile('compresscmd /usr/bin/xz')

    assert re.findall(_regex, _f_logrotate_cnt)


@pytest.mark.parametrize('services', [
    'sshd',
    'rsyslog',
    'chrony',
    'node_exporter'
])
def test_services_running(host, services):
    """
    Test services are running + enabled
    """

    _s_services = host.service(services)
    assert _s_services.is_running
    assert _s_services.is_enabled


def test_users(host):
    """
    Test create user/group
    """
    _hostname = os.uname()[1]

    if 'app' in _hostname:
        _g_deploy = host.group('deploy')
        _u_deploy = host.user('deploy')

        assert _g_deploy.exists
        assert _u_deploy.exists
        assert _u_deploy.shell == '/bin/bash'

    _g_gh_system = host.group('gh-system')
    _u_quang = host.user('quang')

    assert _g_gh_system.exists
    assert _u_quang.exists


def test_deploy_key(host):
    """
    Test ssh key is exist
    """
    with host.sudo('deploy'):
        _f_id_rsa_priv = host.file('/home/deploy/.ssh/id_rsa')

        assert _f_id_rsa_priv.exists
        assert _f_id_rsa_priv.is_file


def test_sudo(host):
    """
    Test sudo for ops user
    """
    with host.sudo('quang'):
        _w_quang = host.check_output('whoami')
        assert _w_quang == 'quang'


def test_build_dir(host):
    """
    Test create directory for compiling package
    """
    _hostname = os.uname()[1]

    if 'app' in _hostname:
        _d_build = host.file('/usr/src/build/modules')
        assert _d_build.is_directory

    _d_build = host.file('/usr/src/build')
    assert _d_build.is_directory


@pytest.mark.parametrize('pkgs', [
    'gcc',
    'chrony'
])
def test_pkgs_installed(host, pkgs):
    """
    Test package installed
    """
    _p_pkgs = host.package(pkgs)

    assert _p_pkgs.is_installed


def test_chrony(host):
    """
    Test chrony service
    """
    _c_chrony = host.file('/etc/chrony/chrony.conf')

    assert _c_chrony.contains('server 169.254.169.123 prefer iburst')


@pytest.mark.parametrize('bpkgs', [
    '/usr/local/bin/ps_mem',
    '/usr/local/bin/node_exporter'
])
def test_binary_packages(host, bpkgs):
    """
    Test binary packages
    """
    _p_binary_pkgs = host.file(bpkgs)

    assert _p_binary_pkgs.exists
    assert _p_binary_pkgs.is_file

    assert oct(_p_binary_pkgs.mode) == '0o755'
