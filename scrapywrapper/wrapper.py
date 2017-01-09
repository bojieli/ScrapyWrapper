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

utf8_parser = lxml.etree.HTMLParser(encoding='utf-8')

class SpiderWrapper(scrapy.Spider):
	def start_requests(self):
		self._check_config()
		self._init_db()
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
		elif type(req_conf) is list:
			for item in req_conf:
				for params in self._gen_http_params(url, item, meta):
					yield params

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
			'webview': False
		}
		for k in conf:
			if k in req_conf:
				if callable(req_conf[k]):
					conf[k] = req_conf[k](url, meta)
				else:
					conf[k] = req_conf[k]

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

	def _strip_tags(self, to_strip, text):
		if to_strip:
			convertor = html2text.HTML2Text()
			convertor.ignore_links = True
			return convertor.handle(text).strip()
		else:
			return text.strip()

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

		try:
			self._prepare_res_conf(res_conf)
			if "parser" in res_conf:
				if res_conf.parser == "js-string":
					from slimit import ast
					from slimit.parser import Parser
					from slimit.visitors import nodevisitor
					tree = Parser().parse(response_text)
					results = [ getattr(node, 'value') for node in nodevisitor.visit(tree) if isinstance(node, ast.String) ]

				elif res_conf.parser == 'js-object':
					m = re.search('var\s+[a-zA-Z0-9_$]+\s*=\s*(.*)', response_text)
					if not m:
						response_text = ""
						results = []
					else:
						response_text = m.group(1).strip(';')
						results = [ response_text ]

			if "selector_matrix" in res_conf:
				doc = lxml.html.fromstring(response_text, parser=utf8_parser)
				matrix = []
				for row in doc.xpath('//tr'):
					col_count = 0
					for col in row.xpath('.//td|.//th'):
						if len(matrix) <= col_count:
							matrix.append([])
						matrix[col_count].append(lxml.etree.tostring(col, encoding=unicode))
						col_count += 1

				try:
					if res_conf.selector_matrix['has_header']:
						matrix = matrix[1:]
				except:
					pass
				return [ ' '.join(col) for col in matrix ]

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
				obj = demjson.decode(response_text)
				levels = res_conf.selector_json.split('.')
				if type(obj) is list:
					next_objs = obj
				else:
					next_objs = [ obj ]
				for l in levels:
					if l == '':
						continue
					elif l == '*':
						next_objs = [ o.values() for o in next_objs ]
						next_objs = [ item for sublist in next_objs for item in sublist ]
					else:
						next_objs = [ o[l] for o in next_objs if l in o ]
					newlist = []
					for o in next_objs:
						if type(o) is list:
							newlist.extend(o)
						else:
							newlist.append(o)
					next_objs = newlist
				results = [ json.dumps(o) for o in next_objs ]
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
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (response ' + str(len(response_text)) + ' bytes)')
			traceback.print_tb(e[2])

		if 'required' in res_conf and res_conf['required']:
			if len(results) == 0:
				print('Record parse error: no results matching selector ' + str(res_conf))
				print('Full record: ' + response_text.encode('utf-8'))

		return results

	def _mangle_text_results(self, text_results, res_conf, meta):
		results = []
		for text_result in text_results:
			result = (text_result, res_conf.next_step, meta)
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				mangled = res_conf.data_postprocessor(text_result, meta)
				results.append((mangled, res_conf.next_step, meta))
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
		try:
			if response.meta['$$encoding']:
				body = response.body.decode(response.meta['$$encoding']).encode('utf-8')
			else:
				body = response.body_as_unicode()
		except:
			body = response.body_as_unicode()
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
				try:
					obj = demjson.decode(result)
					result = '' # default empty
					levels = res_conf.selector_json.split('.')
					next_objs = [ obj ]
					for l in levels:
						if l == '*':
							next_objs = [ o.values() for o in next_objs ]
							next_objs = [ item for sublist in next_objs for item in sublist ]
						else:
							new_objs = []
							for o in next_objs:
								if type(o) is list and len(o) > int(l):
									new_objs.append(o[int(l)])
								elif type(o) is dict and l in o:
									new_objs.append(o[l])
							next_objs = new_objs
					for o in next_objs:
						if type(o) is str or type(o) is unicode:
							result = o
							break
						elif type(o) is int or type(o) is float:
							result = str(o)
							break
						elif type(o) is bool:
							result = str(int(o))
							break
				except:
					print('selector_json failed: ' + result)
					pass
			else: # plain text
				pass

			# regex can be after other types of selectors
			if "selector_regex" in res_conf:
				m = re.search(res_conf.selector_regex, result)
				if m:
					result = m.group(1)
				else:
					result = ''

			if "selector" in res_conf and callable(res_conf.selector):
				result = res_conf.selector(result, meta)
		except:
			e = sys.exc_info()
			print('Exception type ' + str(e[0]) + ' value ' + str(e[1]))
			print('    while parsing response (' + str(len(result)) + ' bytes)')
			traceback.print_tb(e[2])

		return result.strip()

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

		if match == 'exact':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' = %s' for r in remote_fields ]), tuple(local_data))
		elif match == 'prefix':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ d + '%' for d in local_data ]))
		elif match == 'wildcard':
			self.cursor.execute('SELECT ' + remote_id_field + ' FROM ' + remote_table + ' WHERE ' + ' AND '.join([ r + ' LIKE %s' for r in remote_fields ]), tuple([ '%' + d + '%' for d in local_data]))
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
		text = text.replace(' ', '')
		m = re.search(u'^([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日$', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})$', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{2})-([0-9]{1,2})-([0-9]{1,2})$', text)
		if m:
			if int(m.group(1)) >= '70': # 1970 - 1999
				return self._make_date_string('19' + m.group(1), m.group(2), m.group(3))
			else: # >= 2000
				return self._make_date_string('20' + m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})$', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), m.group(3))
		m = re.search('^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})$', text)
		if m:
			return self._make_date_string(m.group(3), m.group(1), m.group(2))
		m = re.search('^([0-9]{1,2})/([0-9]{1,2})/([0-9]{2})$', text)
		if m:
			if int(m.group(1)) >= '70': # 1970 - 1999
				return self._make_date_string('19' + m.group(3), m.group(1), m.group(2))
			else: # >= 2000
				return self._make_date_string('20' + m.group(3), m.group(1), m.group(2))
		m = re.search(u'^([0-9]{4})年([0-9]{1,2})月$', text)
		if m:
			return self._make_date_string(m.group(1), m.group(2), 1)
		m = re.search(u'^([0-9]{4})年$', text)
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
		text = text.replace(',', '')
		try:
			m = re.search('[0-9-][0-9]*', text.replace(',', ''))
			return int(m.group(0))
		except:
			return ScrapyHelper().parse_chinese_int(text)

	def _download_images_from_html(self, response_text, meta):
		if not response_text:
			return response_text

		image_urls = []

		try:
			doc = lxml.html.fromstring(response_text, parser=utf8_parser)
		except:
			return response_text

		for m in doc.xpath('//img/@src'):
			response = AttrDict()
			response.url = urljoin(meta['$$url'], str(m))
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
				response_text = response_text.replace(str(m), filepath)

		if '$$image_urls' not in meta:
			meta['$$image_urls'] = []
		meta['$$image_urls'].extend(image_urls)
		return response_text

	def _parse_db_record(self, conf, url, result, curr_step, meta=None):
		if "preprocessor" in conf and callable(conf.preprocessor):
			(url, result, meta) = conf.preprocessor(url, result, meta)

		reference_fields = []
		# populate record with meta
		if type(meta) is not dict:
			meta = {}
		else: # copy the dict!
			meta = copy.copy(meta)
		meta['$$referer'] = url

		if "fields" not in conf:
			conf.fields = []
		for res_conf in conf.fields:
			if "reference" in res_conf:
				reference_fields.append(res_conf)
				continue
			if "data_preprocessor" in res_conf and callable(res_conf.data_preprocessor):
				result = res_conf.data_preprocessor(result, meta)
			parsed = self._parse_record_field(res_conf, result, meta)
			if "data_type" in res_conf:
				if res_conf.data_type == "Date":
					parsed = self._parse_date(parsed)
				elif res_conf.data_type == "float":
					try:
						m = re.search('[0-9.-][0-9.]*', parsed.replace(',', ''))
						parsed = str(float(m.group(0)))
					except:
						parsed = str(self._parse_int(parsed))
				elif res_conf.data_type == "int":
					parsed = str(self._parse_int(parsed))
				elif res_conf.data_type == "percentage":
					try:
						m = re.search('([0-9.-][0-9.]*)%', parsed.replace(',', ''))
						parsed = str(float(m.group(1)))
					except:
						parsed = None
			if type(parsed) is not str and type(parsed) is not unicode and parsed is not None:
				parsed = str(parsed)
			if "data_validator" in res_conf and callable(res_conf.data_validator):
				if not res_conf.data_validator(parsed, meta):
					#print('Record parse error: field ' + res_conf.name + ' failed data validator (value "' + parsed + '")')
					#print('Full record: ' + result)
					return
			if "data_postprocessor" in res_conf and callable(res_conf.data_postprocessor):
				parsed = res_conf.data_postprocessor(parsed, meta)
			if "download_images" in res_conf and res_conf.download_images:
				parsed = self._download_images_from_html(parsed, meta)
			if "required" in res_conf and res_conf.required:
				if parsed == None or len(parsed) == 0:
					print('Record parse error: required field ' + res_conf.name + ' does not exist')
					print('Full record: ' + result.encode('utf-8'))
					return
			meta[res_conf.name] = parsed

		for res_conf in reference_fields:
			status = self._parse_reference_field(res_conf, meta)
			if status == False and "required" in res_conf and res_conf.required:
				print('Record parse error: required reference field ' + res_conf.name + ' not matched (value "' + meta[res_conf.reference.field] + '")')
				print('Full record: ' + result)
				return

		if "postprocessor" in conf and callable(conf.postprocessor):
			meta = conf.postprocessor(meta)

		# remove empty fields to insert to db
		if conf.type == 'db':
			for res_conf in conf.fields:
				if res_conf.name in meta and meta[res_conf.name] is None:
					del meta[res_conf.name]
			data_guid = self._insert_db_record(conf, url, meta)
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
			results = [ (response.body, one_conf.next_step, meta) for one_conf in res_conf ]
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
		response.meta['$$encoding'] = response.meta['$$encoding'] if '$$encoding' in response.meta else None
		response.meta['$$referer'] = result[2]['$$referer'] if '$$referer' in result[2] else None
		response.body = result[0]
		response.body_as_unicode = lambda: response.body
		return response

	def _yield_requests_from_parse_results(self, url, results):
		count = 0
		for result in results:
			# add counter to metadata
			result[2]['$$record_count'] = count
			count += 1

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


	def _http_request_callback(self, response):
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


	def _insert_db_record(self, conf, url, row):
		if "guid_field" not in conf:
			conf.guid_field = self.config.default_guid_field
		# data tab;e
		data_guid = str(uuid.uuid4())
		row[conf.guid_field] = data_guid
		# remove internal metadata fields
		new_row = {}
		for k in row:
			if not k.startswith('$$'):
				new_row[k] = row[k]
		self.insert_row(conf.table_name, new_row)
		# url table
		url_row = {}
		url_row[conf.guid_field] = str(uuid.uuid4())
		url_row[self.config.url_table.id_field] = data_guid
		url_row[self.config.url_table.url_field] = url
		url_row[self.config.url_table.time_field] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.insert_row(self.config.url_table.table_name, url_row)
		print(url_row[self.config.url_table.time_field] + " [" + self.name + "] Inserted one db record to table " + conf.table_name + " (URL: " + url + " )")
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

