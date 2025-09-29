from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="sycobench",
    version="0.1.0",
    author="SycoBench Team",
    description="AI Safety Benchmarking Tool for Testing Sycophantic Behavior",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sycobench",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "anthropic>=0.31.0",
        "openai>=1.42.0",
        # "google-generativeai>=0.7.0",  # Not available yet
        # "google-cloud-aiplatform>=1.60.0",  # Optional
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "tenacity>=8.2.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "loguru>=0.7.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "typer>=0.12.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-mock>=3.12.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sycobench=src.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)