#!.env/bin/python

from setuptools import setup, find_packages

desc = ''
with open('README.md') as f1:
    desc = f1.read()

setup(
    name='falcon-prospector',
    version='0.0.1',
    description='Leads by IP Address',
    url='https://github.com/craigderington/falcon-prospector.git',
    author='Craig Derington',
    author_email='craig@craigderington.me',
    license='GNUv3',
    classifiers=[
        'Development Status :: 0.1 Alpha',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='falcon api celery',
    packages=find_packages(exclude=['contrib', 'docs', 'test']),
    install_requires=[
        'falcon>=1.4.1',
        'gunicorn>=19.9.0',
        'celery>=4.2.1',
        'redis>=3.0.1'
        'docopt>=0.6.2',
        'jsonschema>=2.5.1',
        'mysql-connector>=2.1.6',
        'sqlalchemy>=1.2.16',
        'aumbry[yaml]>=0.7.0',
        'reverse_geocoder>=1.5.1'
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [
            'falcon-run = prospector.__main__:main'
            'celery-worker = celery -A tasks worker -E --loglevel=INFO -c 10'
        ],
    },
)
