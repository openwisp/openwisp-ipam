import os

from openwisp_ipam import get_version
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []
    for line in open('requirements.txt').readlines():
        if line.startswith('#') or line == '' or line.startswith('git'):
            continue
        requirements.append(line)
    return requirements


setup(
    name='openwisp-ipam',
    version=get_version(),
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    license='BSD-3-Clause',
    description='A django IP address management app.',
    long_description=README,
    url='',
    author='Anurag Sharma',
    author_email='anssharma61@gmail.com',
    install_requires=get_install_requires(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
