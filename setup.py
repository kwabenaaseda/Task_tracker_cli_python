from setuptools import setup, find_packages

setup(
    name='task_tracker',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tracker=src.main:HandleUser',
        ],
    },
    install_requires=[
        'psycopg2-binary',
    ],
)