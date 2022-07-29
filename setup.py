import setuptools

setuptools.setup(
    name="peaqevcore",
    version="4.0.1",
    author="Magnus Eldén",
    description="Core types for peaqev car charging",
    url="https://github.com/elden1337/peaqev-core",
    license="MIT",
    packages=[
        "peaqevcore", 
        "peaqevcore.services.hourselection",
        "peaqevcore.models.hourselection", 
        "peaqevcore.services.chargecontroller", 
        "peaqevcore.services.chargertype",
        "peaqevcore.models.chargertype",
        "peaqevcore.models", 
        "peaqevcore.services.prediction", 
        "peaqevcore.services.session",
        "peaqevcore.services.threshold", 
        "peaqevcore.services.locale", 
        "peaqevcore.services.locale.countries", 
        "peaqevcore.services.locale.querytypes", 
        "peaqevcore.models.locale",
        "peaqevcore.services.scheduler"
        ],
    test_requires=['pytest']
)   
