from setuptools import setup

setup(
    # Application name:
    name="pysmugmugsync",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="Andy Hawkins",
    author_email="andy@gently.org.uk",

    # Packages
    packages=["pysmugmugsync"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/adhawkins/pysmugmugsync",

    #
    license="LICENSE.txt",
    description="A Python based synchronisation client for SmugMug.",

    long_description=open("README.md").read(),

    # Dependent packages (distributions)
    install_requires=[
    ],

    entry_points = {
        "console_scripts": ['pysmugmugsync = pysmugmugsync.Main:main']
    },
)
