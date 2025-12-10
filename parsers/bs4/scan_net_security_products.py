import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        date_str = elem.find("time").text.strip()
        # 2025.12.10 Wed 8:00 -> Wedを削除
        cleaned = re.sub(r'\s+\w{3}\s+', ' ', date_str)
        date =  datetime.strptime(cleaned, "%Y.%m.%d %H:%M")
        h2     = elem.find("h2")
        title = h2.text.strip()
        a     = elem.find("a")
        url   = self.base_url + a.get("href")
        return { "date": date, "url": url, "title": title, "description": None }
