import setuptools

setuptools.setup(
    name="peaqevcore",
    version="3.1.6",
    author="Magnus Eldén",
    description="Core types for peaqev car charging",
    url="https://github.com/elden1337/peaqev-core",
    license="MIT",
    packages=[
        "peaqevcore", 
        "peaqevcore.hourselection_service", 
        "peaqevcore.hourselection_service.models", 
        "peaqevcore.chargecontroller_service", 
        "peaqevcore.chargertype_service",
        "peaqevcore.chargertype_service.models",
        "peaqevcore.models", 
        "peaqevcore.prediction_service", 
        "peaqevcore.session_service",
        "peaqevcore.threshold_service", 
        "peaqevcore.locale_service", 
        "peaqevcore.locale_service.countries", 
        "peaqevcore.locale_service.querytypes", 
        "peaqevcore.locale_service.querytypes.models",
        "peaqevcore.scheduler_service"
        ],
    test_requires=['pytest']
)   
