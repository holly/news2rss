PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name VARCHAR(256) NOT NULL,
  created TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
  updated TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
  UNIQUE(name)
);

CREATE TABLE services (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  category_id INTEGER NOT NULL,
  name VARCHAR(256) NOT NULL,
  identifier VARCHAR(256) NOT NULL,
  executor VARCHAR(256) NOT NULL CHECK(executor IN ('bs4', 'feedparser')),
  news_url VARCHAR(256) NOT NULL,
  base_url VARCHAR(256),
  selector TEXT,
  tags TEXT,
  is_active TINYINT NOT NULL CHECK(is_active IN (0, 1)) DEFAULT 1,
  created TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
  updated TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
  UNIQUE(name),
  UNIQUE(identifier),
  FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE items (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  service_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  link  TEXT NOT NULL,
  pubdate TEXT NOT NULL,
  created TEXT NOT NULL DEFAULT (datetime('now')),
  updated TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (service_id) REFERENCES services(id) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO categories (name) VALUES
  ('web_hosting'),
  ('mail_hosting'),
  ('nocode_cms'),
  ('vps'),
  ('game_vps'), 
  ('domain'),
  ('ssl'),
  ('game'),
  ('cdn'),
  ('corp')
  ;

INSERT INTO services (name, category_id, identifier, executor, news_url, base_url, selector, tags) VALUES
  ('ConoHa WING ニュース', 1, 'conoha_wing', 'bs4', 'https://www.conoha.jp/wing/news/', 'https://www.conoha.jp', 'main > section.section.news > div > ul > li.listNews_item', '[]'),
  ('ConoHa VPS ニュース', 4, 'conoha_vps', 'bs4', 'https://www.conoha.jp/vps/news/', 'https://www.conoha.jp', 'main > section.section.news > div > ul > li.listNews_item', '[]'),
  ('ムームードメイン ニュース', 6, 'muumuu_news', 'bs4', 'https://muumuu-domain.com/information/news', 'https://muumuu-domain.com', 'main > div.muu-column-container > div > section', '[]'),
  ('ムームードメイン キャンペーン', 6, 'muumuu_campaign', 'bs4', 'https://muumuu-domain.com/information/campaigns', 'https://muumuu-domain.com', 'main > div.muu-column-container > div > section', '[]'),
  ('Xserver ニュース', 1, 'xserver', 'bs4', 'https://xserver.ne.jp/support/news.php', 'https://xserver.ne.jp', '#toggle-target > div.contents > section > section > div > dl', '[]'),
  ('Xserver Business ニュース', 1, 'xserver_business', 'bs4', 'https://business.xserver.ne.jp/news/', 'https://business.xserver.ne.jp', '#main > section > div > section > div > dl', '[]'),
  ('Xdomain ニュース', 6, 'xdomain', 'bs4', 'https://www.xdomain.ne.jp/support/news.php', 'https://www.xdomain.ne.jp', 'main > section > div > article > ul > li', '[]'),
  ('Xserver VPS ニュース', 4, 'xserver_vps', 'bs4', 'https://vps.xserver.ne.jp/support/news.php', 'https://vps.xserver.ne.jp', 'main > section > div > article > ul > li', '[]'),
  ('Xserver VPS for Game ニュース', 5, 'xserver_vps_for_game', 'bs4', 'https://vps.xserver.ne.jp/game-server/news/', 'https://vps.xserver.ne.jp/game-server/news/', '#toggle-target > div.contents > section > section > div > dl', '[]'),
  ('Xserver コーポレート ニュース', 10, 'xserver_corp', 'bs4', 'https://www.xserver.co.jp/news.php', 'https://www.xserver.co.jp/', 'div.news__wrapper > ul > li', '[]')

  ('ロリポップ ニュース', 1, 'lolipop', 'bs4', 'https://lolipop.jp/info/news/', 'https://lolipop.jp', 'main > div > div.main-body > section > div > div > ul > li', '[]'),
  ('ロリポップ キャンペーン', 1, 'lolipop_campaign', 'bs4', 'https://lolipop.jp/info/campaign/', 'https://lolipop.jp', 'main > div > div.main-body > section > div > div > ul > li', '[]'),

  ('ペライチ お知らせ', 3, 'peraichi_info', 'bs4', 'https://peraichi.com/news/info', 'https://peraichi.com', 'main > div.c-container.u-mt-sm > ul > li', '[]'),
  ('ペライチ 新機能・サービス向上', 3, 'peraichi_service', 'bs4', 'https://peraichi.com/news/service', 'https://peraichi.com', 'main > div.c-container.u-mt-sm > ul > li', '[]'),
  ('Studio お知らせ', 3, 'studio_info', 'bs4', 'https://studio.design/ja/whats-new/information', 'https://studio.design/', 'main > div.box.sd-3 > div.box.list-1 > div', '[]'),
  ('Studio 最新情報', 3, 'studio_update', 'bs4', 'https://studio.design/ja/whats-new/update', 'https://studio.design/', 'main > div.box.sd-3 > div.box.list-1 > div', '[]'),

  ('さくらのレンタルサーバ ニュース', 1, 'sakura_rs_news', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/newsreleases/feed/', '', '', '["さくらのレンタルサーバ","さくらのマネージドサーバ"]'),
  ('さくらのドメイン ニュース', 6, 'sakura_domain_news', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/newsreleases/feed/', '', '', '["ドメイン"]'),
  ('さくらのSSL ニュース', 7, 'sakura_ssl_news', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/newsreleases/feed/', '', '', '["SSL"]'),
  ('さくらのレンタルサーバ お知らせ', 1, 'sakura_rs_announcement', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/announcements/feed/', '', '', '["さくらのレンタルサーバ","さくらのマネージドサーバ"]'),
  ('さくらのドメイン お知らせ', 6, 'sakura_domain_announcement', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/announcements/feed/', '', '', '["ドメイン"]'),
  ('さくらのSSL お知らせ', 7, 'sakura_ssl_announcement', 'feedparser', 'https://www.sakura.ad.jp/corporate/information/announcements/feed/', '', '', '["SSL"]'),
  ('さくらのVPS ニュース', 4, 'sakura_vps_news', 'feedparser', 'https://vps.sakura.ad.jp/news/feed/', NULL, NULL, '[]'),
  ('MixHost ニュース', 1, 'mixhost_news', 'feedparser', 'https://mixhost.jp/news/feed', NULL, NULL, '["お知らせ"]'),
  ('お名前.com ニュース', 6, 'onamae_news', 'feedparser', 'https://www.onamae.com/news/rss/domain/', NULL, NULL, '[]'),
  ('お名前メール ニュース', 2, 'onamae_mail_news', 'feedparser', 'https://www.onamae.com/news/rss.xml?s=OM%2CRM&c=information', NULL, NULL, '[]'),
  ('お名前レンタルサーバーベーシック ニュース', 1, 'onamae_rsb_news', 'feedparser', 'https://www.onamae.com/news/rss.xml?s=RSB&c=information', NULL, NULL, '[]'),
  ('WebARENA', 1, 'webarena_news', 'feedparser', 'https://web.arena.ne.jp/news/rss/2.0.xml', NULL, NULL, '[]'),
  ('DigitalOcean News', 4, 'digitalocean_news', 'feedparser', 'https://www.digitalocean.com/blog.atom', NULL, NULL, '[]'),
  ('WIXBlog', 3, 'wix_news', 'feedparser', 'https://ja.wix.com/blog/blog-feed.xml', NULL, NULL, '[]'),
  ('Linode News &amp; Updates - Blog | Akamai', 4, 'linode_news', 'feedparser', 'https://www.linode.com/blog/feed/', NULL, NULL, '[]'),

  ('AWS Lightsail News', 4, 'lightsail_news', 'feedparser', 'https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/?search=lightsail', NULL, NULL, '[]'),
  ('AWS CloudFront News', 9, 'cloudfront_news', 'feedparser', 'https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/?search=cloudfront', NULL, NULL, '[]')
;

