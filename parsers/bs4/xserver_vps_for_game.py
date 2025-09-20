import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str = elem.find("dt", class_="headlines_box_date").text
        date =  datetime.strptime(date_str, "%Y/%m/%d")
        a = elem.find("a")
        title = a.text.strip()
        url   = self.base_url + a.get("href")
        return { "date": date, "url": url, "title": title, "description": None }
