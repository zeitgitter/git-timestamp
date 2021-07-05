#!/usr/bin/python3
import os
import re
import subprocess

import setuptools


def extract_version(filename):
    with open(filename, 'r') as fh:
        for line in fh:
            match = re.match(
                r'''VERSION\s*=\s*["']([-_.0-9a-z]+)(\+?)["']''', line)
            if match:
                if match[2] == '':
                    return match[1]
                else:
                    return match[1] + '.post'
    exit("Cannot extract version number from %s" % filename)


def describe_or_extract_version(filename):
    if 'FORCE_VERSION' in os.environ:
        return os.environ['FORCE_VERSION']
    ret = subprocess.run(['git', 'describe'], capture_output=True, text=True)
    if ret.returncode != 0:
        return extract_version(filename)
    else:
        match = re.match('^v?([0-9]+.[0-9]+.[0-9]+)(-([0-9]+))?', ret.stdout)
        if match:
            if match[3] is None:
                return match[1]
            else:
                return match[1] + '.post' + match[3]
        else:
            return extract_version(filename)


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-timestamp",
    version=describe_or_extract_version('git_timestamp/timestamp.py'),
    author="Marcel Waldvogel",
    author_email="marcel.waldvogel@trifence.ch",
    description="GIT Timestamping client for Zeitgitter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://zeitgitter.net",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'pygit2', 'python-gnupg', 'requests', 'setuptools', 'configargparse', 'deltat~=1.1'
    ],
    python_requires='>=3.4',
    entry_points={
        'console_scripts': [
            'git-timestamp=git_timestamp.timestamp:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
)
