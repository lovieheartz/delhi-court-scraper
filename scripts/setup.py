from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="court-data-fetcher",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A web application for fetching and displaying case information from Delhi High Court",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/court-data-fetcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Legal",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "bandit>=1.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "court-fetcher=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/*"],
    },
)