from subprocess import Popen, PIPE
from django.conf import settings
import os

def getVersion():
    """Try to get a version string from git, otherwise use a default"""
    command = ("git", "describe", "--tags")
    try:
        cwd = os.getcwd()
        os.chdir(settings.PROJECT_DIR)
        result = Popen(command, stdout=PIPE).communicate()[0]
        os.chdir(cwd)
    except OSError:
        result = settings.PACKAGE_VERSION
    return result.strip()
