#!/usr/bin/python
# -*- coding:utf-8 -*-
import scrapy
import pymssql
import uuid
import re
import json
import sys
from ftplib import FTP
import tempfile
import mimetypes
import lxml
import cssselect
import html2text
import htmlentities
import traceback
import datetime
from HTMLParser import HTMLParser
from config import ScrapyWrapperConfig
from .helper import ScrapyHelper, AttrDict

class SpiderWrapper(scrapy.Spider):
	config = ScrapyWrapperConfig()

	def start_requests(self):
		self._check_config()
		self._init_db()
		if callable(self.config.begin_urls):
			for url in self.config.begin_urls():
				yield self._build_request(url, "begin")
		else:
			for url in self.config.begin_urls:
				yield self._build_request(url, "begin")

	def _gen_http_params(self, url, req_conf, meta=None):
		if callable(req_conf):
			return req_conf(url, meta)

		# default values
		conf = AttrDict({
			'url': url,
			'meta': meta,
			'method': 'get',
			'headers': {},
			'cookies': {},
			'post_rawdata': None,
			'post_formdata': None,
			'encoding': 'utf-8'
		})
		for k in conf:
			if k in req_conf:
				if callable(req_conf[k]):
					conf[k] = req_conf[k](url, meta)
				else:
					conf[k] = req_conf[k]
		return conf

	def _build_request(self, url, curr_step, meta=None, referer=None):
		if curr_step not in self.config.steps:
			raise scrapy.exceptions.CloseSpider('undefined step ' + curr_step)
		step_conf = self.config.steps[curr_step]
		if "req" in step_conf:
			req_conf = step_conf.req
		else:
			req_conf = {}
		http_params = self._gen_http_params(url, req_conf, meta)

		if http_params.method.lower() == 'post' and http_params.post_formdata:
			request = scrapy.FormRequest(url=http_params.url, method=http_params.method, headers=http_params.headers, formdata=http_params.post_formdata, cookies=http_params.cookies, encoding=http_params.encoding, callback=self._http_request_callback)
		else:
			request = scrapy.Request(url=http_params.url, method=http_params.method, headers=http_params.headers, body=http_params.post_rawdata, cookies=http_params.cookies, encoding=http_params.encoding, callback=self._http_request_callback)
		request.meta['step'] = curr_step
		request.meta['meta'] = http_params.meta
		request.meta['encoding'] = http_params.encoding
		request.meta['referer'] = referer
		return request

	def _to_attr_dict(self, c):
		if type(c) is dict:
			c = AttrDict(c)
			for k in c:
				c[k] = self._to_attr_dict(c[k])
		elif type(c) is list:
			c = [ self._to_attr_dict(v) for v in c ]
		return c

	def _check_config(self):
		c = self.config
		c.proxy = AttrDict(c.proxy)
		c.custom_settings = AttrDict(c.custom_settings)
		c.db = AttrDict(c.db)
		c.file_storage = AttrDict(c.file_storage)
		c.url_table = AttrDict(c.url_table)
		c.steps = self._to_attr_dict(c.steps)

	def _init_db(self):
		if not self.config.db:
			raise "Database config not specified"
		if self.config.db.type != 'mssql':
			raise "Only mssql is supported!"
		self.dbconn = pymssql.connect(self.config.db.server, self.config.db.user, self.config.db.password, self.config.db.name, charset="utf8")
		self.cursor = self.dbconn.cursor(as_dict=True)
		self.cursor.execute('SET ANSI_WARNINGS off')
		#self.db_column_types = self._get_db_columns(self.config.table_name)

	def _get_db_columns(self, table_name):
		self.cursor.execute('SP_COLUMNS ' + tablename)
		cols = {}
		for row in self.cursor:
			cols[row['COLUMN_NAME']] = row['TYPE_NAME']
		return cols

	def _strip_tags(self, res_conf, text):
		if "keep_html_tags" in res_conf and res_conf.keep_html_tags:
			return text.strip()
		convertor = html2text.HTML2Text()
		convertor.ignore_links = True
		return htmlentities.decode(convertor.handle(text).strip())

	def _prepare_res_conf(self, res_conf):
		if "selector_css" in res_conf:
			lxml_expr = cssselect.HTMLTranslator().css_to_xpath(res_conf.selector_css)
			res_conf.selector_xpath = lxml_expr
			del res_conf.selector_css

		if "selector_contains" in res_conf:
			res_conf.selector_xpath = '//*[contains(text(), "' + res_conf.selector_contains + '")]'
			del res_conf.selector_contains

		if "selector_table_sibling" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[contains(text(), "' + res_conf.selector_table_sibling + '")]]/following-sibling::td'
			del res_conf.selector_table_sibling

		if "selector_table_next_row" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[contains(text(), "' + res_conf.selector_table_next_row + '")]]/ancestor::tr/following-sibling::tr/td'
			del res_conf.selector_table_next_row

		if "selector_href_text" in res_conf:
			res_conf.selector_xpath = '//a[text()="' + res_conf.selector_href_text + '"]/@href'
			del res_conf.selector_href_text

		if "selector_href_contains" in res_conf:
			res_conf.selector_xpath = '//a[contains(@href, "' + res_conf.selector_href_contains + '")]/@href'
			del res_conf.selector_href_contains

		if "selector_href_text_contains" in res_conf:
			res_conf.selector_xpath = '//a[contains(text(), "' + res_conf.selector_href_text_contains + '")]/@href'
			del res_conf.selector_href_text_contains
		# in place modifications, no return

	def _parse_text_response(self, response_text, res_conf, meta):
		#if "encoding" in meta and meta['encoding'] != 'utf-8':
		#	response_text = response_text.decode(meta['encoding']).encode('utf-8')

		results = []

		try:
			self._prepare_res_conf(res_conf)
			if "parser" in res_conf and res_conf.parser == "js-string":
					from slimit import ast
					from slimit.parser import Parser
					from slimit.visitors import nodevisitor
					tree = Parser().parse(response_text)
					results = [ getattr(node, 'value') for node in nodevisitor.visit(tree) if isinstance(node, ast.String) ]

			elif "selector_xpath" in res_conf:
				doc = lxml.html.fromstring(response_text)
				if type(res_conf.selector_xpath) is list:
					for p in res_conf.selector_xpath:
						for m in doc.xpath(p):
							try:
								results.append(self._strip_tags(res_conf, lxml.etree.tostring(m)))
							except:
								results.append(self._strip_tags(res_conf, str(m)))
				else:
					for m in doc.xpath(res_conf.selector_xpath):
						try:
							results.append(self._strip_tags(res_conf, lxml.etree.tostring(m)))
						except:
							results.append(self._strip_tags(res_conf, str(m)))
			elif "selector_json" in res_conf:
				obj = json.loads(response_text)
				levels = res_conf.selector_json.split('.')
				next_objs = [ obj ]
				for l in levels:
					if l == '*':
						next_objs = [ o.values() for o in next_objs ]
						next_objs = [ item for sublist in next_objs for item in sublist ]
					else:
						next_objs = [ o[l] for o in next_objs if l in o ]
				results = [ o for o in next_objs if type(o) is str ]
			else: # plain text
				results = [ response_text ]

			# regex can be after other selectors
			if "selector_regex" in res_conf:
				regex_results = []
				for text in results:
					for m in re.finditer(res_conf.selector_regex, text):
						regex_results.append(m.group(1))
				results = regex_results

			if "selector" in res_conf and callable(res_conf.selector):
				results = [ res_conf.selector(r, meta) for r in results ]
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (response ' + str(len(response_text)) + ' bytes)')
			traceback.print_tb(e[2])

		return results

	def _mangle_text_results(self, text_results, res_conf, meta):
		results = []
		for text_result in text_results:
			result = (text_result, res_conf.next_step, meta)
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				mangled = res_conf.data_postprocessor(result)
				if mangled:
					results.append(mangled)
			else:
				results.append(result)
		return results

	def _parse_and_mangle_text_response(self, text_response, res_conf, meta):
		text_results = self._parse_text_response(text_response, res_conf, meta)
		return self._mangle_text_results(text_results, res_conf, meta)

	def _parse_http_response(self, response, res_conf):
		meta = response.meta['meta']
		if meta is None:
			meta = {}
		meta['encoding'] = response.meta['encoding']
		return self._parse_and_mangle_text_response(response.body_as_unicode(), res_conf, meta)

	def _parse_record_field(self, res_conf, result, meta):
		if "value" in res_conf:
			return res_conf.value # fixed value
		try:
			self._prepare_res_conf(res_conf)
			if "parser" in res_conf and res_conf.parser == "js-string":
					from slimit import ast
					from slimit.parser import Parser
					from slimit.visitors import nodevisitor
					tree = Parser().parse(result)
					result = [ getattr(node, 'value') for node in nodevisitor.visit(tree) if isinstance(node, ast.String) ][0]
					
			elif "selector_xpath" in res_conf:
				doc = lxml.html.fromstring(result)
				matches = []
				if type(res_conf.selector_xpath) is list:
					for p in res_conf.selector_xpath:
						for m in doc.xpath(p):
							matches.append(m)
				else:
					for m in doc.xpath(res_conf.selector_xpath):
						matches.append(m)
				if len(matches) == 0:
					result = ""
				else:
					result = self._strip_tags(res_conf, lxml.etree.tostring(matches[0]))
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
						result = o
						break
			else: # plain text
				pass

			# regex can be after other types of selectors
			if "selector_regex" in res_conf:
				m = re.search(res_conf.selector_regex, result)
				if m:
					result = m.group(1)

			if "selector" in res_conf and callable(res_conf.selector):
				result = res_conf.selector(result, meta)
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (' + str(len(result)) + ' bytes)')
			traceback.print_tb(e[2])

		return result

	def _parse_reference_field(self, res_conf, record):
		local_field = res_conf.name
		remote_table = res_conf.reference.table
		remote_id_field = res_conf.reference.remote_id_field if "remote_id_field" in res_conf.reference else "ID"
		if "remote_field" in res_conf.reference:
			remote_fields = [ res_conf.reference.remote_field ]
		elif "remote_fields" in res_conf.reference:
			remote_fields = res_conf.reference.remote_fields
		else:
			raise scrapy.exceptions.CloseSpider("unspecfied remote_field(s) in reference field " + res_conf.name)
		if "field" in res_conf.reference:
			try:
				local_data = record[res_conf.reference.field]
				if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
					local_data = res_conf.data_preprocessor(local_data)
				local_data = [ local_data ]
			except KeyError:
				return False
		elif "fields" in res_conf.reference:
			try:
				local_data = [ record[f] for f in res_conf.reference.fields ]
				if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
					local_data = res_conf.data_preprocessor(local_data)
			except KeyError:
				return False
		else:
			raise scrapy.exceptions.CloseSpider("unspecfied local field(s) in reference field " + res_conf.name)


		if "match" not in res_conf.reference:
			match = "exact"
		else:
			match = res_conf.reference.match

		if match == 'exact':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' = %s' for r in remote_fields ]), tuple(local_data))
		elif match == 'prefix':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ d + '%' for d in local_data ]))
		elif match == 'wildcard':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]) + ' LIKE %s', tuple([ '%' + d + '%' for d in local_data]))
		elif match == 'lpm':
			while local_data[0] != '':
				self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ d + '%' for d in local_data ]))
				row = self.cursor.fetchone()
				if row:
					record[local_field] = row[remote_id_field]
					return True
				else: # try with a shorter prefix
					local_data = [ d[:-1] for d in local_data ]
			return False
		else:
			raise scrapy.exceptions.CloseSpider("unknown match type " + match + " in reference field " + res_conf.name)

		# for common cases
		row = self.cursor.fetchone()
		if row:
			record[local_field] = row[remote_id_field]
			return True
		else:
			return False

	def _parse_date(self, text):
		m = re.search('([0-9]{4})-([0-9]{2})-([0-9]{2})', text)
		if m:
			return text
		m = re.search('([0-9]{4})/([0-9]{2})/([0-9]{2})', text)
		if m:
			return m.group(1) + '-' + m.group(2) + '-' + m.group(3)
		m = re.search('([0-9]{2})/([0-9]{2})/([0-9]{4})', text)
		if m:
			return m.group(3) + '-' + m.group(1) + '-' + m.group(2)
		m = re.search(u'([0-9]{4})年([0-9]{2})月([0-9]{2})日', text)
		if m:
			return m.group(1) + '-' + m.group(2) + '-' + m.group(3)
		return None

	def _parse_int(self, text):
		try:
			return int(text)
		except:
			return ScrapyHelper().parse_chinese_int(text)

	def _parse_db_record(self, conf, url, result, curr_step, meta=None):
		if "preprocessor" in conf and callable(conf.preprocessor):
			(url, result, meta) = conf.preprocessor(url, result, meta)

		reference_fields = []
		record = {}
		if "fields" not in conf:
			conf.fields = []
		for res_conf in conf.fields:
			if "reference" in res_conf:
				reference_fields.append(res_conf)
				continue
			parsed = self._parse_record_field(res_conf, result, meta)
			if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
				parsed = res_conf.data_preprocessor(parsed)
			if (parsed == None or len(parsed) == 0) and "required" in res_conf and res_conf.required:
				print('Record parse error: required field ' + res_conf.name + ' does not exist')
				return
			if "data_validator" in res_conf and callable(res_conf.data_validator):
				if not res_conf.data_validator(parsed):
					print('Record parse error: field ' + res_conf.name + ' failed data validator (value "' + parsed + '")')
					return
			if "data_type" in res_conf:
				if res_conf.data_type == "Date":
					parsed = self._parse_date(parsed)
				elif res_conf.data_type == "float":
					try:
						parsed = str(float(parsed))
					except:
						parsed = str(self._parse_int(parsed))
				elif res_conf.data_type == "int":
					parsed = str(self._parse_int(parsed))
				elif res_conf.data_type == "percentage":
					try:
						parsed = str(float(parsed.strip('%')) / 100)
					except:
						parsed = None
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				parsed = res_conf.data_postprocessor(parsed)
			if parsed:
				record[res_conf.name] = HTMLParser().unescape(parsed)

		for res_conf in reference_fields:
			status = self._parse_reference_field(res_conf, record)
			if status == False and "required" in res_conf and res_conf.required:
				print('Record parse error: required reference field ' + res_conf.name + ' not matched (value ' + record[res_conf.reference.field] + ')')
				return

		if "postprocessor" in conf and callable(conf.postprocessor):
			record = conf.postprocessor(record)

		# the next thing to do...
		if meta is None:
			meta = {}
		for k in record:
			meta[k] = record[k]				
		meta['referer'] = url

		# remove empty fields to insert to db
		if conf.type == 'db':
			for res_conf in conf.fields:
				if res_conf.name in record and record[res_conf.name] is None:
					del record[res_conf.name]
				if "skip" in res_conf and res_conf.skip:
					del record[res_conf.name]
			data_guid = self._insert_db_record(conf, url, record)
			meta['info_id'] = data_guid
			meta['info_table'] = conf.table_name

		return (result, curr_step, meta)

	def _ftp_mkdir_recursive(self, path):
		sub_path = os.path.dirname(path)
		# save pwd
		pwd = self.ftp_conn.pwd()
		try:
			self.ftp_conn.cwd(sub_path)
		except:
			self._ftp_mkdir_recursive(sub_path)
			self.ftp_conn.mkd(sub_path)
		# restore pwd
		self.ftp_conn.cwd(pwd)

	def _save_file_to_ftp(self, filename, conf, data):
		if "ftp_conn" not in self:
			self.ftp_conn = FTP(self.config.file_storage.server,
				self.config.file_storage.user,
				self.config.file_storage.password)
			if self.config.file_storage.basedir:
				self.ftp_conn.mkd(self.config.file_storage.basedir)
				self.ftp_conn.cwd(self.config.file_storage.basedir)

		f = tempfile.NamedTemporaryFile()
		f.write(data)
		try:
			self.ftp_conn.storbinary('STOR ' + filename, f.name)
		except: # in case the diretory does not exist
			self._ftp_mkdir_recursive(filename)
			self.ftp_conn.storbinary('STOR ' + filename, f.name)
		f.close()

	def _local_mkdir_recursive(self, path):
		sub_path = os.path.dirname(path)
		if not os.path.exists(sub_path):
			self._local_mkdir_recursive(sub_path)
		if not os.path.exists(path):
			os.mkdir(path)

	def _save_file_to_local(self, filename, conf, data):
		self._local_mkdir_recursive(filename)
		f = open(filename, 'wb')
		f.write(data)
		f.close()

	def _parse_file_record_callback(self, response):
		conf = self.config.file_storage
		file_uuid = str(uuid.uuid4())
		file_dir = str(datetime.date.today().year) + '/' + str(datetime.date.today().month())
		file_ext = None
		if "Content-Type" in self.headers:
			mimetype = str(self.headers["Content-Type"])
			if mimetype in mimetypes.MimeTypes().types_map_inv:
				file_ext = mimetypes.MimeTypes().types_map_inv[mimetype][0]
		if file_ext:
			filepath = file_dir + '/' + file_uuid + '.' + file_ext
		else:
			filepath = file_dir + '/' + file_uuid

		if conf.type == "ftp":
			self._save_file_to_ftp(conf, filepath, response.body)
		elif conf.type == "local":
			self._save_file_to_local(conf, filepath, response.body)
		else:
			raise scrapy.exceptions.CloseSpider('undefined record type ' + conf.type)

		db_conf = response.meta['conf']
		record = {}
		record[db_conf.path_field] = filepath
		record[db_conf.info_id_field] = response.meta['info_id']
		record[db_conf.info_table_field] = response.meta['info_table']
		self._insert_db_record(db_conf, response.url, record)

		if "res" in db_conf:
			meta = record
			meta.referer = response.url

			res_conf = db_conf.res
			if type(res_conf) is list:
				results = [ self._parse_and_mangle_text_response(response.body_as_unicode(), one_conf, meta) for one_conf in res_conf ]
				results = [ item for sublist in results for item in sublist ]
			else:
				results = self._parse_and_mangle_text_response(response.body_as_unicode(), res_conf, meta)
			for req in self._yield_requests_from_parse_results(results):
				yield req


	def _parse_file_record(self, conf, referer, url, curr_step, meta):
		req = scrapy.Request(url=url, callback=self._parse_file_record_callback)
		req.meta['referer'] = referer
		req.meta['conf'] = conf
		req.meta['info_id'] = meta.info_id
		req.meta['info_table'] = meta.info_table
		return req

	def _yield_requests_from_parse_results(self, url, results):
		for result in results:
			if len(result) < 2 or type(result[1]) is None or result[1] == 'end':
				continue
			if result[1] not in self.config.steps:
				raise scrapy.exceptions.CloseSpider('undefined step ' + result[1])
				continue
			step_config = self.config.steps[result[1]]
			if "type" not in step_config:
				step_config.type = "http" # default

			result = self._parse_db_record(step_config, url, *result)
			# the returned result has more metadata
			if step_config.type == "db":
				pass
			elif step_config.type == "file":
				yield self._parse_file_record(step_config, url, *result)
			elif step_config.type == "http":
				yield self._build_request(result[0], result[1], result[2], url)
			else:
				raise scrapy.exceptions.CloseSpider('undefined step type ' + step.config.type)


	def _http_request_callback(self, response):
		step_conf = self.config.steps[response.meta['step']]
		results = []
		if "res" in step_conf:
			if callable(step_conf.res):
				results = step_conf.res(response)
			elif type(step_conf.res) is list:
				results = [ self._parse_http_response(response, res_conf) for res_conf in step_conf.res ]
				results = [ item for sublist in results for item in sublist ]
			else:
				results = self._parse_http_response(response, step_conf.res)
		else:
			results = [ (response.body_as_unicode(), response.meta['step'], response.meta['meta']) ]

		for req in self._yield_requests_from_parse_results(response.url, results):
			yield req


	def _insert_db_record(self, conf, url, row):
		if "guid_field" not in conf:
			conf.guid_field = self.config.default_guid_field
		# data tab;e
		data_guid = str(uuid.uuid4())
		row[conf.guid_field] = data_guid
		self.insert_row(conf.table_name, row)
		# url table
		url_row = {}
		url_row[conf.guid_field] = str(uuid.uuid4())
		url_row[self.config.url_table.id_field] = data_guid
		url_row[self.config.url_table.url_field] = url
		url_row[self.config.url_table.time_field] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.insert_row(self.config.url_table.name, url_row)
		return data_guid

	def insert_row(self, table_name, row):
		fields = [k for k in row]
		values = [v for v in row.values()]
		value_types = ['%s' for k in row]
		self.insert_one_with_type(table_name, fields, value_types, values)

	def insert_many_with_type(self, table_name, fields, value_types, table_data):
		sql = "INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES " + ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ])
		data = tuple([item for sublist in table_data for item in sublist])
		try:
			self.cursor.execute(sql, data)
			self.dbconn.commit()
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			traceback.print_tb(e[2])
			print(fields)
			print(table_data)

	def insert_one_with_type(self, table_name, fields, value_types, table_data):
		self.insert_many_with_type(table_name, fields, value_types, [table_data])

