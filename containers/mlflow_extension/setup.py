from setuptools import setup

setup(
    name="mlflow_extension",
    install_requires=["mlflow"],
    entry_points={
        "mlflow.app": [
            "custom_app=app:app"
        ]
    }
)
