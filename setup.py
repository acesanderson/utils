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
