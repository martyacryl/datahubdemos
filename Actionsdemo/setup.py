"""
Setup script for DataHub Actions Demo
"""
from setuptools import setup, find_packages

setup(
    name="datahubdemos",
    version="0.1.0",
    description="Demo DataHub Actions",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "acryl-datahub>=0.8.34",
        "acryl-datahub-actions",
    ],
    package_data={
        "datahubdemos": ["configs/*.yaml"],
    },
    entry_points={
        "datahub.action": [
            "tag_notifier = datahubdemos.actions.tag_notifier:TagNotifierAction",
            "quality_monitor = datahubdemos.actions.quality_monitor:QualityMonitorAction",
        ],
    },
)