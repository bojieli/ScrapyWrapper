#?usr/bin/python
# -*- coding:utf-8 -*-
class ScrapyHelper():
	def begin_url_range(self, prefix, suffix, from_id, to_id):
		for url_id in range(from_id, to_id):
			yield prefix + str(url_id) + suffix

	def begin_url_range_encoded(self, prefix, suffix, from_id, to_id, encode_func):
		for url_id in range(from_id, to_id):
			yield prefix + encode_func(url_id) + suffix

	def load_headers_from_file(self, filename):
		header_content = ''
		with file(filename) as f:
			header_content = f.read()
		headers, cookies = self.parse_headers(header_content)

	def parse_headers(self, text):
		lines = text.split("\n")[1:]
		headers = {}
		cookie_dict = {}
		for line in lines:
			try:
				key, value = line.split(':', 1)
			except:
				continue
			key = key.strip()
			value = value.strip()
			if key == 'Cookie':
				cookies = value.split(';')
				for cookie in cookies:
					try:
						k, v = cookie.split('=', 1)
						cookie_dict[k.strip()] = v.strip()
					except:
						pass
			else:
				headers[key] = value			
		return headers, cookie_dict

