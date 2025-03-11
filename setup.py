from setuptools import setup, find_packages

setup(
    name="myproject",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-jwt-extended",
        "supabase",
        "joblib",
        "python-dotenv",
    ],
)