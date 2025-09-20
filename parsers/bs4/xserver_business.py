import os
import sys
from datetime import datetime, timezone, timedelta
from parsers.bs4.bs4parser import BS4Parser

class Parser(BS4Parser):

    def parse_entry(self, elem):
        news = []
        # date
        date_str = elem.dt.text
        date =  datetime.strptime(date_str, "%Y/%m/%d")
        elems2 = elem.find_all("a")
        for elem2 in elems2:
            href  = elem2.get("href")
            url   = self.base_url + "/news/" + href
            title = elem2.text
            news.append({ "date": date, "url": url, "title": title, "description": None })
        return news
