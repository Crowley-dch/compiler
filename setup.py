from setuptools import setup, find_packages

setup(
    name="minicompiler",
    version="0.2.0",
    packages=find_packages(),
    package_dir={"": "."},
    entry_points={
        "console_scripts": [
            "compiler = src.main:main",
        ],
    },
    install_requires=[
    ],
    python_requires=">=3.8",
    description="MiniCompiler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)