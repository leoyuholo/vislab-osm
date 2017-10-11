from setuptools import setup, find_packages

setup(
    name='vue-open-stree-map',
    description='Vue Open Street Map',
    author='Leo Yu Ho, Lo',
    author_email='leoyuholo@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'Flask-PyMongo'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
