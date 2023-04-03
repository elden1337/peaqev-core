import setuptools

setuptools.setup(
    name="peaqevcore",
    version="13.4.15",
    author="Magnus Eldén",
    description="Core types for peaqev car charging",
    url="https://github.com/elden1337/peaqev-core",
    license="CC-NC-ND",
    packages=[
        "peaqevcore", 
        "peaqevcore.services.hourselection",
        "peaqevcore.services.hourselection.hourselectionservice",
        "peaqevcore.services.hourselection.initializers",
        "peaqevcore.models.hourselection", 
        "peaqevcore.models.hourselection.hourobjects", 
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
        "peaqevcore.models.locale.enums",
        "peaqevcore.models.locale.price",
        "peaqevcore.models.locale.price.models",
        "peaqevcore.services.scheduler",
        "peaqevcore.services.timer"
        ],
    test_requires=['pytest']
)   