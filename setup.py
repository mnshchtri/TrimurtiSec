from setuptools import setup, find_packages
from trimurti import VERSION

setup(
    name="trimurti",
    version=VERSION,
    description="Advanced Penetration Testing Framework",
    author="n30x",
    author_email="terrortheweb@gmail.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "markdown>=3.3.0",
        "requests>=2.26.0",
        "scapy>=2.4.5",
        "python-nmap>=0.7.1",
        "paramiko>=2.8.1",
        "colorama>=0.4.4",
        "rich>=10.12.0",
    ],
    entry_points={
        'console_scripts': [
            'trimurti=trimurti.cli:cli',
        ],
    },
    python_requires=">=3.9",
) 