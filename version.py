from subprocess import Popen, PIPE
from django.conf import settings

def getVersion():
    """Try to get a version string from git, otherwise use a default"""
    command = ("git", "describe", "--tags")
    try:
        result = Popen(command, stdout=PIPE).communicate()[0]
    except OSError:
        result = settings.PACKAGE_VERSION
    return result
