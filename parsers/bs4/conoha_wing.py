import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str  = elem.find("div", class_="listNewsUnit_date").text.strip()
        date  = datetime.strptime(date_str, "%Y-%m-%d")
        title = elem.find("span", class_="textLink has-arrow textColor-inherit has-noHover").text.strip()
        href  = elem.find("a", class_="listNewsUnit").get("href")
        url   = self.base_url + href
        return { "date": date, "url": url, "title": title, "description": None }
