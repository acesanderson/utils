from setuptools import setup, find_packages

setup(
    name="aces_utils",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "json_schema=json_schema:main",
        ],
    },
)


setup(
    name="Leviathan",
    version="2.0",
    packages=find_packages(),
)
