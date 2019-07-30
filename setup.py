import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="awsaccountmgr",
    version="0.0.1",
    author="Mathijs Mortimer",
    author_email="thiezn@gmail.com",
    description="A command line tool for managing AWS accounts including AWS Deployment Framework support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiezn/awsaccountmgr/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/awsaccountmgr'],
)