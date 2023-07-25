import re

string = "Ecological Indicators (2022) 135"
year = re.search(r"(\d{4})", re.search(r"(\(\d{4}\))", string).group(1)).group(1)

print(year)
