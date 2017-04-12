#!/usr/bin/python
# -*- coding:utf-8 -*-
import scrapy
import pymssql
import uuid
import re
import json
import demjson
import sys
from ftplib import FTP
import tempfile
import mimetypes
import lxml
import cssselect
import html2text
import traceback
import datetime
from HTMLParser import HTMLParser
from config import ScrapyWrapperConfig
from urlparse import urljoin
from .helper import ScrapyHelper, AttrDict
import types
import copy
from scrapy_webdriver.http import WebdriverRequest
import os
import urllib2
import urllib
from collections import deque
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

utf8_parser = lxml.etree.HTMLParser(encoding='utf-8')

class SpiderWrapper(scrapy.Spider):
	def spider_closed(self, spider):
		print('Report spider status for the last time...')
		# mark as complete
		self.counter.status = 1
		self.report_status(force=True)

	def start_requests(self):
		self._check_config()
		self._init_db()
		self.__total_records_reported = False
		self.__accumulative_report_counter = 0
		self.counter = AttrDict({
		    'status': 0,
		    'crawled_webpages': 0,
		    'total_records': 0,
		    'new_records': 0,
		    'updated_records': 0,
		    'saved_images': 0,
		    'error_count': 0
		})
		dispatcher.connect(self.spider_closed, signals.spider_closed)

		if callable(self.config.begin_urls):
			for url in self.config.begin_urls():
				for req in self._build_request(url, "begin"):
					yield req
		else:
			for url in self.config.begin_urls:
				for req in self._build_request(url, "begin"):
					yield req

	def _gen_http_params(self, url, req_conf, meta=None):
		if callable(req_conf):
			req = req_conf(url, meta)
			if type(req) is dict:
				yield req
			elif type(req) is list:
				for item in req:
					for params in self._gen_http_params(url, item, meta):
						yield params
			elif isinstance(req, types.GeneratorType):
				for genvar in req:
					for params in self._gen_http_params(url, genvar, meta):
						yield params
			else:
				raise scrapy.exceptions.CloseSpider('req_conf return value is neither dict, nor iterable')
			return
		elif type(req_conf) is list:
			for item in req_conf:
				for params in self._gen_http_params(url, item, meta):
					yield params
			return

		# default values
		conf = {
			'url': url,
			'meta': meta,
			'method': 'get',
			'headers': {},
			'cookies': {},
			'post_rawdata': None,
			'post_formdata': None,
			'encoding': 'utf-8',
			'dont_filter': False, # automatic URL deduplication
			'webview': False,
			'debug': False
		}
		for k in conf:
			if k in req_conf:
				if callable(req_conf[k]):
					conf[k] = req_conf[k](url, meta)
				else:
					conf[k] = copy.deepcopy(req_conf[k])

		if type(conf['post_formdata']) is str:
			l = conf['post_formdata'].split('&')
			forms = {}
			for i in l:
				kv = i.split('=')
				forms[kv[0]] = kv[1]
			conf['post_formdata'] = forms

		if type(conf['cookies']) is str:
			l = conf['cookies'].split(';')
			cookies = {}
			for i in l:
				kv = i.split('=')
				cookies[kv[0]] = kv[1].strip()
			conf['cookies'] = cookies

		# disable filtering POST requests
		if conf['method'] == 'post' and 'dont_filter' not in req_conf:
			conf['dont_filter'] = True

		if 'post_formdata' in conf and conf['post_formdata'] is not None:
			for k in conf['post_formdata']:
				if callable(conf['post_formdata'][k]):
					conf['post_formdata'][k] = conf['post_formdata'][k](url, meta)
		yield conf

	def _build_request(self, url, curr_step, meta=None, referer=None):
		if curr_step not in self.config.steps:
			raise scrapy.exceptions.CloseSpider('undefined step ' + curr_step)
		step_conf = self.config.steps[curr_step]
		if "req" in step_conf:
			req_conf = step_conf.req
		else:
			req_conf = {}

		for http_params in self._gen_http_params(url, req_conf, meta):
			if 'encoding' in http_params and http_params['encoding'] != 'utf-8':
				http_params['url'] = http_params['url'].encode(http_params['encoding'])
			else:
				http_params['encoding'] = 'utf-8'

			if referer:
				http_params['url'] = urljoin(referer, http_params['url'])

			if 'webview' in http_params and http_params['webview']:
				request = WebdriverRequest(
					url=http_params['url'],
					method=http_params['method'],
					headers=http_params['headers'] if 'headers' in http_params else None,
					#formdata=http_params['post_formdata'],
					cookies=http_params['cookies'] if 'cookies' in http_params else None,
					encoding=http_params['encoding'] if 'encoding' in http_params else None,
					dont_filter=http_params['dont_filter'] if 'dont_filter' in http_params else None,
					callback=self._http_request_callback)
			elif http_params['method'].lower() == 'post' and "post_formdata" in http_params and http_params['post_formdata']:
				request = scrapy.FormRequest(
					url=http_params['url'],
					method=http_params['method'],
					headers=http_params['headers'] if 'headers' in http_params else None,
					formdata=http_params['post_formdata'],
					cookies=http_params['cookies'] if 'cookies' in http_params else None,
					encoding=http_params['encoding'] if 'encoding' in http_params else None,
					dont_filter=http_params['dont_filter'] if 'dont_filter' in http_params else None,
					callback=self._http_request_callback)
			else:
				request = scrapy.FormRequest(
					url=http_params['url'],
					method=http_params['method'],
					headers=http_params['headers'] if 'headers' in http_params else None,
					body=http_params['post_rawdata'] if 'post_rawdata' in http_params else None,
					cookies=http_params['cookies'] if 'cookies' in http_params else None,
					encoding=http_params['encoding'] if 'encoding' in http_params else None,
					dont_filter=http_params['dont_filter'] if 'dont_filter' in http_params else None,
					callback=self._http_request_callback)

			request.meta['$$step'] = curr_step
			request.meta['$$meta'] = http_params['meta']
			request.meta['$$encoding'] = http_params['encoding']
			request.meta['$$referer'] = referer

			if ('new_session' in http_params and http_params['new_session']) or (meta and '$$new_session' in meta and meta['$$new_session']):
				if not hasattr(self, '_session_id'):
					self._session_id = 1
				request.meta['cookiejar'] = self._session_id
				self._session_id += 1
			elif meta and '$$session_id' in meta:
				request.meta['cookiejar'] = meta['$$session_id']

			request.meta['$$http_debug'] = 'debug' in http_params and http_params['debug']

			if 'webview' in http_params and http_params['webview']:
				request.meta['$$webview'] = True
			else:
				request.meta['$$webview'] = False
			yield request

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
		c.db = AttrDict(c.db)
		c.file_storage = AttrDict(c.file_storage)
		c.file_db_table = AttrDict(c.file_db_table)
		c.url_table = AttrDict(c.url_table)
		c.steps = self._to_attr_dict(c.steps)
		self.reference_cache = {}
		if type(c.status_report_batch) is not int:
			raise "status_report_batch should be an integer"

	def _init_db(self):
		if not self.config.db:
			raise "Database config not specified"
		if self.config.db.type != 'mssql':
			raise "Only mssql is supported!"
		self.dbconn = pymssql.connect(self.config.db.server, self.config.db.user, self.config.db.password, self.config.db.name, charset="utf8", timeout=60, login_timeout=60, autocommit=True, as_dict=True)
		self.cursor = self.dbconn.cursor()
		self.cursor.execute('SET ANSI_WARNINGS OFF')
		#self.db_column_types = self._get_db_columns(self.config.table_name)

	def _get_db_columns(self, table_name):
		self.cursor.execute('SP_COLUMNS ' + tablename)
		cols = {}
		for row in self.cursor:
			cols[row['COLUMN_NAME']] = row['TYPE_NAME']
		return cols

	def _strip_tags(self, to_strip, text):
		if to_strip:
			convertor = html2text.HTML2Text()
			convertor.ignore_links = True
			try:
				text = convertor.handle(text)
			except:
				pass
		return text.replace("\\n", "\n").strip()

	def _prepare_res_conf(self, res_conf):
		if "selector_css" in res_conf:
			lxml_expr = cssselect.HTMLTranslator().css_to_xpath(res_conf.selector_css)
			res_conf.selector_xpath = lxml_expr
			del res_conf.selector_css

		if "selector_contains" in res_conf:
			res_conf.selector_xpath = '//*[contains(text(), "' + res_conf.selector_contains + '")]'
			del res_conf.selector_contains

		if "selector_table_sibling_contains" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[contains(text(), "' + res_conf.selector_table_sibling_contains + '")]]/following-sibling::td'
			del res_conf.selector_table_sibling_contains

		if "selector_table_sibling" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[text()[normalize-space()="' + res_conf.selector_table_sibling + '"]]]/following-sibling::td'
			del res_conf.selector_table_sibling

		if "selector_dt" in res_conf:
			res_conf.selector_xpath = '//dt[descendant-or-self::*[text()[normalize-space()="' + res_conf.selector_dt + '"]]]/following-sibling::dd'
			del res_conf.selector_dt

		if "selector_table_next_row_contains" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[contains(text(), "' + res_conf.selector_table_next_row_contains + '")]]/ancestor::tr/following-sibling::tr/td'
			del res_conf.selector_table_next_row_contains

		if "selector_table_next_row" in res_conf:
			res_conf.selector_xpath = '(//td|//th)[descendant-or-self::*[text()[normalize-space()="' + res_conf.selector_table_next_row + '"]]]/ancestor::tr/following-sibling::tr/td'
			del res_conf.selector_table_next_row

		if "selector_href_text" in res_conf:
			res_conf.selector_xpath = '//a[text()[normalize-space()="' + res_conf.selector_href_text + '"]]/@href'
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

		if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
			response_text = res_conf.data_preprocessor(response_text, meta)

		try:
			self._prepare_res_conf(res_conf)
			# parsers
			if "parser" in res_conf:
				if res_conf.parser == 'js-object':
					m = re.search('var\s+[a-zA-Z0-9_$]+\s*=\s*(.*)', response_text)
					if not m:
						response_text = ""
						results = []
					else:
						response_text = m.group(1).strip(';')
						results = [ response_text ]

			# selectors
			if "selector_table" in res_conf:
				doc = lxml.html.fromstring(response_text, parser=utf8_parser)
				col_keys = [ lxml.etree.tostring(field, method='text', encoding=unicode).strip() for field in doc.xpath('//tr[1]/td')[1:] ]
				records = [ { "$$key": key } for key in col_keys ]
				for row in doc.xpath('//tr')[1:]:
					row_key = lxml.etree.tostring(row.xpath('.//td[1]')[0], method='text', encoding=unicode).strip()
					col_id = 0
					for col in row.xpath('.//td')[1:]:
						try:
							records[col_id][row_key] = lxml.etree.tostring(col, method='text', encoding=unicode).strip()
							col_id += 1
						except: # no such column
							break
				results = [ json.dumps(r, ensure_ascii=False) for r in records ]

			elif "selector_matrix" in res_conf:
				doc = lxml.html.fromstring(response_text, parser=utf8_parser)
				matrix = []
				for row in doc.xpath('//tr'):
					col_count = 0
					for col in row.xpath('.//td|.//th'):
						if len(matrix) <= col_count:
							matrix.append([])
						matrix[col_count].append(lxml.etree.tostring(col, method='text', encoding=unicode))
						col_count += 1

				try:
					if res_conf.selector_matrix['has_header']:
						matrix = matrix[1:]
				except:
					pass
				return [ ''.join([ '<td>' + x + '</td>' for x in col ]) for col in matrix ]

			elif "selector_xpath" in res_conf:
				#if "keep_entities" in res_conf and res.keep_entities:
				#	pass
				#else:
				#	response_text = HTMLParser().unescape(response_text)
				doc = lxml.html.fromstring(response_text, parser=utf8_parser)
				try:
					if "strip_tags" in res_conf:
						to_strip = res_conf.strip_tags
					else:
						to_strip = False
					if type(res_conf.selector_xpath) is list:
						for p in res_conf.selector_xpath:
							for m in doc.xpath(p):
								try:
									serialize_method = 'text' if to_strip else 'html'
									results.append(lxml.etree.tostring(m, method=serialize_method, encoding=unicode))
								except:
									results.append(self._strip_tags(to_strip, unicode(m)))
					else:
						for m in doc.xpath(res_conf.selector_xpath):
							try:
								serialize_method = 'text' if to_strip else 'html'
								results.append(lxml.etree.tostring(m, method=serialize_method, encoding=unicode))
							except:
								results.append(self._strip_tags(to_strip, unicode(m)))
				except:
					raise scrapy.exceptions.CloseSpider('invalid selector_xpath ' + str(res_conf.selector_xpath))

			elif "selector_json" in res_conf:
				results = [] # default empty
				obj = None
				try:
					obj = json.loads(response_text)
				except:
					try:
						obj = demjson.decode(response_text)
					except:
						print('JSON parse failed: ')
						print('----- begin JSON -----')
						print(response_text)
						print('----- end JSON -----')

				if obj:
					if type(obj) is list:
						next_objs = obj
					else:
						next_objs = [ obj ]

					# escape '\.'
					levels = []
					part = ""
					for l in res_conf.selector_json.split('.'):
						if l[-1:] == '\\':
							part = l[:-1] + '.'
						else:
							levels.append(part + l)
							part = ""
					if part != "":
						levels.append(part)

					for l in levels:
						if l == '':
							continue
						elif l == '*':
							next_objs = [ o.values() for o in next_objs ]
							next_objs = [ item for sublist in next_objs for item in sublist ]
						else:
							new_objs = []
							for o in next_objs:
								if type(o) is list:
									if l.isdigit():
										if len(o) > int(l):
											new_objs.append(o[int(l)])
									else:
										next_objs.extend(o)
								elif type(o) is dict and l in o:
									new_objs.append(o[l])
							next_objs = new_objs

					new_objs = []
					for o in next_objs:
						if type(o) is list:
							new_objs.extend(o)
						else:
							new_objs.append(o)
					results = [ json.dumps(o, ensure_ascii=False).strip('"') for o in new_objs ]
			# end selector json

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
				new_results = []
				for r in results:
					res = res_conf.selector(r, meta)
					if type(res) is list:
						new_results.extend(res)
					else:
						new_results.append(res)
				results = new_results

			if "data_validator" in res_conf and callable(res_conf.data_validator):
				results = [ r for r in results if res_conf.data_validator(r, meta) ]
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (response ' + str(len(response_text)) + ' bytes)')
			traceback.print_tb(e[2])

		if 'required' in res_conf and res_conf['required']:
			if len(results) == 0:
				print('Record parse error: no results matching selector ' + str(res_conf))
				print('Full record: ')
				print(repr(response_text)[:10000])
				self.counter.error_count += 1
				self.report_status(force=True)

		if 'limit' in res_conf and len(results) > res_conf.limit:
			results = results[:res_conf.limit]

		return results

	def _mangle_text_results(self, text_results, res_conf, meta):
		results = []
		for text_result in text_results:
			local_meta = copy.deepcopy(meta)
			result = (text_result, res_conf.next_step, local_meta)
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				mangled = res_conf.data_postprocessor(text_result, local_meta)
				results.append((mangled, res_conf.next_step, local_meta))
			else:
				results.append(result)
		return results

	def _parse_and_mangle_text_response(self, text_response, res_conf, meta):
		text_results = self._parse_text_response(text_response, res_conf, meta)
		return self._mangle_text_results(text_results, res_conf, meta)

	def _parse_http_response(self, response, res_conf):
		meta = response.meta['$$meta']
		if meta is None:
			meta = {}
		meta['$$referer'] = response.meta['$$referer']
		meta['$$url'] = response.url
		meta['$$encoding'] = response.meta['$$encoding']
		meta['$$new_session'] = res_conf['new_session'] if 'new_session' in res_conf else False
		if 'cookiejar' in response.meta and not meta['$$new_session']:
			meta['$$session_id'] = response.meta['cookiejar']

		body = None
		try:
			if response.meta['$$encoding']:
				body = response.body.decode(response.meta['$$encoding']).encode('utf-8')
		except:
			pass

		if body is None:
			try:
				body = response.body_as_unicode()
			except:
				body = response.body

		if '$$http_debug' in response.meta and response.meta['$$http_debug']:
			print('----------------')
			print(response.url)
			try:
				print(response.request.body)
			except:
				print(response.request)
			print(body)
			print('================')

		return self._parse_and_mangle_text_response(body, res_conf, meta)

	def _parse_record_field(self, res_conf, result, meta):
		if "value" in res_conf:
			return res_conf.value # fixed value
		try:
			self._prepare_res_conf(res_conf)
			if "parser" in res_conf:
				if res_conf.parser == "js-string":
					from slimit import ast
					from slimit.parser import Parser
					from slimit.visitors import nodevisitor
					tree = Parser().parse(result)
					result = [ getattr(node, 'value') for node in nodevisitor.visit(tree) if isinstance(node, ast.String) ][0]
				elif res_conf.parser == 'js-object':
					m = re.search('var\s+[a-zA-Z0-9_$]+=\s+(.*)')
					if not m:
						result = ''
					else:
						result = m.group(1)
					
			elif "selector_xpath" in res_conf:
				doc = lxml.html.fromstring(result, parser=utf8_parser)
				matches = []
				if type(res_conf.selector_xpath) is list:
					for p in res_conf.selector_xpath:
						for m in doc.xpath(p):
							matches.append(m)
				else:
					for m in doc.xpath(res_conf.selector_xpath):
						matches.append(m)
				if len(matches) == 0:
					result = ''
				else:
					if "strip_tags" in res_conf:
						to_strip = res_conf.strip_tags
					else:
						to_strip = True
					serialize_method = 'text' if to_strip else 'html'
					try:
						result = lxml.etree.tostring(matches[0], method=serialize_method, encoding=unicode)
					except:
						result = self._strip_tags(to_strip, unicode(matches[0]))

			elif "selector_json" in res_conf:
				obj = None
				try:
					obj = json.loads(result)
				except:
					try:
						obj = demjson.decode(result)
					except:
						print('JSON parse failed: ')
						print('----- begin JSON -----')
						print(result)
						print('----- end JSON -----')
						result = '' # default empty

				if obj:
					if type(obj) is list:
						next_objs = obj
					else:
						next_objs = [ obj ]

					# escape '\.'
					levels = []
					part = ""
					for l in res_conf.selector_json.split('.'):
						if l[-1:] == '\\':
							part = l[:-1] + '.'
						else:
							levels.append(part + l)
							part = ""
					if part != "":
						levels.append(part)

					for l in levels:
						if l == '':
							continue
						elif l == '*':
							next_objs = [ o.values() for o in next_objs ]
							next_objs = [ item for sublist in next_objs for item in sublist ]
						else:
							new_objs = []
							for o in next_objs:
								if type(o) is list:
									if l.isdigit():
										if len(o) > int(l):
											new_objs.append(o[int(l)])
									else:
										next_objs.extend(o)
								elif type(o) is dict and l in o:
									new_objs.append(o[l])
							next_objs = new_objs

					result = ''
					for o in next_objs:
						if type(o) is list:
							o = o[0]

						if type(o) is str or type(o) is unicode:
							result = o
							break
						elif type(o) is int or type(o) is float:
							result = str(o)
							break
						elif type(o) is bool:
							result = str(int(o))
							break
			# end selector json

			else: # original text
				pass

			# regex can be after other types of selectors
			if "selector_regex" in res_conf:
				m = re.search(res_conf.selector_regex, result)
				if m:
					result = m.group(1)
				else:
					result = ''

			if "strip_tags" in res_conf:
				to_strip = res_conf.strip_tags
			else:
				to_strip = True
			result = self._strip_tags(to_strip, result)

			if "selector" in res_conf and callable(res_conf.selector):
				result = res_conf.selector(result, meta)
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (' + str(len(result)) + ' bytes)')
			traceback.print_tb(e[2])

		if result is not None:
			if type(result) is not unicode:
				try:
					result = result.decode('utf-8', 'ignore')
				except:
					result = unicode(result)
			result = result.strip()
		return result

	def _parse_reference_field(self, res_conf, record):
		local_field = res_conf.name
		record[local_field] = None
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
					local_data = res_conf.data_preprocessor(local_data, record)
				local_data = [ local_data ]
			except KeyError:
				return False
		elif "fields" in res_conf.reference:
			try:
				local_data = [ record[f] for f in res_conf.reference.fields ]
				if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
					local_data = res_conf.data_preprocessor(local_data, record)
			except KeyError:
				return False
		else:
			raise scrapy.exceptions.CloseSpider("unspecfied local field(s) in reference field " + res_conf.name)


		if "match" not in res_conf.reference:
			match = "exact"
		else:
			match = res_conf.reference.match

		for d in local_data:
			if d is None:
				return False

		is_cached = "cache" not in res_conf.reference or res_conf.reference.cache
		# find from cache
		if remote_table in self.reference_cache:
			to_match = '&&&'.join(local_data)
			if to_match in self.reference_cache[remote_table]:
				record[local_field] = self.reference_cache[remote_table][to_match]
				return True
		elif is_cached: # initialize the cache
			self.reference_cache[remote_table] = {}

		if match == 'exact':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' = %s' for r in remote_fields ]), tuple(local_data))
		elif match == 'prefix':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ d + '%' for d in local_data ]))
		elif match == 'wildcard':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ '%' + d + '%' for d in local_data]))
		elif match == 'lpm':
			# find from cache
			if is_cached:
				to_match_cache = local_data
				while to_match_cache[0] and len(to_match_cache[0]) != 0:
					to_match = '&&&'.join(to_match_cache)
					if to_match in self.reference_cache[remote_table]:
						record[local_field] = self.reference_cache[remote_table][to_match]
						return True
					else: # try with a shorter prefix
						to_match_cache = [ d[:-1] for d in to_match_cache ]
			# fetch from DB
			while local_data[0] and len(local_data[0]) != 0:
				self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ d + '%' for d in local_data ]))
				row = self.cursor.fetchone()
				if row:
					record[local_field] = row[remote_id_field]
					if is_cached:
						self.reference_cache[remote_table]['&&&'.join(local_data)] = row[remote_id_field]
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
			if is_cached:
				self.reference_cache[remote_table]['&&&'.join(local_data)] = row[remote_id_field]
			return True
		else:
			if 'insert_if_not_exist' in res_conf.reference and res_conf.reference['insert_if_not_exist']:
				row = dict(zip(remote_fields, local_data))
				gen_uuid = str(uuid.uuid4())
				row[remote_id_field] = gen_uuid
				self.insert_row(remote_table, row)
				record[local_field] = gen_uuid
				return True
			else:
				return False

	def _make_date_string(self, year, month, day):
		return ("%04d" % int(year)) + '-' + ("%02d" % int(month)) + '-' + ("%02d" % int(day))

	def _parse_date(self, text):
		if not text:
			return None
		text = text.replace(' ', '')
		m = re.search(u'^([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{2})-([0-9]{1,2})-([0-9]{1,2})', text)
		if m:
			if int(m.group(1)) >= '70': # 1970 - 1999
				return self._make_date_string('19' + m.group(1), m.group(2), m.group(3))
			else: # >= 2000
				return self._make_date_string('20' + m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})', text)
		if m:
			return self._make_date_string(m.group(3), m.group(1), m.group(2))
		m = re.search('^([0-9]{1,2})/([0-9]{1,2})/([0-9]{2})', text)
		if m:
			if int(m.group(1)) >= '70': # 1970 - 1999
				return self._make_date_string('19' + m.group(3), m.group(1), m.group(2))
			else: # >= 2000
				return self._make_date_string('20' + m.group(3), m.group(1), m.group(2))
		m = re.search(u'^([0-9]{4})年([0-9]{1,2})月', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), 1)
		m = re.search(u'^([0-9]{4})年', text)
		if m:
			return self._make_date_string(m.group(1), 1, 1)
		m = re.search(u'^([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})', text)
		if m:
			return m.group(1) + '-' + m.group(2) + '-' + m.group(3) + ' ' + m.group(4) + ':' + m.group(5) + ':' + m.group(6)
		m = re.search(u'^([0-9]{4})([0-9]{2})([0-9]{2})', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		return None

	def _parse_int(self, text):
		if not text:
			return None
		text = text.replace(',', '')
		parsed = ScrapyHelper().parse_chinese_int(text)
		if parsed:
			return int(parsed)
		try:
			m = re.search('[0-9-][0-9]*', text)
			return int(m.group(0))
		except:
			return None

	def _parse_float(self, text):
		if not text:
			return None
		text = text.replace(',', '')
		parsed = ScrapyHelper().parse_chinese_int(text)
		if parsed is not None:
			return float(parsed)
		try:
			m = re.search('[0-9.-][0-9.]*', parsed.replace(',', ''))
			return float(m.group(0))
		except:
			return None


	def _get_image_urls_from_doc(self, doc):
		for m in doc.xpath('//img/@src'):
			yield str(m)

		for m in doc.xpath('//a/@href'):
			re_m = re.search('\.(jpg|png|gif|bmp|doc|docx|xls|xlsx|ppt|pptx|zip|rar)$', str(m))
			if re_m:
				yield str(m)

	def _download_images_from_html(self, response_text, meta):
		if not response_text:
			return response_text

		image_urls = []

		try:
			doc = lxml.html.fromstring(response_text, parser=utf8_parser)
		except:
			return response_text

		for m in self._get_image_urls_from_doc(doc):
			response = AttrDict()
			response.url = urljoin(meta['$$url'], m)
			response.meta = meta
			try:
				response.body_stream = urllib2.urlopen(response.url)
			except:
				print('Failed to download image "' + response.url + '" in article "' + meta['$$url'] + '"')
				continue
			response.headers = {}
			record = self._save_file_record(response)
			if record:
				filepath, _ = record
				image_urls.append((filepath, response.url))
				response_text = response_text.replace(m, filepath)

		if '$$image_urls' not in meta:
			meta['$$image_urls'] = []
		meta['$$image_urls'].extend(image_urls)
		return response_text
	
	def _parse_db_field(self, res_conf, result, meta):
		if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
			result = res_conf.data_preprocessor(result, meta)

		parsed = self._parse_record_field(res_conf, result, meta)

		if "data_type" in res_conf:
			if res_conf.data_type == "Date":
				parsed = self._parse_date(parsed)
			elif res_conf.data_type == "float":
				parsed = self._parse_float(parsed)
			elif res_conf.data_type == "int":
				parsed = self._parse_int(parsed)
			elif res_conf.data_type == "percentage":
				try:
					m = re.search('([0-9.-][0-9.]*)%', parsed.replace(',', ''))
					parsed = float(m.group(1))
				except:
					parsed = None

		if type(parsed) is not str and type(parsed) is not unicode and parsed is not None:
			parsed = str(parsed)
		if "data_validator" in res_conf and callable(res_conf.data_validator):
			if not res_conf.data_validator(parsed, meta):
				#print('Record parse error: field ' + res_conf.name + ' failed data validator (value "' + parsed + '")')
				#print('Full record: ' + result)
				return False
		if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
			parsed = res_conf.data_postprocessor(parsed, meta)
		if "download_images" in res_conf and res_conf.download_images:
			parsed = self._download_images_from_html(parsed, meta)
		if "required" in res_conf and res_conf.required:
			if parsed == None or len(parsed) == 0:
				if not "mute_warnings" in res_conf:
					print('Record parse error: required field ' + res_conf.name + ' does not exist')
					print('Full record: ')
					try:
						print(repr(result)[:1000])
					except:
						print(result.encode('utf-8')[:10000])
					self.counter.error_count += 1
					self.report_status(force=True)
				return False
		meta[res_conf.name] = parsed
		return True

	def _order_fields_by_dependency(self, confs):
		dep_graph = {}
		for conf in confs:
			dep_graph[conf.name] = set()
			if "reference" in conf:
				if "fields" in conf.reference:
					dep_graph[conf.name].update(set(conf.reference.fields))
				elif "field" in conf.reference:
					dep_graph[conf.name].add(conf.reference.field)
			if "dependencies" in conf:
				dep_graph[conf.name].update(set(conf.dependencies))

		GRAY, BLACK = 0, 1
		enter = set(dep_graph)
		state = {}
		ordered = []

		def dfs(node):
			state[node] = GRAY
			for k in dep_graph.get(node, ()):
				sk = state.get(k, None)
				if sk == GRAY:
					raise ValueError("Circular dependency in reference conf!")
				if sk == BLACK:
					continue
				enter.discard(k)
				dfs(k)
			ordered.append(node)
			state[node] = BLACK

		while enter:
			dfs(enter.pop())

		confs_dict = {}
		for conf in confs:
			confs_dict[conf.name] = conf
		return [confs_dict[name] for name in ordered]

	def _parse_db_record(self, conf, url, result, curr_step, meta=None):
		if "preprocessor" in conf and callable(conf.preprocessor):
			(url, result, meta) = conf.preprocessor(url, result, meta)

		# populate record with meta
		if type(meta) is not dict:
			meta = {}
		else: # copy the dict!
			meta = copy.deepcopy(meta)
		meta['$$referer'] = url

		if "fields" not in conf:
			conf.fields = []

		if "$$dependency_ordered" not in conf:
			conf.fields = self._order_fields_by_dependency(conf.fields)
			conf['$$dependency_ordered'] = True

		for res_conf in conf.fields:
			if "reference" in res_conf:
				status = self._parse_reference_field(res_conf, meta)
				if status == False and "required" in res_conf and res_conf.required:
					print('Record parse error: required reference field ' + res_conf.name + ' not matched (value "' + meta[res_conf.reference.field].encode('utf-8') + '")')
					print('Full record: ')
					print(result.encode('utf-8')[:10000])
					self.counter.error_count += 1
					self.report_status(force=True)
					return
			else: # normal field
				if not self._parse_db_field(res_conf, result, meta):
					return

		if "postprocessor" in conf and callable(conf.postprocessor):
			meta = conf.postprocessor(meta)

		# remove empty fields to insert to db
		if conf.type == 'db':
			for res_conf in conf.fields:
				if res_conf.name in meta and meta[res_conf.name] is None:
					del meta[res_conf.name]

			row = self._remove_metadata_fields(meta)
			data_guid = None
			if 'unique' in conf:
				data_guid = self._get_guid_by_unique_constraint(conf, conf.unique, url, row)
				if data_guid:
					if 'upsert' in conf and conf.upsert:
						self._update_db_record(conf, data_guid, url, row)
			if not data_guid:
				data_guid = self._insert_db_record(conf, url, row)

			meta['$$info_id'] = data_guid
			meta['$$info_table'] = conf.table_name

		if '$$image_urls' in meta:
			self._save_image_urls_to_db(meta['$$image_urls'], meta)

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

	def _save_file_to_ftp(self, filename, conf, data_stream):
		if not hasattr(self, 'ftp_conn'):
			self.ftp_conn = FTP(self.config.file_storage.server,
				self.config.file_storage.user,
				self.config.file_storage.password)
			if self.config.file_storage.basedir:
				self.ftp_conn.mkd(self.config.file_storage.basedir)
				self.ftp_conn.cwd(self.config.file_storage.basedir)
			self.ftp_conn.set_pasv(True)

		try:
			self.ftp_conn.storbinary('STOR ' + filename, data_stream)
		except: # in case the diretory does not exist
			try:
				self._ftp_mkdir_recursive(filename)
				self.ftp_conn.storbinary('STOR ' + filename, data_stream)
			except:
				e = sys.exc_info()
				print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
				print('    while saving file to FTP, filename: ' + filename)
				traceback.print_tb(e[2])
				return False

		return True

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

	def _save_file_record(self, response):
		self.counter.saved_images += 1
		self.report_status()

		conf = self.config.file_storage
		file_uuid = str(uuid.uuid4())
		file_dir = str(datetime.date.today().year) + '/' + str(datetime.date.today().month)
		file_ext = None
		if "Content-Type" in response.headers:
			mimetype = str(response.headers["Content-Type"])
			if mimetype in mimetypes.MimeTypes().types_map_inv:
				file_ext = mimetypes.MimeTypes().types_map_inv[mimetype][0]

		if not file_ext:
			_, file_ext = os.path.splitext(response.url)
		file_ext = file_ext.strip('.')

		if file_ext:
			filepath = file_dir + '/' + file_uuid + '.' + file_ext
		else:
			filepath = file_dir + '/' + file_uuid

		if conf.type == "ftp":
			if hasattr(response, 'body_stream'):
				if not self._save_file_to_ftp(filepath, conf, response.body_stream):
					return None
			else:
				import StringIO
				if not self._save_file_to_ftp(filepath, conf, StringIO.StringIO(response.body)):
					return None

		elif conf.type == "local":
			if hasattr(response, 'body_stream'):
				response.body = response.body_stream.read()
			self._save_file_to_local(conf, filepath, response.body)
		else:
			raise scrapy.exceptions.CloseSpider('undefined record type ' + conf.type)

		print("[" + self.name + "] Saved file " + filepath + " (URL: " + response.url + " )")
		return (filepath, response.url)

	def _parse_file_record_callback(self, response):
		record = self._save_file_record(response)
		if record is None:
			return
		filepath, _ = record

		meta = response.meta['$$meta']
		if '$$conf' in meta:
			self._save_image_urls_to_db([(filepath, response.url)], meta)

		curr_step = meta['$$step']
		if "res" in self.config.steps[curr_step]:
			res_conf = self.config.steps[curr_step].res

			meta['$$referer'] = response.url
			meta['$$filepath'] = filepath

			if type(res_conf) is not list:
				res_conf = [ res_conf ]
			results = [ (response.body, one_conf.next_step, copy.deepcopy(meta)) for one_conf in res_conf ]
			for req in self._yield_requests_from_parse_results(response.url, results):
				yield req

	def _save_image_urls_to_db(self, image_urls, response_meta):
		db_conf = response_meta['dbconf'] if 'dbconf' in response_meta else self.config.file_db_table
		for image_path_url_tuple in image_urls:
			image_path, image_url = image_path_url_tuple
			record = {}
			record[db_conf.path_field] = image_path
			record[db_conf.info_id_field] = response_meta['$$info_id']
			record[db_conf.info_table_field] = response_meta['$$info_table']
			self._insert_db_record(db_conf, image_url, record)

	def _parse_file_record(self, conf, referer, url, curr_step, meta):
		url = urljoin(referer, url)
		req = scrapy.Request(url=url, callback=self._parse_file_record_callback)
		meta['$$referer'] = referer
		meta['$$conf'] = conf
		meta['$$step'] = curr_step
		meta['$$info_id'] = meta['$$info_id'] if '$$info_id' in meta else None
		meta['$$info_table'] = meta['$$info_table'] if '$$info_table' in meta else None
		req.meta['$$meta'] = meta
		return req

	def _forge_http_response_for_intermediate(self, conf, url, result):
		response = AttrDict()
		response.url = url
		response.meta = dict()
		response.meta['$$meta'] = result[2]
		response.meta['$$step'] = result[1]
		response.meta['$$conf'] = conf
		response.meta['$$encoding'] = result[2]['$$encoding'] if '$$encoding' in result[2] else None
		response.meta['$$referer'] = result[2]['$$referer'] if '$$referer' in result[2] else None
		response.body = result[0]
		response.body_as_unicode = lambda: response.body
		return response

	def _yield_requests_from_parse_results(self, url, results):
		count = 0
		for result in results:
			# add counter to metadata
			count += 1
			result[2]['$$record_count'] = count

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
				if result:
					for req in self._http_request_callback(self._forge_http_response_for_intermediate(step_config, url, result)):
						yield req
			elif step_config.type == "file":
				yield self._parse_file_record(step_config, url, *result)
			elif step_config.type == "http":
				for req in self._build_request(result[0], result[1], result[2], url):
					yield req
			elif step_config.type == "intermediate":
				if result:
					for req in self._http_request_callback(self._forge_http_response_for_intermediate(step_config, url, result)):
						yield req
			else:
				raise scrapy.exceptions.CloseSpider('undefined step type ' + step.config.type)

	def report_status(self, force=False):
		self.__accumulative_report_counter += 1
		if not force and self.__accumulative_report_counter < self.config.status_report_batch:
			return
		if self.__accumulative_report_counter == self.config.status_report_batch:
			self.__accumulative_report_counter = 0
		try:
			urllib2.urlopen('http://127.0.0.1:8080/task/' + self.name + '/update_status', urllib.urlencode(self.counter)).read()
		except Exception as e:
			print(e)

	def _http_request_callback(self, response):
		self.counter.crawled_webpages += 1
		self.report_status()

		step_conf = self.config.steps[response.meta['$$step']]
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
			results = []

		for req in self._yield_requests_from_parse_results(response.url, results):
			yield req


	def _get_guid_by_unique_constraint(self, conf, unique, url, row):
		if "guid_field" not in conf:
			conf.guid_field = self.config.default_guid_field
		constraint_fields = [ field + ' = %s' for field in unique ]
		constraint_data = [ row[field] if field in row else '' for field in unique ]
		self.cursor.execute("SELECT " + conf.guid_field + " FROM " + conf.table_name + " WHERE " + ' AND '.join(constraint_fields), tuple(constraint_data))
		for row in self.cursor:
			return row[conf.guid_field]
		return None
		
	def _insert_url_table(self, conf, data_guid, url, action="Inserted"):
		url_row = {}
		url_row[conf.guid_field] = str(uuid.uuid4())
		url_row[self.config.url_table.id_field] = data_guid
		url_row[self.config.url_table.url_field] = url
		url_row[self.config.url_table.time_field] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.insert_row(self.config.url_table.table_name, url_row)
		print(url_row[self.config.url_table.time_field] + " [" + self.name + "] " + action + " one db record to table " + conf.table_name + " (URL: " + url + " )")

	def _update_db_record(self, conf, guid, url, row):
		if not self.__total_records_reported:
			self.counter.total_records = self.get_total_records(conf.table_name)
			self.report_status(force=True)
			self.__total_records_reported = True
		self.counter.updated_records += 1
		self.report_status()

		if "guid_field" not in conf:
			conf.guid_field = self.config.default_guid_field
		update_fields = [ field + ' = %s' for field in row ]
		update_data = [ row[field] if field in row else '' for field in row ]
		self.cursor.execute("UPDATE " + conf.table_name + " SET " + ','.join(update_fields) + " WHERE " + conf.guid_field + " = %s", tuple(update_data + [guid]))
		self._insert_url_table(conf, guid, url, action="Updated")
		return guid

	def _remove_metadata_fields(self, row):
		new_row = {}
		for k in row:
			if not k.startswith('$$'):
				new_row[k] = row[k]
		return new_row

	def _insert_db_record(self, conf, url, row):
		if not self.__total_records_reported:
			self.counter.total_records = self.get_total_records(conf.table_name)
			self.report_status(force=True)
			self.__total_records_reported = True
		self.counter.total_records += 1
		self.counter.new_records += 1
		self.report_status()

		if "guid_field" not in conf:
			conf.guid_field = self.config.default_guid_field
		# data table
		data_guid = str(uuid.uuid4())
		row[conf.guid_field] = data_guid
		self.insert_row(conf.table_name, row)
		self._insert_url_table(conf, data_guid, url, action="Inserted")
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
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			traceback.print_tb(e[2])
			print(fields)
			print(table_data)

	def insert_one_with_type(self, table_name, fields, value_types, table_data):
		self.insert_many_with_type(table_name, fields, value_types, [table_data])

	def get_total_records(self, table_name):
		try:
			self.cursor.execute('SELECT COUNT(*) as cnt FROM ' + table_name)
			for row in self.cursor:
				print('Total records in table ' + table_name + ' : ' + str(row['cnt']))
				return int(row['cnt'])
		except Exception as e:
			print(e)


def SpiderFactory(config, module_name):
	class_dict = {
		"name": module_name,
		"config": config,
		"__module__": module_name
	}
	copy_attrs = ["custom_settings", "crawlera_enabled", "crawlera_apikey"]
	for a in copy_attrs:
		if hasattr(config, a):
			class_dict[a] = getattr(config, a)
	return type('MyScrapySpider', (SpiderWrapper, ), class_dict)

