"""
Setup script for the AI Workflow MVP package.
"""

from setuptools import setup, find_packages

setup(
    name="ai-workflow-mvp",
    version="0.1.0",
    description="AI Workflow MVP that orchestrates interactions between multiple AI models",
    author="AI Workflow Team",
    author_email="example@example.com",
    packages=find_packages(),
    py_modules=["ai_workflow"],
    install_requires=[
        "openai",
        "anthropic",
        "python-dotenv",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "ai-workflow=ai_workflow:cli",
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