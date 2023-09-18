#
# A project file for the httplib2_cache_mongodb python module.
#
import os

from setuptools import find_packages, setup


def read_requirements(name):
    project_root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(project_root, name), "rb") as f:
        # remove whitespace and comments
        g = (line.decode("utf-8").lstrip().split("#", 1)[0].rstrip() for line in f)
        return [line for line in g if line]


VERSION = "0.1.0"
setup(
    name="httplib2_cache_mongodb",
    version=VERSION,
    author="Roberto Polli",
    author_email="robipolli@gmail.com",
    description="A mongodb cache module for httplib2",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ioggstream/httplib2-cache-mongodb",
    include_package_data=True,
    package_data={"": ["LICENSE", "README.md"]},
    packages=find_packages(),
    python_requires=">=3.9",
    # Install requires are flexible, since this
    #  is a library.
    install_requires=[
        "httplib2",
        "pymongo",
    ],
    # Install requires from requirements-dev.txt
    # tests_require=read_requirements("requirements-dev.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
