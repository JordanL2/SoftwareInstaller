import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="softwareinstaller",
    version="1.2.1",
    author="Jordan Leppert",
    author_email="jordanleppert@gmail.com",
    description="A tool to search, install and update software from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JordanL2/SoftwareInstaller",
    packages=setuptools.find_packages() + setuptools.find_namespace_packages(include=['softwareinstaller.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: LGPL-2.1 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {'console_scripts': ['si = softwareinstaller.cli:main',], },
)
