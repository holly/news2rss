#!/usr/bin/env python

import aiohttp
import asyncio
import argparse
import os
import sys
import importlib
import re
import unicodedata
from datetime import timezone
from dotenv import load_dotenv
from feedgen.feed import FeedGenerator
from pathlib import Path

#from models import Service, Item
from models import Service, Item

LIMIT = 10
MAX_CONCURRENT = 5
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FNAME = "rss/{identifier}.xml"
S3_SYNC_CMD  = os.path.join(os.path.dirname(__file__), "s3_sync.py")
S3_BUCKET    = "rss"
TRUNCATE_WIDTH = 200
VERSION = 0.9

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--max-concurrent", type=int, default=MAX_CONCURRENT, help="Maximum number of concurrent requests")
parser.add_argument("--limit", type=int, default=LIMIT, help="Maximum number of feed items")
parser.add_argument("--output-dir", "-o", type=str, default=OUTPUT_DIR, help="rss output dir(default: {0})".format(OUTPUT_DIR))
parser.add_argument("--output-fname", "-f", type=str, default=OUTPUT_FNAME, help="rss fname format(default: {0})".format(OUTPUT_FNAME))
parser.add_argument("--skip-scraping", action="store_true",  help="skip scrape website or parse feed")
parser.add_argument("--s3-sync", action="store_true", help="enable s3 sync")
parser.add_argument("--s3-bucket",type=str, default=S3_BUCKET,  help="s3 bucket name(default: {})".format(S3_BUCKET))
parser.add_argument("--force-generate", action="store_true",  help="force generate rss files")
parser.add_argument("--version", "-v", action="version", version="{0} {1}".format(os.path.basename(__file__), VERSION))
args = parser.parse_args()


def delete_html_tag(s: str) -> str:
    return re.sub(r'<.*?>', "", s)

def truncate_text(s: str, width=TRUNCATE_WIDTH, suffix="...") -> str:
    current_width = 0
    truncated = ""
    for char in s:
        # 文字の表示幅を取得（全角=2, 半角=1）
        char_width = 2 if unicodedata.east_asian_width(char) in 'FWA' else 1
        
        if current_width + char_width + len(suffix) > width:
            return truncated + suffix
        
        truncated += char
        current_width += char_width
    
    return s



async def process_service(session: aiohttp.ClientSession, service_name: str, service_data: dict):
    """単一サービスを非同期で処理"""
    print(f"Processing {service_name}...")
    
    service_id = service_data["id"]
    news_url = service_data["news_url"]
    executor = service_data["executor"]
    base_url = service_data.get("base_url")
    selector = service_data.get("selector")
    tags = service_data.get("tags")

    try:
        async with session.get(news_url) as response:
            content = await response.text()

        mod_name = f"parsers.{executor}.{service_name}"
        mod = importlib.import_module(mod_name)
        parser = mod.Parser(content, selector=selector, base_url=base_url, tags=tags)
        news = parser.get_news()

    except Exception as e:
        print(e)
        return 


    # 新しいアイテムを収集（既存の同期メソッドを使用）
    new_items = []
    for data in news:
        if not Item.exists(
            service_id=service_id, 
            title=data["title"], 
            link=data["url"], 
            pubdate=data["date"]
        ):
            new_items.append({
                "service_id": service_id, 
                "title": data["title"], 
                "link": data["url"], 
                "pubdate": data["date"],
                "description": data.get("description")
            })
    
    print(f"{service_name} parser end. found {len(new_items)} new items")
    return service_name, new_items

