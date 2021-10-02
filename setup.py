from setuptools import find_packages, setup

setup(
    name='myapp',
    version='0.0.1',
    packages=["myapp"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)