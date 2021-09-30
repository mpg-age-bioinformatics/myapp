from setuptools import find_packages, setup

setup(
    name='flaskapp',
    version='0.0.1',
    packages=["flaskapp"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)