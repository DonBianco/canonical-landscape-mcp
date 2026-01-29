from setuptools import setup

setup(
    name="landscape-mcp-server",
    version="0.1.0",
    description="MCP Server for Canonical Landscape API - Desktop/Laptop Management",
    author="Landscape MCP Contributors",
    license="MIT",
    python_requires=">=3.10",
    py_modules=["landscape_mcp"],
    install_requires=[
        "mcp==1.24.0",
        "landscape-api-py3==0.9.0",
        "requests==2.32.5",
    ],
    entry_points={
        "console_scripts": [
            "landscape-mcp=landscape_mcp:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
    ],
)
