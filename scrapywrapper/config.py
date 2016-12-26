#!/usr/bin/python
# -*- 'coding':utf-8 -*-
class ScrapyWrapperConfig():
	name = 'MySpider'

	proxy = {
		'type': "crawlera",
		'enabled': True,
		'apikey': "c8a6eb2f7cab4450806b9ea73187391a"
	}

	custom_settings = {
		'DOWNLOAD_DELAY': 0,
		'CONCURRENT_REQUESTS': 16
	}

	db = {
		'type': "mssql",
		'server': "114.215.255.52",
		'user': "AddDataUser",
		'password': "Dv*#d~18K",
		'name': "DB_Medicine"
	}

	file_storage = {
		'type': "ftp",
		'server': "cy.zaixianshop.com",
		'user': "picuser",
		'password': "Ftp@*^#19",
		'basedir': ""
	}

	url_table = {
		'name': "OriginalWebUrl",
		'id_field': "ResID",
		'url_field': "WebURL",
		'time_field': "UpdateTime"
	}

	default_guid_field = "ID"
	check_url_exist_before_crawl = False
	on_exist_update = True

	# static list or a generator to generate list
	begin_urls = []
	steps = {
		"begin": {
			'type': "http",
			'req': {
				'method': 'get', # or post
				'extra_headers': {},
				'cookies': {},
				'post_rawdata': "",
				'post_formdata': None,
				'encoding': 'utf-8'
			},
			'res': {
				'selector_regex': "",
				'next_step': 'list'
			}
		},
		"list": {
			'type': "http",
			'req': {
				'method': 'get', # or post
				'extra_headers': {},
				'cookies': {},
				'post_rawdata': "",
				'post_formdata': None
			},
			'res': {
				'selector_regex': "",
				'next_step': 'content'
			}
		},
		"content": {
			'type': "http",
			'req': {
				'method': 'get', # or post
				'extra_headers': {},
				'cookies': {},
				'post_rawdata': "",
				'post_formdata': None
			},
			'res': {
				'selector_xpath': "",
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "",
			'guid_field': "ID",
			'preprocessor': None,
			'fields': [{
				'table_name': "",
				'guid_field': "ID",
				'name': "hello",
				'selector_xpath': "",
				'data_validator': None,
				'data_postprocessor': None,
				'required': True
			}],
			'postprocessor': None,
			'res': {
				'selector_xpath': "",
				'data_postprocessor': None,
				'next_step': 'image'
			}
		},
		"image": {
			'type': "file",
			'table_name': "PictureInfo",
			'guid_field': "ID",
			'path_field': "PicUrl",
			'info_id_field': "InfoID",
			'info_table_field': "InfoTable"
		}
	}

