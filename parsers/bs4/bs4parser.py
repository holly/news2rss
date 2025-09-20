import os
import sys
from bs4 import BeautifulSoup
from parsers.base import BaseParser

class BS4Parser(BaseParser):

    def _setup(self):
        soup = BeautifulSoup(self.content, "lxml")
        self.entries = soup.select(self.selector)

