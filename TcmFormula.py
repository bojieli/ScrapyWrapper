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
	crawlera_enabled = True

	def encode_url_id(self, url_id):
		url_s = str(url_id)
		enc_s = chr(0x65 + int(url_s[0]))
		if len(url_s) >= 2:
			enc_s += chr(0x94 + int(url_s[1]))
		if len(url_s) >= 3:
			enc_s += chr(0x91 + int(url_s[2]))
		return base64.encodestring(enc_s).strip()

	def url_gen(self):
		for url_id in range(1, 2):
			yield 'http://db.yaozh.com/fangji/' + self.encode_url_id(url_id) + '.html'

	begin_urls = url_gen

	steps = {
		"begin": {
			'res': [{
				'selector_css': '.main table.table',
				'next_step': 'content'
			}]
		},
		"content": {
			'type': "db",
			'table_name': "TcmFormula",
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
				'selector': lambda text, meta: parse_ingredients(text),
				'next_step': 'ingredient'
			}
		},
		"ingredient": {
			'type': 'db',
			'table_name': 'TcmFormulaIngredient',
			'fields': [{
				'name': '$$dummy',
				'selector': lambda _,meta: remove_unknown_fields(meta)
			}, {
				'name': 'TcmFormulaID',
				'selector': lambda _,meta: meta['$$info_id']
			}, {
				'name': 'TcmName',
				'selector_regex': u'(.*)（',
				'required': True
			}, {
				'name': 'TcmContent',
				'selector_regex': u'（(.*)）',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'TcmID',
				'reference': {
					'field': 'TcmContent',
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

