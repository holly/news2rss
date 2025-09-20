import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_elem = elem.find("p", attrs={'data-date-format': True})
        if date_elem:
            date_str = date_elem.text.strip()
        else:
            # studioで無い場合はおそらく「もっとみる」なので何もせずに終了
            return None
        date =  datetime.strptime(date_str, "%Y.%m.%d")
        a = elem.find("a")
        href = a.get("href")

        if re.search(r"^/.*", href):
            url  = self.base_url + href
        else:
            url = href
        title = elem.find("h2").text.strip()
        description = elem.find("p").text.strip()
        return { "date": date, "url": url, "title": title, "description": description }
