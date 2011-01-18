from setuptools import setup, find_packages

version = '0.1'

setup(
    name='django-toolbox',
    version=version,
    description="A collection of utilities for django applications.",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    keywords='django',
    author='Baptiste Mispelon',
    author_email='bmispelon@gmail.com',
    url='https://github.com/bmispelon/django-toolbox',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
