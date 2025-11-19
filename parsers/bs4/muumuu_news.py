import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        # date
        p = elem.find("p", class_="muu-section__date")
        if p is None:
            return {}
        date_str = p.text
        m = re.match(r'^(\d{4}-\d{1,2}-\d{1,2})', date_str)
        if m:
            date  = datetime.strptime(m.group(0), "%Y-%m-%d")
        else:
            date = datetime.now()

        # title
        title = elem.find("h3", class_="muu-infomation__title").text
        # url
        href = elem.find("a", class_="muu-button muu-button--primary").get("href")
        url  = self.base_url + href
        return { "date": date, "url": url, "title": title, "description": None }
