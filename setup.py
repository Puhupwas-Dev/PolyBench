"""
PolyBench-Evaluation packaging setup.
"""
# Docstring describing the purpose of this setup script

import os
# Import the operating system module for filesystem path operations

from setuptools import setup
# Import the setup function from setuptools for building and installing the package

# Declare your non-python data files:
# Files underneath configuration/ will be copied into the build preserving the
# subdirectory structure if they exist.
data_files = []
# Initialize an empty list to hold data file specifications

for root, dirs, files in os.walk("configuration"):
    # Iterate through every directory and file under the "configuration" folder
    data_files.append(
        # Append a tuple (install_path, list_of_files) to data_files
        (os.path.relpath(root, "configuration"), 
         # The relative path from "configuration" becomes the install directory
         [os.path.join(root, f) for f in files])
         # List of full file paths for each file in the current directory
    )

setup(
    # Call the setuptools.setup() function to configure the package
    # include data files
    data_files=data_files,
    # Pass the collected data_files to setup() so they get installed alongside the package
)
