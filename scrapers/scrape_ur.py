#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import scrape_common as sc

url = 'https://www.ur.ch/themen/2962'
d = sc.download(url, silent=True)

# 2020-03-26 (and possibly earlier) from https://www.ur.ch/themen/2962
# 2020-07-07 they changed the title, so we're using the table header to find the table
# 2020-07-24 column "Genesen" was removed
"""
<table cellpadding="1" cellspacing="1" class="icms-wysiwyg-table" icms="CLEAN" style="width:100%">
	<caption><br>
	Stand: 24.07.2020, 11.00 Uhr</caption>
	<tbody>
		<tr>
			<td icms=""><strong>Positiv getestete Erkrankungsfälle</strong></td>
			<td icms=""><strong>Hospitalisiert</strong></td>
			<td icms=""><strong>Verstorben</strong></td>
		</tr>
		<tr>
			<td icms="">115</td>
			<td icms="">1</td>
			<td icms="">7</td>
		</tr>
	</tbody>
</table>
"""

# 2020-08-03 new table layout with 6 columns
"""
<table cellpadding="1" cellspacing="1" class="icms-wysiwyg-table" icms="CLEAN" style="width:100%">
	<caption><br>
	Stand: 03.08.2020, 16.00 Uhr</caption>
	<tbody>
		<tr>
			<td icms=""><strong>Aktive Fälle&nbsp;</strong></td>
			<td icms=""><strong>Positiv getestete Erkrankungsfälle</strong></td>
			<td icms=""><strong>Hospitalisiert</strong></td>
			<td icms=""><strong>Quarantäne</strong></td>
			<td icms=""><strong>Verstorben</strong></td>
			<td icms="">&nbsp;</td>
		</tr>
		<tr>
			<td icms="">4</td>
			<td icms="">117</td>
			<td icms="">0</td>
			<td icms="">47</td>
			<td icms="">7</td>
			<td icms="">&nbsp;</td>
		</tr>
	</tbody>
</table>
"""

soup = BeautifulSoup(d, 'html.parser')
data_table = soup.find(string=re.compile(r'Positiv\s+getestete\s+Erkrankungsfälle')).find_parent('table')

assert data_table, "Can't find data table"

dd = sc.DayData(canton='UR', url=url)
dd.datetime = sc.find(r'Stand[A-Za-z ]*[:,]? ([^<)]+ Uhr)<', d)

rows = data_table.find_all('tr')
assert len(rows) == 2, f"Number of rows changed, {len(rows)} != 2"

headers = rows[0].find_all('td') or rows[0].find_all('th')
assert len(headers) == 6, f"Number of header columns changed, {len(headers)} != 6"
assert headers[0].text.strip() == "Aktive Fälle"
assert headers[1].text == "Positiv getestete Erkrankungsfälle"
assert headers[2].text == "Hospitalisiert"
assert headers[3].text == "Quarantäne"
assert headers[4].text == "Verstorben"

cells = rows[1].find_all('td')
assert len(cells) == 6, f"Number of columns changed, {len(cells)} != 6"

active_cases = cells[0].text
dd.cases = cells[1].text
dd.hospitalized = cells[2].text
dd.quarantined = cells[3].text
dd.deaths = cells[4].text

dd.recovered = int(dd.cases) - int(dd.deaths) - int(active_cases)

print(dd)
