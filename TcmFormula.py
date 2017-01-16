#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import base64
import copy

def remove_unknown_fields(meta):
	new_meta = copy.copy(meta)
	for k in new_meta:
		if not k.startswith('$$'):
			del meta[k]

def parse_ingredients(text):
	l = []
	while text != '':
		pos = text.find(u'（')
		if pos == -1:
			break
		endpos = text.find(u'）')
		if endpos == -1:
			break
		l.append(text[:endpos])
		text = text[endpos+1:]
	return l

class ScrapyConfig(ScrapyWrapperConfig):
	custom_settings = {
		'DOWNLOAD_DELAY': 1,
		'CONCURRENT_REQUESTS': 1,
	}

	def encode_url_id(self, url_id):
		url_s = str(url_id)
		enc_s = chr(0x65 + int(url_s[0]))
		if len(url_s) >= 2:
			enc_s += chr(0x94 + int(url_s[1]))
		if len(url_s) >= 3:
			enc_s += chr(0x91 + int(url_s[2]))
		return base64.encodestring(enc_s).strip()

	def url_gen(self):
		for url_id in range(300, 600):
			yield 'http://db.yaozh.com/fangji/' + self.encode_url_id(url_id) + '.html'

	begin_urls = url_gen

	steps = {
		"begin": {
			'req': {
				'cookies': 'MEIQIA_EXTRA_TRACK_ID=a6452976bc9311e6b96b02fa39e25136; gr_user_id=a1c068f7-5995-45af-87ec-a7ff262d7430; pgv_pvi=1900213552; PHPSESSID=2rquhbdd6rk3m255sjabcuulj0; _user_=2rquhbdd6rk3m255sjabcuulj0; think_language=en-US; _gat=1; ad_index_dialog=1; _ga=GA1.2.1255801030.1481121571; yaozh_logintime=1484527746; yaozh_user=424196%09bojieli; _ga=GA1.3.1255801030.1481121571; Hm_lvt_65968db3ac154c3089d7f9a4cbb98c94=1482749665,1482959253,1483892989,1484527717; Hm_lpvt_65968db3ac154c3089d7f9a4cbb98c94=1484527736',
				'dont_filter': True
			},
			'res': [{
				'selector_css': '.main table.table',
				'next_step': 'content',
				'required': True
			}, {
				'selector_regex': u'(暂无权限)',
				'data_postprocessor': lambda _,meta: meta['$$url'],
				'next_step': 'begin'
			}, {
				'selector_regex': u'(您的操作过于频繁)',
				'data_postprocessor': lambda _,meta: meta['$$url'],
				'next_step': 'begin'
			}]
		},
		"content": {
			'type': "db",
			'table_name': "TcmFormula",
			'unique': ['FormulaName'],
			'upsert': True,
			'fields': [{
				'selector_table_sibling': u'方名',	'name': "FormulaName",
				'data_validator': lambda d,_: d != u'暂无权限',
				'required': True
			}, {
				'selector_table_sibling': u'分类',	'name': 'ClassificationName'
			}, {
				'selector_table_sibling': u'出处',	'name': 'FormulaSource'
			}, {
				'selector_table_sibling': u'功用',	'name': 'MainEffect'
			}, {
				'selector_table_sibling': u'主治',	'name': 'MainFunction'
			}, {
				'selector_table_sibling': u'禁忌',	'name': 'Warnings'
			}, {
				'selector_table_sibling': u'方解',	'name': 'Fangjie'
			}, {
				'selector_table_sibling': u'化裁',	'name': 'HuaCai'
			}, {
				'selector_table_sibling': u'附方',	'name': 'AdditionalFormula'
			}, {
				'selector_table_sibling': u'附注',	'name': 'AdditionalComment'
			}, {
				'selector_table_sibling': u'文献',	'name': 'SourceDocument'
			}, {
				'selector_table_sibling': u'运用',	'name': 'ApplicationInfo'
			}],
			'res': {
				'selector_table_sibling': u'组成',
				'selector': lambda text, meta: text.split(),
				'strip_tags': True,
				'next_step': 'ingredient'
			}
		},
		"ingredient": {
			'type': 'db',
			'table_name': 'TcmFormulaIngredient',
			'unique': ['TcmFormulaID', 'TcmName'],
			'upsert': True,
			'fields': [{
				'name': '$$dummy',
				'selector': lambda _,meta: remove_unknown_fields(meta)
			}, {
				'name': 'TcmFormulaID',
				'selector': lambda _,meta: meta['$$info_id']
			}, {
				'name': 'TcmName',
				'selector': lambda t,_: t.split(u'（')[0],
				'required': True
			}, {
				'name': 'TcmContent',
				'selector_regex': u'（(.*)）',
				'data_type': 'float'
			}, {
				'name': 'TcmID',
				'reference': {
					'field': 'TcmName',
					'table': 'TB_Resources_TraditionalChineseMedicinalMaterials',
					'remote_field': 'MedicineName',
					'remote_id_field': 'ResID',
					'insert_if_not_exist': True
				},
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

