#?usr/bin/python
# -*- coding:utf-8 -*-
import json

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

	chs_arabic_map = {u'零':0, u'一':1, u'二':2, u'三':3, u'四':4,
	        u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
	        u'十':10, u'百':100, u'千':10 ** 3, u'万':10 ** 4,
	        u'〇':0, u'壹':1, u'贰':2, u'叁':3, u'肆':4,
	        u'伍':5, u'陆':6, u'柒':7, u'捌':8, u'玖':9,
	        u'拾':10, u'佰':100, u'仟':10 ** 3, u'萬':10 ** 4,
	        u'亿':10 ** 8, u'億':10 ** 8, u'幺': 1,
	        u'０':0, u'１':1, u'２':2, u'３':3, u'４':4,
	        u'５':5, u'６':6, u'７':7, u'８':8, u'９':9,
	        u'0':0, u'1':1, u'2':2, u'3':3, u'4':4,
	        u'5':5, u'6':6, u'7':7, u'8':8, u'9':9,
			u'.':'.', u'-':'-',
			u' ':' ', u'\t':' ', u',':' ' }
	
	def parse_chinese_int(self, chinese_digits):
		# skip any non-number chars
		for count in range(len(chinese_digits)):
			curr_char  = chinese_digits[count]
			curr_digit = self.chs_arabic_map.get(curr_char, None)
			if curr_digit is not None:
				break

		chinese_digits = chinese_digits[count:]
		if len(chinese_digits) == 0:
			return None

		result  = 0
		tmp     = 0
		hnd_mln = 0
		is_decimal = False
		decimal_count = 0
		minus   = 0
		for count in range(len(chinese_digits)):
			curr_char  = chinese_digits[count]
			curr_digit = self.chs_arabic_map.get(curr_char, None)
			if curr_digit == ' ':
				continue
			elif curr_digit == '-':
				minus = 1
			# meet demical point
			elif curr_digit == '.':
				is_decimal = True
				decimal_count = 0
			# meet 「亿」 or 「億」
			elif curr_digit == 10 ** 8:
				result  = result + tmp
				result  = result * curr_digit / float(10 ** decimal_count)
				is_decimal = False
				decimal_count = 0
				# get result before 「亿」 and store it into hnd_mln
				# reset `result`
				hnd_mln = hnd_mln * 10 ** 8 + result
				result  = 0
				tmp     = 0
			# meet 「万」 or 「萬」
			elif curr_digit == 10 ** 4:
				result = result + tmp
				result = result * curr_digit / float(10 ** decimal_count)
				is_decimal = False
				decimal_count = 0
				tmp    = 0
			# meet 「十」, 「百」, 「千」 or their traditional version
			elif curr_digit >= 10:
				tmp    = 1 if tmp == 0 else tmp
				result = result + curr_digit / float(10 ** decimal_count) * tmp
				is_decimal = False
				decimal_count = 0
				tmp    = 0
			# meet single digit
			elif curr_digit is not None:
				tmp = tmp * 10 + curr_digit
				if is_decimal:
					decimal_count += 1
			else:
				break
		result = result + tmp / float(10 ** decimal_count)
		result = result + hnd_mln
		if minus:
			result = -result
		return result

class AttrDict(dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self


def dict2json(d):
    s = '{'
    first = True
    for k in d:
        if not first:
            s += ','
        else:
            first = False
        s += '"' + k + '":'
        text = ''
        try:
            text = d[k].replace('\\', '\\\\').replace('"', '\\"')
        except:
            text = repr(d[k])
        s += '"' + text + '"'

    s += '}'
    return s

