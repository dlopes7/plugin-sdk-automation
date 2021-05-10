import os

from setuptools import setup, find_packages


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


long_description = read("README.md")

setup(
    name="plugin-sdk-automation",
    version=get_version("plugin_sdk_automation/__init__.py"),
    description="Tools to automate extensions building and publishing",
    long_description=long_description,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    url="https://github.com/dlopes7/plugin-sdk-automation",
    keywords="dynatrace extension plugin",
    project_urls={
        "Documentation": "https://github.com/dlopes7/plugin-sdk-automation",
        "Source": "https://github.com/dlopes7/plugin-sdk-automationp",
        "Changelog": "https://github.com/dlopes7/plugin-sdk-automation",
    },
    author="David Lopes",
    author_email="david.lopes@dynatrace.com",
    packages=find_packages(),
    install_requires=["docker==4.4.4", "rich==10.1.0", "click==7.1.2"],
    entry_points={
        "console_scripts": ["plugin_sdk_automation=plugin_sdk_automation.main:main", "psa=plugin_sdk_automation.main:main"],
    },
    python_requires=">=3.6",
)
