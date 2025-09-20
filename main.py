#!/usr/bin/env python

import argparse
import xml.dom.minidom
import feedparser
import os
import sys
import pytz
import requests
import warnings
from bs4 import BeautifulSoup
from datetime import datetime
from feedgenerator import Rss201rev2Feed, Atom1Feed, get_tag_uri
from pathlib import Path

#from models import Service, Item
from models import Service, Item

LIMIT = 10

FEED_URL     = "http://127.0.0.1/rss/"
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "rss")
OUTPUT_FNAME = "{identifier}.xml"

def conv_time_struct_time_to_datetime(struct_time):

    tz = pytz.timezone("Asia/Tokyo")
    return datetime(*struct_time[:6], tzinfo=pytz.utc).astimezone(tz)

def conv_str_to_datetime(s):
    try:
        #ISO 8601形式の場合
        return datetime.fromisoformat(s)
    except ValueError:
        # 'Wed, 24 May 2023 00:00:00 +0900'
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
    except Exception as e:
        warnings.warn(e)
        return None


def get_news_by_bs4(news_url, **kwargs):

    res = requests.get(news_url)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.select(kwargs["selector"])
    news  = []
    for elem in elems:

        date  = None
        title = None
        url   = None
        data  = None
        if kwargs["service"] == "conoha_wing" or kwargs["service"] == "conoha_vps":
            date_str  = elem.find("div", class_="listNewsUnit_date").text.strip()
            date  = datetime.strptime(date_str, "%Y-%m-%d")
            title = elem.find("span", class_="textLink has-arrow textColor-inherit has-noHover").text.strip()
            href  = elem.find("a", class_="listNewsUnit").get("href")
            url   = kwargs["base_url"] + href

        elif kwargs["service"] == "muumuu_news" :
            # date
            p = elem.find("p", class_="muu-section__date")
            if p is None:
                continue
            date_str = p.text
            date  = datetime.strptime(date_str, "%Y-%m-%d")
            # title
            title = elem.find("h3", class_="muu-infomation__title").text
            # url
            href = elem.find("a", class_="muu-button muu-button--primary").get("href")
            url  = kwargs["base_url"] + href

        elif kwargs["service"] == "muumuu_campaign" :
            # date
            p = elem.find("p", class_="muu-section__date")
            if p is None:
                continue
            date_str = p.find("span").text.strip()
            date  = datetime.strptime(date_str, "%Y-%m-%d")
            # title
            title = elem.find("h3", class_="muu-infomation__title").text
            # url
            href = elem.find("a", class_="muu-button muu-button--primary").get("href")
            url  = kwargs["base_url"] + href

        elif kwargs["service"] == "xserver" or kwargs["service"] == "xserver_business" :
            # date
            date_str = elem.dt.text
            date =  datetime.strptime(date_str, "%Y/%m/%d")
            elems2 = elem.find_all("a")
            for elem2 in elems2:
                href  = elem2.get("href")
                url   = kwargs["base_url"] + href.replace("..", "") if kwargs["service"] == "xserver" else news_url + href
                title = elem2.text
        elif kwargs["service"] == "xdomain" or kwargs["service"] == "xserver_vps":
            date_str = elem.find("span", class_="date century").text
            date =  datetime.strptime(date_str, "%Y/%m/%d")
            a = elem.find("a", class_="hover-opacity")
            title = a.text.strip()
            url   = a.get("href")

        elif kwargs["service"] == "lolipop" or kwargs["service"] == "lolipop_campaign" :
            date_str = elem.find("time").text.strip()
            date =  datetime.strptime(date_str, "%Y/%m/%d")
            a = elem.select("p.lol-section-top-info__title > a")[-1]
            title = a.text.strip()
            url  = kwargs["base_url"] + a.get("href")

        data = {"date": date, "url": url, "title": title, "description": None}
        news.append(data)

    return news

def get_news_by_feedparser(news_url, **kwargs):

    atom = feedparser.parse(news_url)
    news  = []

    for entry in atom["entries"]:

        if "tags" in entry:
            if type(kwargs["tags"]).__name__ == "list" and len(kwargs["tags"]) > 0 and  not exists_feed_tags(entry["tags"], kwargs["tags"]):
                continue

        title        = entry["title"]
        url          = entry["link"]
        if "description" in entry:
            description = entry["description"]
        else:
            description = None

        if "published_parsed" in entry :
            dt    = conv_time_struct_time_to_datetime(entry["published_parsed"])
        elif "updated" in entry:
            dt = conv_str_to_datetime(entry["updated"])

        data = {"date": dt, "url": url, "title": title, "description": description }
        news.append(data)

    return news


def exists_feed_tags(tags, check_tags):

    if type(check_tags).__name__ != "list":
        return False

    for check_tag in check_tags:
        for tag in tags:
            if tag["term"] == check_tag:
                return True

    return False


def main():

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    services = Service.get_all_services()
    items = []
    updates = {}

    print(">> Website/Feed parse start")
    for service in services.keys():

        service_id = services[service]["id"]
        news_url = services[service]["news_url"]
        executor = services[service]["executor"]
        base_url = services[service]["base_url"] if "base_url" in services[service] else None
        selector = services[service]["selector"] if "selector" in services[service] else None
        tags     = services[service]["tags"] if "tags" in services[service] else None

        news = []
        if service not in updates:
            updates[service] = 0

        if executor == "bs4":
            news = get_news_by_bs4(news_url, service=service, selector=selector, base_url=base_url)
        elif executor == "feedparser":
            news = get_news_by_feedparser(news_url, service=service, tags=tags)

        for data in news:
            if not Item.exists(service_id=service_id, title=data["title"], link=data["url"], pubdate=data["date"]):
                items.append({ "service_id": service_id, "title": data["title"], "link": data["url"], "pubdate": data["date"] })
                updates[service] += 1
        print("{0} parser end. update {1} items".format(service, updates[service]))
    print("")

    print(">> Insert parsed items start")
    num = len(items)
    if num > 0:
        Item.bulk_insert(items)
        print("Insert parsed items end. inserted {0} items".format(num))
    else:
        print("Now new items to insert")
    print("")
        
    print(">> Make and output feed start")
    for service in services.keys():
        if updates[service] == 0:
            continue
        service_id = services[service]["id"]
        fname = os.path.join(OUTPUT_DIR, OUTPUT_FNAME.format(identifier=service, id=service_id))
        output_dir = os.path.dirname(fname)
        if not os.path.exists(output_dir):
            Path(os.path.dirname(fname)).mkdir(parents=True)

        items = Item.get_items_by_service_id(service_id)
        feed = Rss201rev2Feed(title=services[service]["name"], link=services[service]["news_url"], description="")
        for item in items:
            feed.add_item(
                    title=item.title,
                    link=item.link,
                    description=item.description,
                    unique_id=item.link,
                    unique_id_is_permalink=True,
                    pubdate=item.pubdate
                )

        feed_str = xml.dom.minidom.parseString(feed.writeString("utf-8")).toprettyxml(indent="  ")
        with open(fname, "w") as f:
            f.write(feed_str)
    print("Feed generation completed")

    print("\n=== Summary ===")
    total_updates = sum(updates.values())
    print("Total services processed: {0}".format(len(services)))
    print("Total new items found: {0}".format(total_updates))
    for service_name, count in updates.items():
        if count > 0:
            print("  {0}: {1} new items".format(service_name, count))

if __name__ == "__main__":
    main()

