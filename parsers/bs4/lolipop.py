import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str = elem.find("time").text.strip()
        date =  datetime.strptime(date_str, "%Y/%m/%d")
        a = elem.select("p.lol-section-top-info__title > a")[-1]
        title = a.text.strip()
        url  = self.base_url + a.get("href")
        return { "date": date, "url": url, "title": title, "description": None }
