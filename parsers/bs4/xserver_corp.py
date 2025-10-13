import os
import sys
import re
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):

        # 過去データを隠しているだけで、2009年のデータまで取得できてしまうため、
        #  <li data-year="2025" data-category="お知らせ" class="news__link" style=""> のdata-yearが2025以上の場合のみ各値を取得する
        year = elem.get("data-year")
        if int(year) < 2025:
            return None

        a = elem.find("a")
        url  = self.base_url + a.get("href")
        date_str = elem.find("p", class_="news__link-date").text.strip()
        date_format = ""
        if re.search(r'^\d{4}\.\d{2}\.\d{2}$', date_str):
            date_format = "%Y.%m.%d"
        elif re.search(r'^\d{4}\/\d{2}\/\d{2}$', date_str):
            date_format = "%Y/%m/%d"
        date =  datetime.strptime(date_str, date_format)
        title = elem.find("p", class_="news__link-title").text.strip()
        return { "date": date, "url": url, "title": title, "description": None }
