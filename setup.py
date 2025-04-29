from setuptools import setup, Extension, find_packages
import numpy
import sys
import pybind11
from pathlib import Path

numpy_inc = numpy.get_include()
pybind11_inc = pybind11.get_include()

pybind11_extensions = [
    Extension("swatuq.utility", [str(Path("swatuq/swat_utility.cpp"))], extra_compile_args=['-std=c++17'] if sys.platform != 'win32' else ['/std:c++20'], include_dirs=[numpy_inc, pybind11_inc]),
]

setup(
    name="swatuq",
    version="1.0.6",
    author="wmtSky",
    author_email="wmtsmasky@gmail.com",
    description="A extend project of UQPyL, which provides develop and GUI versions.",
    ext_modules=pybind11_extensions,
    packages=find_packages(),
    package_data={
        'swatuq': ['swat_parameters.json'],
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)