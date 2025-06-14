#!/usr/bin/env python3
"""Setup script for SheetsBot package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="sheetsbot",
    version="1.0.0",
    author="SheetsBot Team",
    author_email="support@sheetsbot.com",
    description="Google Sheets automation tool with file monitoring and Slack integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boadamm/demoproject",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "pre-commit>=3.0.0",
        ],
        "gui": [
            "PySide6>=6.5.0",
            "qt-material>=2.14",
        ],
    },
    entry_points={
        "console_scripts": [
            "sheetsbot=cli:main",
            "sheetsbot-cli=cli:main",
        ],
        "gui_scripts": [
            "sheetsbot-gui=app.gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["gui/*.ui", "gui/assets/*"],
        "config": ["*.toml"],
        "docs": ["*.md"],
    },
    data_files=[
        ("share/applications", ["SheetsBot.desktop"]),
        ("share/doc/sheetsbot", ["README.md", "INSTALLATION.md", "API_SETUP_GUIDE.md"]),
    ],
    zip_safe=False,
    keywords="sheets automation google excel csv monitoring slack",
    project_urls={
        "Bug Reports": "https://github.com/boadamm/demoproject/issues",
        "Source": "https://github.com/boadamm/demoproject",
        "Documentation": "https://github.com/boadamm/demoproject/blob/main/README.md",
    },
)
