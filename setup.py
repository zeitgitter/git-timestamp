#!/usr/bin/python3
import re

import setuptools


def extract_version(filename):
    with open(filename, 'r') as fh:
        for line in fh:
            match = re.match('''VERSION\s*=\s*["']([-_.0-9a-z]+)(\+?)["']''', line)
            if match:
                if match[2] == '':
                    return match[1]
                else:
                    return match[1] + '.post'
    exit("Cannot extract version number from %s" % filename)


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-timestamp",
    version=extract_version('git_timestamp/timestamp.py'),
    author="Marcel Waldvogel",
    author_email="marcel.waldvogel@trifence.ch",
    description="Timestamping client for zeitgitter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/zeitgitter/git-timestamp",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['pygit2', 'python-gnupg', 'requests', 'setuptools'],
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
