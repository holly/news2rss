import os
import sys
import re
from datetime import datetime
from parsers.feedparser.feedparser import FeedParser

class Parser(FeedParser):

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

        if "published" in entry :
            # published_parsed がNoneでpublishedに木, 28 Aug 2025 13:00:00 +0000 のような文字列がはいっているので、これをdatetimeに変換する
            # 日本語の曜日部分を除去（漢字1-3文字の曜日 + カンマ + スペース）
            # 「木,」「木曜,」「木曜日,」のパターンに対応
            # Fri, 22 Aug 2025 19:38:06 +0000 という時もある
            # Tue, 19 8月 2025 13:00:00 +0000 という時もある
            date = self.parse_chaotic_pubdate(entry["published"])

        return { "date": date, "url": url, "title": title, "description": description }

    def parse_chaotic_pubdate(self, date_str: str):

        """英語・日本語曜日混在対応の日付パーサー"""
        # 日本語曜日を英語に変換
        japanese_to_english = {
            '月': 'Mon', '月曜': 'Mon', '月曜日': 'Mon',
            '火': 'Tue', '火曜': 'Tue', '火曜日': 'Tue', 
            '水': 'Wed', '水曜': 'Wed', '水曜日': 'Wed',
            '木': 'Thu', '木曜': 'Thu', '木曜日': 'Thu',
            '金': 'Fri', '金曜': 'Fri', '金曜日': 'Fri',
            '土': 'Sat', '土曜': 'Sat', '土曜日': 'Sat',
            '日': 'Sun', '日曜': 'Sun', '日曜日': 'Sun'
        }

        # 日本語曜日があれば英語に変換
        for jp_day, en_day in japanese_to_english.items():
            pattern = f'^{re.escape(jp_day)}[,，]\\s*'
            if re.match(pattern, date_str):
                date_str = re.sub(pattern, f'{en_day}, ', date_str)
                break

         # 2. 日本語月名 → 英語月名
        japanese_months = {
            '1月': 'Jan', '2月': 'Feb', '3月': 'Mar', '4月': 'Apr',
            '5月': 'May', '6月': 'Jun', '7月': 'Jul', '8月': 'Aug', 
            '9月': 'Sep', '10月': 'Oct', '11月': 'Nov', '12月': 'Dec'
        }

        for jp_month, en_month in japanese_months.items():
            if jp_month in date_str:
                date_str = date_str.replace(jp_month, en_month)

        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
