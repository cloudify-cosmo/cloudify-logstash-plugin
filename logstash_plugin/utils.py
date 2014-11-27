import requests
import tarfile
import subprocess
import os
import platform

from cloudify import ctx
from cloudify import exceptions


def get_distro():
    ctx.logger.debug('identifying distribution...')
    distro = platform.dist()[0]
    ctx.logger.debug('distro identified: {0}'.format(distro))


def get_package_type_for_distro(distro=get_distro()):
    ctx.logger.debug('identifying package type for distro')
    if distro.lower() in ('ubuntu', 'debian'):
        return 'deb'
    elif distro.lower() in ('centos', 'redhat', 'fedora'):
        return 'rpm'
    else:
        return None


def install_package(path, distro=get_distro()):
    """installs an rpm/deb package

    Distribution identification will happen automatically.
    If the distribution is not supported, or the package
    extension does not fit the identified distribution,
    an exception will be raised.
    """
    ctx.logger.debug('attemping to install {0}'.format(path))
    ext = os.path.splitext(path)
    ctx.logger.debug('package extention is: {0}'.format(ext))
    package_type = get_package_type_for_distro(distro)
    # check which package type we're expecting
    if not package_type:
        raise exceptions.NonRecoverableError(
            'unsupported distribution: {0}'.format(distro))
    if not ext == package_type:
        raise exceptions.NonRecoverableError(
            'package type for distro {0} cannot be of type {1}'.format(
                distro, ext))
    elif ext == 'deb':
        return sudo('dpkg -i {0}'.format(path))
    elif ext == 'rpm':
        return sudo('rpm -ivh {0}'.format(path))


def check_resource_available(resource):
    ctx.logger.debug('verifying that {0} is available'.format(resource))
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


def run(cmd):
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


def verify_is_executable(execute):
    ctx.logger.debug('verifying that {0} is executable.'.format(execute))
    if os.system('{0}'.format(execute)):
        raise exceptions.NonRecoverableError('{0} is not executable'.format(
            execute))


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
