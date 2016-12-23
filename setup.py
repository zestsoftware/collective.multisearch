from setuptools import setup, find_packages

version = '1.2'

setup(
    name='collective.multisearch',
    version=version,
    description="Portlet based display for the Plone search page",
    long_description=(open("README.txt").read() + "\n\n" +
                      open("CHANGES.rst").read()),
    # Get more strings from
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='multisearch portlet remote',
    author='Zest Software',
    author_email='info@zestsoftware.nl',
    url='https://github.com/zestsoftware/collective.multisearch',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'feedparser',
    ],
    extras_require={
        'test': [
            'Products.PloneTestCase',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
