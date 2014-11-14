import requests
import tarfile
import subprocess
import os
import platform

from cloudify import ctx
from cloudify import exceptions


def get_distro():
    return platform.dist()[0]


def install_package(path, distro=get_distro()):

    def raise_package_type_error(distro, pkg_type):
        raise exceptions.NonRecoverableError(
            'package type for distro {0} must be of type {1}'.format(
                distro, pkg_type))

    ext = os.path.splitext(path)
    if distro.lower() in ('ubuntu', 'debian'):
        if ext == 'deb':
            return sudo('dpkg -i {0}'.format(path))
        else:
            raise_package_type_error(distro, 'deb')
    elif distro.lower() in ('redhat', 'centos', 'fedora'):
        if ext == 'rpm':
            return sudo('rpm -ivh {0}'.format(path))
        else:
            raise_package_type_error(distro, 'rpm')
    else:
        raise exceptions.NonRecoverableError(
            'unsupported distribution: {0}'.format(distro))


def check_resource_available(resource):
    response = requests.head(resource)
    if response.status_code != requests.codes.ok:
        raise exceptions.NonRecoverableError(
            "resource is not available (at {0})".format(resource))


def untar(source, destination):
    if not tarfile.is_tarfile(source):
        raise exceptions.NonRecoverableError(
            '{0} is not a tar file.'.format(source))
    # with tarfile.open(source, 'r:gz') as tar:
    #     tar.extractall(destination)

    # after this logstash now available at ~/logstash/bin/logstash
    run('tar -xzvf {0} -C {1} --strip-components=1'.format(
        source, destination))


def run(ctx, cmd):
    """executes a command

    :param string cmd: command to execute
    """
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    ctx.logger.debug('stdout: {0}'.format(stdout))
    ctx.logger.debug('stderr: {0}'.format(stderr))
    p.stdout = stdout
    p.strerr = stderr
    return p


def sudo(cmd):
    return run('sudo {0}'.format(cmd))


def mkdir(path):
    if not os.path.isdir(os.path.dirname(path)):
        ctx.logger.debug('creating directory: {0}'.format(path))
        try:
            os.makedirs(os.path.dirname(path))
        except Exception as ex:
            raise exceptions.NonRecoverableError(
                'failed to create directory: {0}. ({1})'.format(
                    path, ex.message))
    else:
        ctx.logger.debug('directory already exists: {0}'.format(path))


def check_java_exists(java_path):
    ctx.logger.debug('checking to see if java is runnable.')
    java_nexists = os.system('{0} -version'.format(java_path))
    if java_nexists:
        raise exceptions.NonRecoverableError('{0} is not executable'.format(
            java_path))


def download_file(url, destination):
    ctx.logger.debug('downloading {0} to {1}...'.format(url, destination))
    r = requests.get(url, stream=True)
    if not r.status_code == 200:
        raise exceptions.NonRecoverableError(
            'failed to download file: {0}'.format(url))
    with open(destination, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
