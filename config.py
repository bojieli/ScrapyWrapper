#!/usr/bin/python
class ScrapyWrapperConfig():
	proxy = {
		type: "crawlera",
		enabled: True,
		apikey: "c8a6eb2f7cab4450806b9ea73187391a"
	}

	custom_settings = {
		'DOWNLOAD_DELAY': 0,
		'CONCURRENT_REQUESTS': 16
	}

	db = {
		type: "mssql",
		server: "114.215.255.52",
		user: "AddDataUser",
		password: "Dv*#d~18K",
		name: "DB_Medicine"
	}

	url_table = {
		name: "OriginalWebUrl",
		id_field: "ResID",
		url_field: "WebURL",
		time_field: "UpdateTime"
	}

	table_name = ""
	guid_field = "ID"

	check_url_exist_before_crawl = False
	on_exist_update = True

	# static list or a generator to generate list
	begin_urls = []
	steps = {
		"begin": {
			"req": {
				method: 'get', # or post
				extra_headers: {},
				cookies: {},
				post_rawdata: "",
				post_formdata: None,
				encoding: 'utf-8'
			},
			"res": {
				type: 'html', # or json
				selector_regex: "",
				next_step: 'list'
			}
		},
		"list": {
			"req": {
				method: 'get', # or post
				extra_headers: {},
				cookies: {},
				post_rawdata: "",
				post_formdata: None
			},
			"res": {
				type: 'html', # or json
				selector_regex: "",
				next_step: 'content'
			}
		},
		"content": {
			"req": {
				method: 'get', # or post
				extra_headers: {},
				cookies: {},
				post_rawdata: "",
				post_formdata: None
			},
			"res": {
				type: 'html', # or json
				selector_xpath: "",
				next_step: 'end'
			}
		}
	}

	record_preprocessor: None,
	record_fields = [{
		name: "hello",
		selector_xpath: "",
		data_validator: None,
		data_postprocessor: None,
		required: True
	}],
	# before record is inserted into database
	record_postprocessor = None

