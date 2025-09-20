import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str = elem.find("span", class_=["u-color-gray-dark", "u-v-align-middle", "u-mr-sm"]).text.strip()
        m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        if m:
            year, month, day = map(int, m.groups())
            date = datetime(year, month, day)
        a = elem.find("a")
        title = elem.find("div", class_=["u-fs-md", "u-mt-xs"]).text.strip()
        url  = self.base_url + a.get("href")
        return { "date": date, "url": url, "title": title, "description": None }
