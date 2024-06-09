from setuptools import setup, find_packages

setup(
    name="AI_database_enrichment",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],  # Añade aquí tus dependencias
    author="Enric Chust Gimeno",
    description="",
)
