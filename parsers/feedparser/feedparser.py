import os
import sys
import feedparser
import pytz
import re
import warnings
from datetime import datetime, timezone, timedelta
from parsers.base import BaseParser

class FeedParser(BaseParser):

    def _setup(self):
        atom = feedparser.parse(self.content)
        self.entries = atom["entries"]


    def parse_entry(self, entry):
        if "tags" in entry:
            if type(self.tags).__name__ == "list" and len(self.tags) > 0 and not self.exists_feed_tags(entry["tags"]):
                return None

        title = entry["title"]
        url   = entry["link"]
        if "description" in entry:
            description = entry["description"]
        else:
            description = None

        if "published_parsed" in entry :
            date = self.conv_time_struct_time_to_datetime(entry["published_parsed"])
        elif "updated" in entry:
            date = self.conv_str_to_datetime(entry["updated"])

        return { "date": date, "url": url, "title": title, "description": description }


    def exists_feed_tags(self, entry_tags):
        if type(self.tags).__name__ != "list":
            return False

        for check_tag in self.tags:
            for tag in entry_tags:
                if tag["term"] == check_tag:
                    return True

        return False


    def conv_time_struct_time_to_datetime(self, struct_time):
        tz = pytz.timezone("Asia/Tokyo")
        return datetime(*struct_time[:6], tzinfo=pytz.utc).astimezone(tz)


    def conv_str_to_datetime(self, s):
        try:
            #ISO 8601形式の場合
            return datetime.fromisoformat(s)
        except ValueError:
            # 'Wed, 24 May 2023 00:00:00 +0900'
            return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
        except Exception as e:
            warnings.warn(e)
            return None

