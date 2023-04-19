from .countries.default import Default, NoPeak
from .countries.belgium import VregBelgium
from .countries.sweden import (
    SE_Bjerke_Energi,
    SE_FalbygdensEnergi, 
    SE_Gothenburg, 
    SE_Karlstad, 
    SE_Kristinehamn, 
    SE_Linde_Energi, 
    SE_Malarenergi, 
    SE_Malung_Salen, 
    SE_Nacka_normal, 
    SE_NACKA_timediff, 
    SE_Partille, 
    SE_SHE_AB, 
    SE_Skovde, 
    SE_Sollentuna,
    SE_TekniskaVerken_Link,
    SE_Eskilstuna,
    SE_Ellevio,
    SE_JBF
    #SE_Telge_Energi
    )
from .countries.norway import NO_AgderEnergi, NO_Elvia, NO_GlitreEnergi, NO_LNett, NO_Lede, NO_Mellom, NO_Tensio, NO_BKK, NO_AskerNett


"""LOCALETYPES"""
LOCALE_SE_ESKILSTUNA = "Eskilstuna elnät, Sweden"
LOCALE_SE_GOTHENBURG = "Gothenburg, Sweden"
LOCALE_SE_KARLSTAD = "Karlstad, Sweden"
LOCALE_SE_KRISTINEHAMN = "Kristinehamn, Sweden"
LOCALE_SE_NACKA_NORMAL = "Nacka, Sweden (Normal tariffe)"
#LOCALE_SE_NACKA_TIMEDIFF = "Nacka, Sweden (Time differentiated tariffe)"
LOCALE_SE_PARTILLE = "Partille, Sweden"
LOCALE_DEFAULT = "Other, just want to test"
LOCALE_NO_PEAK = "No peak shaving needed"
LOCALE_SE_SALA = "Sala-Heby Energi AB, Sweden"
LOCALE_SE_MALUNG_SALEN = "Malung-Sälen, Sweden (Malungs elverk)"
LOCALE_SE_TEKNISKA_LINK = "Tekniska verken Linköping, Sweden"
LOCALE_SE_SKOVDE = "Skövde, Sweden"
LOCALE_SE_SOLLENTUNA = "Sollentuna Energi, Sweden"
LOCALE_BE_VREG = "Belgium (VREG)"
LOCALE_SE_BJERKE_ENERGI = "Bjärke Energi, Sweden"
LOCALE_NO_GLITRE_ENERGI = "Glitre Energi, Norway"
LOCALE_NO_AGDER_ENERGI = "Agder Energi, Norway"
LOCALE_NO_LNETT = "LNett, Norway"
LOCALE_NO_TENSIO = "Tensio, Norway"
LOCALE_SE_LINDE_ENERGI = "Linde Energi, Sweden"
LOCALE_SE_FALBYDGENS_ENERGI = "Falbygdens Energi, Sweden"
LOCALE_NO_ELVIA = "Elvia, Norway"
LOCALE_NO_LEDE = "Lede, Norway"
LOCALE_NO_BKK = "BKK, Norway"
LOCALE_SE_MALARENERGI = "Mälarenergi, Sweden"
LOCALE_NO_MELLOM = "Mellom, Norway"
LOCALE_NO_ASKER = "Asker Nett, Norway"
LOCALE_SE_ELLEVIO = "Ellevio, Sweden"
LOCALE_SE_JBF = "Jukkasjärvi (JBF), Sweden"

LOCALETYPEDICT = {
    LOCALE_DEFAULT: Default,
    LOCALE_NO_PEAK: NoPeak,
    LOCALE_SE_ESKILSTUNA: SE_Eskilstuna,
    LOCALE_SE_GOTHENBURG: SE_Gothenburg,
    LOCALE_SE_PARTILLE: SE_Partille,
    LOCALE_SE_KARLSTAD: SE_Karlstad,
    LOCALE_SE_KRISTINEHAMN: SE_Kristinehamn,
    LOCALE_SE_NACKA_NORMAL: SE_Nacka_normal,
    LOCALE_SE_MALUNG_SALEN: SE_Malung_Salen,
    LOCALE_SE_SALA: SE_SHE_AB,
    LOCALE_SE_SKOVDE: SE_Skovde,
    LOCALE_SE_SOLLENTUNA: SE_Sollentuna,
    LOCALE_SE_TEKNISKA_LINK: SE_TekniskaVerken_Link,
    LOCALE_BE_VREG: VregBelgium,
    LOCALE_SE_BJERKE_ENERGI: SE_Bjerke_Energi,
    LOCALE_NO_GLITRE_ENERGI: NO_GlitreEnergi,
    LOCALE_NO_AGDER_ENERGI: NO_AgderEnergi,
    LOCALE_NO_LNETT: NO_LNett,
    LOCALE_NO_TENSIO: NO_Tensio,
    LOCALE_SE_LINDE_ENERGI: SE_Linde_Energi,
    LOCALE_SE_FALBYDGENS_ENERGI: SE_FalbygdensEnergi,
    LOCALE_NO_ELVIA: NO_Elvia,
    LOCALE_NO_LEDE: NO_Lede,
    LOCALE_NO_BKK: NO_BKK,
    LOCALE_SE_MALARENERGI: SE_Malarenergi,
    LOCALE_NO_MELLOM: NO_Mellom,
    LOCALE_NO_ASKER: NO_AskerNett,
    LOCALE_SE_ELLEVIO: SE_Ellevio,
    LOCALE_SE_JBF: SE_JBF
}

"""Lookup locales for config flow"""
LOCALES = [
    LOCALE_BE_VREG,
    LOCALE_NO_AGDER_ENERGI,
    LOCALE_NO_BKK,
    LOCALE_NO_ELVIA,
    LOCALE_NO_GLITRE_ENERGI,
    LOCALE_NO_LEDE,
    LOCALE_NO_LNETT,
    LOCALE_NO_MELLOM,
    LOCALE_NO_TENSIO,
    LOCALE_NO_ASKER,
    LOCALE_SE_BJERKE_ENERGI,
    LOCALE_SE_ELLEVIO,
    LOCALE_SE_FALBYDGENS_ENERGI,
    LOCALE_SE_GOTHENBURG,
    LOCALE_SE_JBF,
    LOCALE_SE_KRISTINEHAMN,
    LOCALE_SE_LINDE_ENERGI,
    LOCALE_SE_MALUNG_SALEN,
    LOCALE_SE_MALARENERGI,
    LOCALE_SE_NACKA_NORMAL,
    LOCALE_SE_PARTILLE,
    LOCALE_SE_SALA,
    LOCALE_SE_SKOVDE,
    LOCALE_SE_SOLLENTUNA,
    LOCALE_SE_TEKNISKA_LINK,
    LOCALE_DEFAULT,
    LOCALE_NO_PEAK
    ]


class LocaleData:
    def __init__(self, input_type:str, domain:str):
        self._data = None
        self._type = input_type
        self._domain = domain
        self._data = LOCALETYPEDICT[input_type]

    @property
    def type(self) -> str:
        return self._type

    @property
    def data(self):
        return self._data