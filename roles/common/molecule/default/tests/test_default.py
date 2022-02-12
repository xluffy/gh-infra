import os
import re

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.fixture()
def get_vars(host):
    """
    Get variable
    """
    defaults_files = "dir=defaults/main"
    # defaults_files = "file=defaults/main/main.yml"

    host.ansible("setup")
    ansible_vars = host.ansible("include_vars", defaults_files)["ansible_facts"]

    ansible_vars.update(host.ansible.get_variables())

    return ansible_vars


@pytest.mark.parametrize(
    "files",
    [
        "/etc/hostname",
        "/etc/default/locale",
        "/etc/systemd/journald.conf",
        "/etc/systemd/system.conf",
        "/etc/systemd/user.conf",
        "/etc/logrotate.conf",
        "/var/log/commands.log",
        "/etc/rsyslog.d/30-bash.conf",
        "/etc/chrony/chrony.conf",
    ],
)
def test_config_files_exist(host, files):
    """
    Test config files are exist
    """
    _f_configs = host.file(files)

    assert _f_configs.is_file
    assert _f_configs.exists


def test_systemd_resolved(host):
    """
    Test systemd-resolved for local dns caching
    """

    _f_systemd_resolved = host.file("/etc/systemd/resolved.conf")

    assert _f_systemd_resolved.is_file
    assert _f_systemd_resolved.exists


def test_journald(host):
    """
    Check update journald config
    """
    _f_journald_ctn = host.file("/etc/systemd/journald.conf").content_string
    _regex = re.compile("ForwardToSyslog=yes")

    assert re.findall(_regex, _f_journald_ctn)


def test_systemd_system(host):
    """
    Check update systemd system config
    """
    _f_systemd_system_ctn = host.file("/etc/systemd/system.conf").content_string
    _regex = re.compile("DefaultLimitNOFILE=65535")

    assert re.findall(_regex, _f_systemd_system_ctn)


def test_systemd_user(host):
    """
    Check update systemd user config
    """
    _f_systemd_user_ctn = host.file("/etc/systemd/user.conf").content_string
    _regex = re.compile("DefaultLimitNPROC=65535")

    assert re.findall(_regex, _f_systemd_user_ctn)


def test_timezone(host):
    """
    Check timezone of server
    """
    _c_tz = host.check_output("date +%Z")

    assert _c_tz in ("UTC")


def test_kernel_parameter(host):
    """
    Check set kernel parameter
    """
    _ipv4_forward = host.sysctl("net.ipv4.ip_forward")
    _so_max_conn = host.sysctl("net.core.somaxconn")
    _vm_min_free_kb = host.sysctl("vm.min_free_kbytes")
    _kernel_pid_max = host.sysctl("kernel.pid_max")

    assert _ipv4_forward == 0
    assert _so_max_conn == 32768
    assert _vm_min_free_kb == 131072
    assert _kernel_pid_max == 65535


def test_hugepage(host):
    """
    Check disable hugepage on redis/mongodb
    """
    _hostname = os.uname()[1]

    if "redis" in _hostname or "mongodb" in _hostname:
        _f_rc_local = host.file("/etc/rc.local")
        _s_rc_local = host.service("rc.local")

        assert _f_rc_local.exists
        assert _f_rc_local.is_file
        assert _s_rc_local.is_running
        assert _s_rc_local.is_enabled


def test_logrotate(host):
    """
    Check to update logrotate config (enable compress with xz)
    """
    _f_logrotate_cnt = host.file("/etc/logrotate.conf").content_string
    _regex = re.compile("compresscmd /usr/bin/xz")

    assert re.findall(_regex, _f_logrotate_cnt)


def test_alternatives(host):
    """
    Test alternatives
    """

    _f_vim = host.file("/etc/alternatives/editor")
    _f_vim_linked_to = host.file("/etc/alternatives/editor").linked_to

    assert _f_vim.is_symlink
    assert _f_vim_linked_to == "/usr/bin/vim.basic"


@pytest.mark.parametrize("services", ["sshd", "rsyslog", "chrony", "node_exporter"])
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

    if "app" in _hostname or "api" in _hostname or "web" in _hostname:
        _g_deploy = host.group("deploy")
        _u_deploy = host.user("deploy")

        assert _g_deploy.exists
        assert _u_deploy.exists
        assert _u_deploy.shell == "/bin/bash"


def test_build_dir(host):
    """
    Test create directory for compiling package
    """
    _hostname = os.uname()[1]

    if "app" in _hostname or "api" in _hostname or "web" in _hostname:
        _d_build = host.file("/usr/src/build/modules")
        assert _d_build.is_directory

    _d_build = host.file("/usr/src/build")
    assert _d_build.is_directory


@pytest.mark.parametrize("pkgs", ["gcc", "chrony"])
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
    _c_chrony = host.file("/etc/chrony/chrony.conf")
    _hostname = host.check_output("hostname -s")

    if "local" in _hostname:
        assert _c_chrony.contains("server 0.vn.pool.ntp.org")
    elif "prod" in _hostname or "test" in _hostname or "vg" in _hostname:
        assert _c_chrony.contains("server 169.254.169.123 prefer iburst")
    else:
        assert True


@pytest.mark.parametrize("bpkgs", ["/usr/local/bin/ps_mem"])
def test_binary_packages(host, bpkgs):
    """
    Test binary packages
    """
    _p_binary_pkgs = host.file(bpkgs)

    assert _p_binary_pkgs.exists
    assert _p_binary_pkgs.is_file

    assert oct(_p_binary_pkgs.mode) == "0o755"
