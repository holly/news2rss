import os
import sys

class BaseParser:

    def __init__(self, content, selector=None, base_url=None, tags=None):

        self.content  = content
        self.selector = selector
        self.base_url = base_url
        self.tags = tags
        self.entries  = []

        self._setup()

    def _setup(self):
        raise NotImplementedError()

    def parse_entry(self, entry):
        raise NotImplementedError()

    def get_news(self):
        news = []
        for entry in self.entries:
            data = self.parse_entry(entry)  
            if not data:
                continue
            if isinstance(data, dict):
                news.append(data)
            if isinstance(data, list) and len(data) > 0:
                news.extend(data)
            if isinstance(data, tuple) and len(data) > 0:
                news.extend(list(data))

        return news

