#from setuptools import setup, find_packages

#setup(
#    name='utils',
#    version='1.0.1',
#    packages=find_packages(),
#    description='A utility package for MSP2 extraction',
#    author='Rweyemamu Barongo',
#    author_email='ribarongo@bot.go.tz rbarongo@gmail.com',
#)
import tomllib  # Use 'import toml' or 'import tomli as tomllib' if on Python < 3.11
from setuptools import setup, find_packages
from pathlib import Path

# Load pyproject.toml
path_to_toml = Path(__file__).parent / "pyproject.toml"
with open(path_to_toml, "rb") as f:
    pyproject_data = tomllib.load(f)

# Extract data from the [project] section
project_meta = pyproject_data.get("project", {})

setup(
    name=project_meta.get("name", "utils"),  # Defaults to 'utils' if name not found
    version=project_meta.get("version", "1.0.1"),
    packages=find_packages(),
    description='A utility package for MSP2 extraction',
    author='Rweyemamu Barongo',
    author_email='ribarongo@bot.go.tz rbarongo@gmail.com',
)




