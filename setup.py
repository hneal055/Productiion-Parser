"""
Scene Reader Studio Technologies - AURA Enterprise
Commercial Distribution Setup
"""

from setuptools import setup, find_packages
import json

# Read version info
with open('version.json', 'r') as f:
    version_info = json.load(f)

setup(
    name="scene_reader_aura",
    version=version_info['version'],
    description="AURA Enterprise - AI-Powered Screenplay Intelligence Platform",
    long_description=open('README.md').read(),
    author="Scene Reader Studio Technologies LLC",
    author_email="licensing@scenereadertech.com",
    url="https://www.scenereadertech.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pandas>=1.3.0", 
        "flask>=2.0.0",
        "pymongo>=4.0.0",
        "numpy>=1.21.0",
        "cryptography>=3.4.0",
        "python-dotenv>=0.19.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Entertainment Industry",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'aura-processor=scene_reader_aura.processor:main',
            'aura-dashboard=scene_reader_aura.dashboard:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)