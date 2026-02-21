from setuptools import find_packages, setup

setup(
    name='mlproject',
    version='0.0.1',
    author='krishan',
    author_email='kk9289@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'scikit-learn', 'flask' 
    ]
)