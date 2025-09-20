import os
import sys
import re
from parsers.feedparser.feedparser import FeedParser

class Parser(FeedParser):

    def parse_entry(self, entry):

        data = super().parse_entry(entry)
        regex = re.compile(r'cloudfront', flags=re.IGNORECASE)
        m_title = regex.search(data["title"])
        m_desc  = regex.search(data["description"])
        if not m_title and not m_desc:
            return None
        return data