async def run_sync_s3_command():
    """基本的なコマンド実行"""
    cmds = [ S3_SYNC_CMD, "--local-sync-dir", args.output_dir, "--s3-bucket", args.s3_bucket ]
    #if "AWS_PROFILE" in os.environ:
    #    cmds.extend(["--aws-profile", os.environ["AWS_PROFILE"]])
    process = await asyncio.create_subprocess_exec(
        *cmds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    return {
        'returncode': process.returncode,
        'stdout': stdout.decode('utf-8'),
        'stderr': stderr.decode('utf-8')
    }


async def write_feed_file_async(fname: str, content: str):
    """ファイル書き込みを非同期で実行"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _write_feed_file_sync, fname, content)

def _write_feed_file_sync(fname: str, content: str):
    """同期的なファイル書き込み"""
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)

async def generate_feed_async(service_name: str, service_data: dict, updated_count: int, force_generate: bool = False, limit: int = LIMIT):
    """RSSフィードを非同期で生成"""
    if updated_count == 0 and not force_generate:
        return
        
    print(f"Generating feed for {service_name}...")
    
    service_id = service_data["id"]
    category_name = service_data["category_name"]
    s3_key = args.output_fname.format(identifier=service_name, id=service_id, category_name=category_name)
    fname = os.path.join(args.output_dir, s3_key)
    output_dir = os.path.dirname(fname)
    
    # ディレクトリ作成（同期的に実行）
    if not os.path.exists(output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # アイテム取得（既存の同期メソッドを使用）
    items = Item.get_items_by_service_id(service_id, limit=limit)
    
    # RSS フィード生成
    fg = FeedGenerator()
    fg.title(service_data["name"])
    fg.link(href=service_data["news_url"], rel="alternate") 
    fg.description("feed")

    for item in items:

        fe = fg.add_entry(order="append")
        fe.title(item.title)
        fe.link(href=item.link)
        if item.description:
            fe.description(truncate_text(delete_html_tag(item.description)))
            fe.content(item.description, type="html")
        else:
            #fe.description("No description")
            pass
        fe.published(item.pubdate.replace(tzinfo=timezone.utc))
        fe.guid(item.link, permalink=True)


    #loop = asyncio.get_event_loop()
    #feed_str = await loop.run_in_executor(
    #    None, 
    #    lambda: xml.dom.minidom.parseString(feed.writeString("utf-8")).toprettyxml(indent="  ")
    #)
    #feed_str = xml.dom.minidom.parseString(feed.writeString("utf-8")).toprettyxml(indent="  ")
    feed_content = fg.rss_str(pretty=True)
    
    # ファイル書き込み（非同期）
    await write_feed_file_async(fname, feed_content.decode("utf-8"))
    print(f"Generated feed for {service_name}: {fname}")

async def main():

    services = Service.get_all_services()

    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=args.max_concurrent)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            'User-Agent': 'Mozilla/5.0 (compatible; NewsAggregator/1.0)'
        }
    ) as session:

        all_items = []
        updates = {}
        if args.skip_scraping:
            print(">> Website/Feed parse skip")
        else:
            print(">> Website/Feed parse start")
            tasks = []
            for service_name, service_data in services.items():
                task = process_service(session, service_name, service_data)
                tasks.append(task)

            # セマフォで同時実行数を制限
            semaphore = asyncio.Semaphore(args.max_concurrent)
            async def limited_process(task):
                async with semaphore:
                    return await task
            results = await asyncio.gather(*[limited_process(task) for task in tasks])
    
            print(">> Insert parsed items start")
            for service_name, new_items in results:
                updates[service_name] = len(new_items)
                all_items.extend(new_items)

            if len(all_items) > 0:
                Item.bulk_insert(all_items)
                print("Insert parsed items end. inserted {0} items".format(len(all_items)))
            else:
                print("No new items")

        print("")

    print(">> Make and output feed start")
    feed_tasks = []
    for service_name, service_data in services.items():
        updated_count = updates[service_name] if service_name in updates else 0
        feed_task = generate_feed_async(
                                service_name=service_name,
                                service_data=service_data,
                                updated_count=updated_count,
                                force_generate=args.force_generate,
                                limit=args.limit
                            ) 
        feed_tasks.append(feed_task) 
    await asyncio.gather(*feed_tasks)
    print("Feed generation completed")
    print("")

    if args.s3_sync:
        print(">> Syncing output feed to Sync S3 bucket start")
        result = await run_sync_s3_command()
        print(f"Return code: {result['returncode']}")
        print(f"Output: {result['stdout']}")
        if result['stderr']:
            print(f"Error: {result['stderr']}")
        print("Syncing s3 completed")
        print("")


    print("\n=== Summary ===")
    total_updates = sum(updates.values())
    print("Total services processed: {0}".format(len(services)))
    print("Total new items found: {0}".format(total_updates))
    for service_name, count in updates.items():
        if count > 0:
            print("  {0}: {1} new items".format(service_name, count))

if __name__ == "__main__":
    asyncio.run(main())

