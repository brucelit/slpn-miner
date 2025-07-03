from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slpn_miner",
    version="0.1.0",
    author="Tian Li",
    author_email="t.li@bpm.rwth-aachen.de",
    description="Mine optimal SLPNs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brucelit/slpn-miner",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        "pm4py~=2.7.11",
        "pandas~=2.2.2",
        "lxml~=5.2.1",
        "scipy~=1.13.1",
        "sympy~=1.12",
        "numba~=0.61.2",
    ],
    extras_require={"dev": []},
    entry_points={'console_scripts': []},
)