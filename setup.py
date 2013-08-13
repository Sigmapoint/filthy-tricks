import sys
import subprocess

from setuptools import setup

import distutils.core
        
setup(
    name = "filthy-tricks",
    version = "0.1",
    package_dir = {
        '': 'src',
    },
    packages = [
        'filthy',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        'djangorestframework>=2.3.6',
    ],

    author = "Sigmapoint",
    author_email = "karol.majta@sigmapoint.co",
    description = "Some quick and dirty hacks to make your life with" \
                  "django-rest-framework even nicer than it is now.",
    license = "MIT",
    url = "http://sigmapoint.co",
)
