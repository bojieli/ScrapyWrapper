#!/usr/bin/python
# -*- 'coding':utf-8 -*-
class ScrapyWrapperConfig():
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS': 1,
        #DOWNLOADER_MIDDLEWARES = {
        #    'scrapywrapper.webkit_downloader.WebkitDownloader': 1000,
        #},
        #'DOWNLOADER_MIDDLEWARES': {
        #    'scrapy_crawlera.CrawleraMiddleware': 610
        #},
        #'DOWNLOAD_HANDLERS': {
        #    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
        #    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
        #},
        #'SPIDER_MIDDLEWARES': {
        #    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
        #},
        #'WEBDRIVER_BROWSER': 'PhantomJS', # Or any other from selenium.webdriver
        #                                 # or 'your_package.CustomWebdriverClass'
        #                                 # or an actual class instead of a string.
        ## Optional passing of parameters to the webdriver
        #'WEBDRIVER_OPTIONS': {
        #    'service_args': ['--debug=true', '--load-images=false', '--webdriver-loglevel=debug']
        #},
        'TELNETCONSOLE_PORT': None,
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    crawlera_apikey = 'c8a6eb2f7cab4450806b9ea73187391a'

    db = {
        'type': "mysql",
        'server': "127.0.0.1",
        'user': "crawler",
        'password': "crawler",
        'name': "TeacherInfo"
    }

    file_storage = {
        'type': "local",
        'basedir': ''
    }

    file_db_table = {
        'table_name': 'image_info',
        'info_id_field': 'ID',
        'path_field': 'url',
        'info_table_field': 'info_table'
    }

    url_table = {
        'table_name': "original_web_url",
        'id_field': "ID",
        'url_field': "url",
        'time_field': "update_time"
    }

    page_cache_table = 'page_cache'
    file_cache_table = 'file_cache'
    save_pages = True
    use_cached_pages = True
    cache_expire_days = 14

    default_guid_field = "ID"
    check_url_exist_before_crawl = False
    on_exist_update = True
    status_report_batch = 50

    use_http_proxy = False
    http_proxy_pool = [
        'http://hwcloud.ring0.me:48526',
        'http://hwcloud2.ring0.me:48526',
        'http://conoha2.ring0.me:48526',
    ]

