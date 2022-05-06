from setuptools import find_packages
from setuptools import setup


version = "2.0.0a2"

setup(
    name="collective.multisearch",
    version=version,
    description="Portlet based display for the Plone search page",
    long_description=(open("README.txt").read() + "\n\n" + open("CHANGES.rst").read()),
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="multisearch portlet remote",
    author="Zest Software",
    author_email="info@zestsoftware.nl",
    url="https://github.com/zestsoftware/collective.multisearch",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "feedparser",
        "plone.api",
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
