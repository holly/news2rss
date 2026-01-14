import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):

        a = elem.find("a")
        url  = self.base_url + a.get("href")
        date_str = elem.find("span", class_="date").text.strip()
        date_format = "%Y/%m/%d"
        date =  datetime.strptime(date_str, date_format)
        title = elem.find("p", class_="title").text.strip()
        return { "date": date, "url": url, "title": title, "description": None }
