"""
Setup script for the Floop AI workflow tool.
"""

from setuptools import setup, find_packages

setup(
    name="floop",
    version="0.1.0",
    description="Floop - AI Workflow tool that orchestrates interactions between multiple AI models",
    author="Floop Team",
    author_email="example@example.com",
    packages=find_packages(),
    py_modules=["floop"],
    install_requires=[
        "openai",
        "anthropic",
        "python-dotenv",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "floop=floop:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
) 