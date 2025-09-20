import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        # date
        p = elem.find("p", class_="muu-section__date")
        if p is None:
            return None
        date_str = p.find("span").text.strip()
        date  = datetime.strptime(date_str, "%Y-%m-%d")
        # title
        title = elem.find("h3", class_="muu-infomation__title").text
        # url
        href = elem.find("a", class_="muu-button muu-button--primary").get("href")
        url  = self.base_url + href
        return { "date": date, "url": url, "title": title, "description": None }
