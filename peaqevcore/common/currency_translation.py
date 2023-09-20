currency_formats = {
    "eur": ("€ {}", "€ {}¢"),
    "sek": ("{} kr", "{} öre"),
    "nok": ("{} kr", "{} øre"),
    "usd": ("${}", "${}¢"),
    "gbp": ("£{}", "£{}p")
}

def currency_translation(value: float | str | None, currency, use_cent: bool = False) -> str:
    value = "-" if value is None else value
    if currency.lower() in currency_formats:
        format_string = currency_formats[currency.lower()]
        ret = format_string[0].format(value) if not use_cent else format_string[1].format(value)
    else:
        ret = f"{value} {currency}"
    return ret
