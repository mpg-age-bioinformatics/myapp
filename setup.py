from setuptools import find_packages, setup

setup(
    name='cycshare',
    version='2.0.1',
    packages=["cycshare"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)