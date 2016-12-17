#!/usr/bin/python
import scrapy
import pymssql
import .config
import uuid
import re
import json
import sys

class SpiderWrapper(scrapy.Spider):
	config = ScrapyWrapperConfig()

	def start_requests(self):
		self._init_db()
		if callable(self.config.begin_urls):
			for url in begin_urls():
				yield _build_request(url, "begin")
		else:
			for url in begin_urls:
				yield _build_request(url, "begin")

	def _gen_http_params(self, url, req_conf, meta=None):
		if callable(req_conf):
			return req_conf(url, meta)

		# default values
		conf = {
			url: url,
			meta: meta,
			method: 'get',
			headers: {},
			cookies: {},
			post_rawdata: None,
			post_formdata: None,
			encoding: 'utf-8'
		}
		for k in conf:
			if k in req_conf:
				if callable(req_conf[k]):
					conf[k] = req_conf[k](url, meta)
				else:
					conf[k] = req_conf[k]
		return conf

	def _build_request(self, url, curr_step, meta=None):
		if curr_step not in self.config.steps:
			raise scrapy.exceptions.CloseSpider('undefined step ' + curr_step)
		step_conf = self.config.steps[curr_step]
		req_conf = step_conf.req if "req" in step_conf or {}
		http_params = self._gen_http_params(url, req_conf, meta)

		if http_params.method.lower() == 'post' and http_params.post_formdata:
			request = scrapy.FormRequest(url=http_params.url, method=http_params.method, headers=http_params.headers, formdata=http_params.post_formdata, cookies=http_params.cookies, encoding=http_params.encoding, callback=self.parse)
		else:
			request = scrapy.Request(url=http_params.url, method=http_params.method, headers=http_params.headers, body=http_params.post_rawdata, cookies=http_params.cookies, encoding=http_params.encoding, callback=self.parse)
		request.meta['url'] = url
		request.meta['step'] = curr_step
		request.meta.meta = http_params.meta
		return request

	def _init_db(self):
		if self.config.db_type != 'mssql':
			raise "Only mssql is supported!"
		self.dbconn = pymssql.connect(self.config.db_server, self.config.db_user, self.config.db_password, self.config.db_name, charset="utf8")
		self.cursor = self.dbconn.cursor(as_dict=True)
		self.db_column_types = self._get_db_columns(self.config)

	def _get_db_columns(self, table_name):
		self.cursor.execute('SP_COLUMNS ' + tablename)
		cols = {}
		for row in self.cursor:
			cols[row['COLUMN_NAME']] = row['TYPE_NAME']
		return cols

	def _parse_response(self, response, res_conf):
		next_step = res_conf.next_step or 'end'
		meta = res_conf.meta or response.meta.meta
		results = []

		response_type = res_conf.type or 'html'
		try:
			if "selector_regex" in res_conf:
				for m in re.finditer(res_conf.selector_regex, response.body):
					results.append(m.group(0))
			elif "selector_css" in res_conf:
				for m in response.css(res_conf.selector_css):
					results.append(m.extract_first().strip())
			elif "selector_xpath" in res_conf:
				for m in response.xpath(res_conf.selector_xpath):
					results.append(m.extract_first().strip())
			elif "selector_json" in res_conf:
				obj = json.loads(response.body)
				levels = res_conf.selector_json.split('.')
				next_objs = [ obj ]
				for l in levels:
					if l == '*':
						next_objs = [ o.values() for o in next_objs ].flatten()
					else:
						next_objs = [ o[l] for o in next_objs if l in o ]
				result = [ o for o in next_objs if type(o) is str ]
			else: # plain text
				result = [ response.body ]
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response for url ' + response.url + ' (response ' + len(response.body) + ' bytes)')
			traceback.print_tb(e[2])

		return [(result, next_step, meta) for result in results]


	def _parse_record_field(self, res_conf, result, encoding='utf-8'):
		parsed = None
		try:
			if "selector_regex" in res_conf:
				m = re.search(res_conf.selector_regex, result)
				if m:
					parsed = m.group(0)
			elif "selector_css" in res_conf:
				response = scrapy.http.HtmlResponse(url=None, text=result, encoding=encoding)
				parsed = response.css(res_conf.selector_css).extract_first().strip()
			elif "selector_xpath" in res_conf:
				response = scrapy.http.HtmlResponse(url=None, text=result, encoding=encoding)
				parsed = response.xpath(res_conf.selector_xpath).extract_first().strip()
			elif "selector_json" in res_conf:
				obj = json.loads(result)
				levels = res_conf.selector_json.split('.')
				next_objs = [ obj ]
				for l in levels:
					if l == '*':
						next_objs = [ o.values() for o in next_objs ].flatten()
					else:
						next_objs = [ o[l] for o in next_objs if l in o ]
				for o in next_objs:
					if type(o) is str:
						parsed = o
						break
			else: # plain text
				parsed = result
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response for url ' + response.url + ' (response ' + len(response.body) + ' bytes)')
			traceback.print_tb(e[2])

		return [(result, next_step, meta) for result in results]

	def _parse_record(self, url, result, meta=None):
		if callable(self.config.record_preprocessor):
			(url, result, meta) = self.config.record_preprocessor(url, result, meta)
		record = {}
		for res_conf in self.config.record_fields:
			parsed = self._parse_record_field(res_conf, result)
			if parsed == None and "required" in res_conf and res_conf.required:
				print('Record parse error: required field ' + res_conf.name + ' does not exist')
				return
			if "data_validator" in res_conf and callable(res_conf.data_validator):
				if not res_conf.data_validator(parsed):
				print('Record parse error: field ' + res_conf.name + ' failed data validator (value "' + parsed + '")')
					return
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				parsed = res_conf.data_postprocessor(parsed)
			record[res_conf.name] = parsed

		if "record_postprocessor" in self.config and callable(self.config.record_postprocessor):
			record = self.config.record_postprocessor(record)
		self.insert_record(record, url)

	def parse(self, response):
		step_conf = self.config.steps[response.meta['step']]
		if "res" in step_conf:
			if callable(step_conf.res):
				results = step_conf.res(response)
			else:
				results = self._parse_response(response, step_conf.res)
		else:
			results = [ (response.body, 'end', response.meta.meta) ]

		for result in results:
			if len(result) < 2 or result[1] == "" or result[1] == 'end':
				self._parse_record(*result)
			else:
				yield self._build_request(*result)

	def insert_record(self, row, url):
		# data tab;e
		guid = self.insert_row(self.config.table_name, row)
		# url table
		url_row = {}
		url_row[self.config.guid_field] = str(uuid.uuid4())
		url_row[self.config.url_table_id_field] = guid
		url_row[self.config.url_table_url_field] = url
		url_row[self.config.url_table_time_field] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.insert_row(self.config.url_table_name, url_row)


	def insert_row(self, table_name, row):
		guid = str(uuid.uuid4())
		row[self.config.guid_field] = guid
		fields = [k for k in row]
		values = [v for v in row.values()]
		self.insert_one_with_type(table_name, fields, values)
		return guid

	def insert_one(self, table_name, fields, values):

			else:
				parsed = result
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing record for url ' + url + ' (result ' + len(result) + ' bytes)')
		return parsed

	def _parse_record(self, url, result, meta=None):
		if callable(self.config.record_preprocessor):
			(url, result, meta) = self.config.record_preprocessor(url, result, meta)
		record = {}
		for res_conf in self.config.record_fields:
			parsed = self._parse_record_field(res_conf, result)
			if parsed == None and "required" in res_conf and res_conf.required:
				print('Record parse error: required field ' + res_conf.name + ' does not exist')
				return
			if "data_validator" in res_conf and callable(res_conf.data_validator):
				if not res_conf.data_validator(parsed):
				print('Record parse error: field ' + res_conf.name + ' failed data validator (value "' + parsed + '")')
					return
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				parsed = res_conf.data_postprocessor(parsed)
			record[res_conf.name] = parsed

		if "record_postprocessor" in self.config and callable(self.config.record_postprocessor):
			record = self.config.record_postprocessor(record)
		self.insert_record(record, url)

	def parse(self, response):
		step_conf = self.config.steps[response.meta['step']]
		if "res" in step_conf:
			if callable(step_conf.res):
				results = step_conf.res(response)
			else:
				results = self._parse_response(response, step_conf.res)
		else:
			results = [ (response.body, 'end', response.meta.meta) ]

		for result in results:
			if len(result) < 2 or result[1] == "" or result[1] == 'end':
				self._parse_record(*result)
			else:
				yield self._build_request(*result)

	def insert_record(self, row, url):
		# data tab;e
		guid = self.insert_row(self.config.table_name, row)
		# url table
		url_row = {}
		url_row[self.config.guid_field] = str(uuid.uuid4())
		url_row[self.config.url_table_id_field] = guid
		url_row[self.config.url_table_url_field] = url
		url_row[self.config.url_table_time_field] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.insert_row(self.config.url_table_name, url_row)


	def insert_row(self, table_name, row):
		guid = str(uuid.uuid4())
		row[self.config.guid_field] = guid
		fields = [k for k in row]
		values = [v for v in row.values()]
		self.insert_one_with_type(table_name, fields, values)
		return guid

	def insert_one(self, table_name, fields, values):
		value_types = ['%s' for f in fields]
		self.insert_one_with_type(table_name, fields, value_types, values)

	def insert_many_with_type(self, table_name, fields, value_types, table_data):
		self.cursor.execute("INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES "
			+ ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ]),
			tuple([item for sublist in table_data for item in sublist]))
		self.conn.commit()

	def insert_one_with_type(self, table_name, fields, value_types, table_data):
		self.insertmany(table_name, fields, value_types, [table_data])

