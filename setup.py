import setuptools

setuptools.setup(
    name="peaqevcore",
    version="19.7.15",
    author="Magnus Eldén",
    description="Core types for peaqev car charging",
    url="https://github.com/elden1337/peaqev-core",
    license="CC-NC-ND",
    packages=[
        "peaqevcore",
        "peaqevcore.common",
        "peaqevcore.common.enums",
        "peaqevcore.common.models",
        "peaqevcore.common.spotprice",
        "peaqevcore.common.spotprice.models",
        "peaqevcore.services.hourselection",
        "peaqevcore.services.hourselection.hourselectionservice",
        "peaqevcore.services.hourselection.initializers",
        "peaqevcore.models.hourselection",
        "peaqevcore.models.hourselection.hourobjects",
        "peaqevcore.services.hoursselection_service_new",
        "peaqevcore.services.hoursselection_service_new.models",
        "peaqevcore.services.chargertype",
        "peaqevcore.models.chargertype",
        "peaqevcore.models",
        "peaqevcore.models.hub",
        "peaqevcore.hub",
        "peaqevcore.services.prediction",
        "peaqevcore.services.savings",
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
        "peaqevcore.services.timer",
    ],
    extras_require={"tests": ["pytest>3.6.4", "pytest-cov<2.6", "pytest-asyncio"]},
)
