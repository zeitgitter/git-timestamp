#!/usr/bin/python3
import setuptools
import re

def extract_version(filename):
    with open(filename, 'r') as fh:
        for line in fh:
            match = re.match('''VERSION\s*=\s*["']([-_.0-9a-z]+)(\+?)["']''', line)
            if match:
                if match[2] == '':
                    return match[1]
                else:
                    return match[1] + '.post7'
    exit("Cannot extract version number from %s" % filename)


with open('../README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-timestamp",
    version=extract_version('igitt_client/timestamp.py'),
    author="Marcel Waldvogel",
    author_email="marcel.waldvogel@uni-konstanz.de",
    description="Timestamping client for igitt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/igitt/igitt",
    license='AGPLv3',
    packages=setuptools.find_packages(),
    install_requires=['pygit2', 'python-gnupg', 'requests'],
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'git-timestamp=igitt_client.timestamp:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
