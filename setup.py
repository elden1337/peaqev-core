import setuptools

setuptools.setup(
    name="peaqevcore",
    version="5.10.3",
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
        "peaqevcore.models.hub", 
        "peaqevcore.hub", 
        "peaqevcore.services.prediction", 
        "peaqevcore.services.production", 
        "peaqevcore.services.session",
        "peaqevcore.services.threshold", 
        "peaqevcore.services.locale", 
        "peaqevcore.services.locale.countries", 
        "peaqevcore.services.locale.querytypes", 
        "peaqevcore.models.locale",
        "peaqevcore.services.scheduler",
        "peaqevcore.services.timer"
        ],
    test_requires=['pytest']
)   
