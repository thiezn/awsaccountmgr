import setuptools

with open('README.md', 'r') as f:
    readme = f.read()

with open('HISTORY.md', 'r') as f:
    history = f.read()

setuptools.setup(
    name="awsaccountmgr",
    version="0.0.6",
    author="Mathijs Mortimer",
    keywords="AWS Accounts",
    author_email="mathijs@mortimer.nl",
    description="A command line tool for managing accounts within an AWS organization. Easy to integrate into AWS Deployment Framework",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    url="https://github.com/thiezn/awsaccountmgr/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/awsaccountmgr'],
)