import os

from setuptools import find_packages, setup

from openwisp_ipam import get_version

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
    license='BSD-3-Clause',
    author='OpenWISP',
    author_email='support@openwisp.io',
    description='IP address space administration module of OpenWISP.',
    long_description=README,
    url='https://github.com/openwisp/openwisp-ipam',
    download_url='https://github.com/openwisp/openwisp-ipam/releases',
    platforms=['Platform Independent'],
    keywords=['django', 'freeradius', 'networking', 'openwisp'],
    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=get_install_requires(),
    classifiers=[
        'Development Status :: 5 - Production/Stable ',
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
