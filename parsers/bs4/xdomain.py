import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str = elem.find("span", class_="date century").text
        date =  datetime.strptime(date_str, "%Y/%m/%d")
        a = elem.find("a", class_="hover-opacity")
        title = a.text.strip()
        url   = a.get("href")
        return { "date": date, "url": url, "title": title, "description": None }
