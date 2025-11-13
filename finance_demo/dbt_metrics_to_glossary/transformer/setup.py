"""
Setup file for dbt Metrics to Glossary Terms Transformer

Install with:
    pip install -e .
"""

from setuptools import setup

setup(
    name="dbt-metrics-to-glossary-transformer",
    version="0.1.7",
    description="DataHub transformer to convert dbt metrics to glossary terms",
    packages=["transformer"],
    package_dir={"transformer": "."},
    py_modules=["transformer.dbt_metrics_to_glossary_transformer"],
    install_requires=[
        "acryl-datahub",
    ],
    python_requires=">=3.8",
)

