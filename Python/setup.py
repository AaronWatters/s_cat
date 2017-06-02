import os
import sys
from setuptools import setup

tests_require = ["coverage", "nose"]

base_dir = os.path.dirname(os.path.abspath(__file__))

version = "0.1"

setup(
    name = "s_cat",
    version = version,
    description = "Simple and general write once indexed file format.",
    long_description="\n\n".join([
        open(os.path.join(base_dir, "../README.md"), "r").read(),
        #open(os.path.join(base_dir, "CHANGELOG.rst"), "r").read()
    ]),
    url = "https://github.com/AaronWatters/s_cat",
    author = "Aaron Watters",
    author_email = "awatters@simonsfoundation.org",
    maintainer = "Aaron Watters",
    maintainer_email = "awatters@simonsfoundation.org",
    packages = ["s_cat"],
    zip_safe = False,
    #install_requires = install_requires,
    tests_require = tests_require,
    test_suite = "nose.collector",
)
