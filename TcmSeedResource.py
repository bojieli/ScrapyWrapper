#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def is_page_higher_than_curr(url, meta):
	m = re.search('page=([0-9]*)', meta['$$url'])
	if not m:
		return True
	curr_page = int(m.group(1))
	m = re.search('page=([0-9]*)', url)
	if not m:
		return False
	next_page = int(m.group(1))
	return next_page > curr_page

def parse_TcmID(meta):
	if '$$PreferredTcmID' in meta and meta['$$PreferredTcmID']:
		meta['TcmID'] = meta['$$PreferredTcmID']
	else:
		meta['TcmID'] = meta['$$DefaultTcmID']
	return meta

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://124.254.6.83:8088/querymain.asp"]
	steps = {
        # 首页（药材分类目录页）
		"begin": {
			'req': {
				'encoding': 'gb2312'
			},
			'res': {
                # 首先找出所有链接，然后筛选出中药材类别的 URL
				'selector_xpath': '//a/@href',
				'selector_regex': u'(show.asp\?.*)',
				'next_step': 'content',
                # 由于网站使用 cookie 来保存每个中药材类别的查询结果，而采集程序是多线程的，可能同时在采集多个中药材类别，因此需要把不同中药材类别用 new_session 隔开。
				'new_session': True
			}
		},
        # 药材详情页
		"content": {
			'req': {
				'encoding': 'gb2312',
                # 由于链接相同，需要指定 dont_filter 以免 scrapy 引擎认为是重复 URL
				'dont_filter': True
			},
			'res': [{
                # 解析药材信息，入库
				'selector_xpath': '/html/body/table/tr[2]/td/font/table',
				'next_step': 'db'
			},
			{
                # 解析下一页的药材信息
				'selector_href_text': u'下一页',
                # 防止死循环，因为最后一页的“下一页”链接仍然是当前页面
				'data_validator': is_page_higher_than_curr,
				'next_step': 'content',
                # 每个网页上面有两个相同的“下一页”链接，只访问一个即可
				'limit': 1
			}]
		},
		"db": {
			'type': "db",
			'table_name': "TcmSeedResource",
			'unique': ['PlatformResNumber'],
			'upsert': True,
            # 在解析完所有 fields 之后，执行 postprocessor 后处理程序
            # 这里的目的是根据两种不同方式匹配 TcmID，如果根据名字和药典 2015 的能匹配出来，优先用药典 2015 的；不然就只根据名字匹配。
			'postprocessor': parse_TcmID,
            # 匹配数据库的各个域
			'fields': [
            # selector_table_sibling 表示获取表格中紧挨着的右边一格
{ 'name': "TcmSeedName", 'selector_table_sibling': u"种质名称", 'required': True },
{ 'name': "$$YaoDianName", 'value': u'中国药典2015年版一部' },
            # TcmName 匹配 MedicineName，$$YaoDianName 匹配 StandardSource
            # 上面把 $$YaoDianName 初始化成了“中国药典2015年版一部”
            # 这是优先 TcmID 匹配结果
{ 'name': "$$PreferredTcmID", 'reference': {'fields': ['TcmName', '$$YaoDianName'], 'table': 'TB_Resources_TraditionalChineseMedicinalMaterials', 'remote_fields': ['MedicineName', 'StandardSource'], 'remote_id_field': 'ResID' } },
            # 只根据名字匹配 TcmID
            # 如果匹配不到，插入 TB_Resources_... 表（insert_if_not_exist）
{ 'name': "$$DefaultTcmID", 'reference': {'field': 'TcmName', 'table': 'TB_Resources_TraditionalChineseMedicinalMaterials', 'remote_field': 'MedicineName', 'remote_id_field': 'ResID', 'insert_if_not_exist': True } },
{ 'name': "TcmSeedEnglishName", 'selector_table_sibling': u"种质外文名" },
{ 'name': "PlatformResNumber", 'selector_table_sibling': u"平台资源号" },
{ 'name': "ResNumber", 'selector_table_sibling': u"资源编号" },
            # 这里是匹配中文部分
{ 'name': "PlantFamilyName", 'selector_table_sibling': u"科名", 'selector_regex': u'([\u4e00-\u9fa5]+)' },
{ 'name': "PlantGenusName", 'selector_table_sibling': u"属名", 'selector_regex': u'([\u4e00-\u9fa5]+)' },
            # 这里是匹配英文部分，并去掉多余的括号
{ 'name': "PlantFamilyEnglishName", 'selector_table_sibling': u"科名", 'selector_regex': u'([^\u4e00-\u9fa5]+)', 'data_postprocessor': lambda d,_: d.strip(u'()（）') },
{ 'name': "PlantGenusEnglishName", 'selector_table_sibling': u"属名", 'selector_regex': u'([^\u4e00-\u9fa5]+)', 'data_postprocessor': lambda d,_: d.strip(u'()（）') },
{ 'name': "TcmName", 'selector_table_sibling': u"种名", 'selector_regex': u'([\u4e00-\u9fa5]+)', 'required': True },
{ 'name': "TcmEnglishName", 'selector_table_sibling': u"种名", 'selector_regex': u'([^\u4e00-\u9fa5]+)', 'data_postprocessor': lambda d,_: d.strip(u'()（）'), 'required': True },
            # 特殊的地址匹配：'match': 'address'，不需要指定关联表名（table）和关联表域（remote_field）
{ 'name': "PlaceOfOriginID", 'reference': { 'field': 'PlaceOfOrigin', 'match': 'address' } },
{ 'name': "PlaceOfOrigin", 'selector_table_sibling': u"原产地" },
{ 'name': "SourceLocationID", 'reference': { 'field': 'SourceLocation', 'match': 'address' } },
{ 'name': "SourceLocation", 'selector_table_sibling': u"来源地" },
{ 'name': "ResourceClassificationNumber", 'selector_table_sibling': u"资源归类编码" },
{ 'name': "ResourceType", 'selector_table_sibling': u"资源类型" },
{ 'name': "MainCharacteristic", 'selector_table_sibling': u"主要特性" },
{ 'name': "MainUse", 'selector_table_sibling': u"主要用途" },
{ 'name': "ClimateZone", 'selector_table_sibling': u"气候带" },
{ 'name': "GrowthHabit", 'selector_table_sibling': u"生长习性" },
{ 'name': "GrowthCycle", 'selector_table_sibling': u"生育周期" },
{ 'name': "KeyCharacteristic", 'selector_table_sibling': u"特征特性" },
{ 'name': "SeedPurpose", 'selector_table_sibling': u"具体用途" },
{ 'name': "ObserveLocation", 'selector_table_sibling': u"观测地点" },
            # 特殊的地址匹配：根据多个字段拼接起来匹配地址。这里是把 ObserveLocation 和 ConservationOrg 拼接起来匹配地址
{ 'name': "ObserveLocationID", 'reference': { 'fields': ['ObserveLocation', 'ConservationOrg'], 'match': 'address' } },
{ 'name': "Pedigree", 'selector_table_sibling': u"系谱" },
{ 'name': "SeedSeletionOrg", 'selector_table_sibling': u"选育单位" },
{ 'name': "SeedSeletionYear", 'selector_table_sibling': u"选育年份" },
            # 按照 float 类型解析
{ 'name': "Altitude", 'selector_table_sibling': u"海拔", 'data_type': 'float' },
{ 'name': "Longitude", 'selector_table_sibling': u"经度", 'data_type': 'float' },
{ 'name': "Latitude", 'selector_table_sibling': u"纬度", 'data_type': 'float' },
{ 'name': "SoilType", 'selector_table_sibling': u"土壤类型" },
{ 'name': "Ecosystemtype", 'selector_table_sibling': u"生态系统类型" },
{ 'name': "AnnualAverageTemperature", 'selector_table_sibling': u"年均温度", 'data_type': 'float' },
{ 'name': "AnnualAveragePrecipitation", 'selector_table_sibling': u"年均降雨量", 'data_type': 'float' },
{ 'name': "RecordLocation", 'selector_table_sibling': u"记录地址" },
{ 'name': "ConservationOrg", 'selector_table_sibling': u"保存单位" },
{ 'name': "OrgNumber", 'selector_table_sibling': u"单位编号" },
{ 'name': "WarehouseNumber", 'selector_table_sibling': u"库编号" },
{ 'name': "GardenNumber", 'selector_table_sibling': u"圃编号" },
{ 'name': "SeedImportNumber", 'selector_table_sibling': u"引种号" },
{ 'name': "CollectionNumber", 'selector_table_sibling': u"采集号" },
{ 'name': "ResourcePreservationType", 'selector_table_sibling': u"保存资源类型" },
{ 'name': "PreservationMethod", 'selector_table_sibling': u"保存方式" },
{ 'name': "SeedCondition", 'selector_table_sibling': u"实物状态" },
{ 'name': "ShareType", 'selector_table_sibling': u"共享方式" },
{ 'name': "AcquireMethod", 'selector_table_sibling': u"获取途径" },
{ 'name': "ContactInfo", 'selector_table_sibling': u"联系方式" },
{ 'name': "GenuineProducingArea", 'selector_table_sibling': u"道地产区" },
{ 'name': "GenuineProducingAreaID", 'reference': { 'field': 'GenuineProducingArea', 'match': 'address' } },
{ 'name': "PlantHeight", 'selector_table_sibling': u"株高" },
{ 'name': "LeafShape", 'selector_table_sibling': u"叶形" },
{ 'name': "LeafColor", 'selector_table_sibling': u"叶色" },
{ 'name': "LeafMargin", 'selector_table_sibling': u"叶缘" },
{ 'name': "LeafLength", 'selector_table_sibling': u"叶片长" },
{ 'name': "LeafWidth", 'selector_table_sibling': u"叶片宽" },
{ 'name': "FlowerColor", 'selector_table_sibling': u"花色" },
{ 'name': "FruitType", 'selector_table_sibling': u"果实类型" },
{ 'name': "FruitShape", 'selector_table_sibling': u"果实形状" },
{ 'name': "FruitColor", 'selector_table_sibling': u"果实颜色" },
{ 'name': "FruitSize", 'selector_table_sibling': u"果实大小" },
{ 'name': "FruitWeight", 'selector_table_sibling': u"单果重", 'data_type': 'float' },
{ 'name': "PersistentCalyx", 'selector_table_sibling': u"宿存萼" },
{ 'name': "BladeNumber", 'selector_table_sibling': u"叶片数", 'data_type': 'float' },
{ 'name': "TuberWeight", 'selector_table_sibling': u"块茎重", 'data_type': 'float' },
{ 'name': "StemDiameter", 'selector_table_sibling': u"茎粗", 'data_type': 'float' },
{ 'name': "Tiller", 'selector_table_sibling': u"分蘖", 'data_type': 'float' },
{ 'name': "EffectiveLing", 'selector_table_sibling': u"有效苓", 'data_type': 'float' },
{ 'name': "StemWidth", 'selector_table_sibling': u"茎宽", 'data_type': 'float' },
{ 'name': "StemLength", 'selector_table_sibling': u"茎长", 'data_type': 'float' },
{ 'name': "PrecedingCrop", 'selector_table_sibling': u"前作物" },
{ 'name': "CurrentYield", 'selector_table_sibling': u"产量", 'data_type': 'float' },
{ 'name': "SeedShape", 'selector_table_sibling': u"种子形状" },
{ 'name': "SeedColor", 'selector_table_sibling': u"种子颜色" },
{ 'name': "ThousandSeedWeight", 'selector_table_sibling': u"种子千粒重", 'data_type': 'float' },
{ 'name': "SeedWaterContent", 'selector_table_sibling': u"种子含水量", 'data_type': 'float' },
{ 'name': "SeedGerminationRate", 'selector_table_sibling': u"种子发芽率", 'data_type': 'float' },
{ 'name': "SeedGerminationPotential", 'selector_table_sibling': u"种子发芽势", 'data_type': 'float' },
{ 'name': "SowingPeriod", 'selector_table_sibling': u"播种期" },
{ 'name': "TransplantingPeriod", 'selector_table_sibling': u"移栽期" },
{ 'name': "GrowingPeriod", 'selector_table_sibling': u"生长期" },
{ 'name': "FloweringPeriod", 'selector_table_sibling': u"开花期" },
{ 'name': "FruitingPeriod", 'selector_table_sibling': u"结果期" },
{ 'name': "FullProductiveAge", 'selector_table_sibling': u"盛果期" },
{ 'name': "MaturePeriod", 'selector_table_sibling': u"成熟期" },
{ 'name': "HavestPeriod", 'selector_table_sibling': u"收获期" },
{ 'name': "SeedlingGrowthTrend", 'selector_table_sibling': u"幼苗生长势" },
{ 'name': "PlantType", 'selector_table_sibling': u"株型" },
{ 'name': "SeedlingStageDroughtTolerance", 'selector_table_sibling': u"苗期的耐旱性" },
{ 'name': "FloodTolerance", 'selector_table_sibling': u"耐涝性" },
{ 'name': "AcidBaseResistance", 'selector_table_sibling': u"耐酸碱性" },
{ 'name': "SouthernBlightResistance", 'selector_table_sibling': u"白绢病抗性" },
{ 'name': "PowderyMildewResistance", 'selector_table_sibling': u"白粉病抗性" },
{ 'name': "AnthracnoseResistance", 'selector_table_sibling': u"炭疽病抗性" },
{ 'name': "RootRotResistance", 'selector_table_sibling': u"根腐病抗性" },
{ 'name': "LeafRingRotResistance", 'selector_table_sibling': u"轮纹叶斑病抗性" },
{ 'name': "RottenLeafResistance", 'selector_table_sibling': u"烂叶病抗性" },
{ 'name': "RootKnotNematodeResistance", 'selector_table_sibling': u"根线虫病抗性" },
{ 'name': "MiteResistance", 'selector_table_sibling': u"卵形短须螨抗性" },
{ 'name': "MycinResistance", 'selector_table_sibling': u"霉素病抗性" },
{ 'name': "ScarabResistance", 'selector_table_sibling': u"金龟子抗性" },
{ 'name': "BlightResistance", 'selector_table_sibling': u"枯萎病抗性" },
{ 'name': "LeafBugResistance", 'selector_table_sibling': u"白木香卷叶虫抗性" },
{ 'name': "LongicornResistance", 'selector_table_sibling': u"天牛抗性" },
{ 'name': "TcmShape", 'selector_table_sibling': u"药材形状" },
{ 'name': "TcmColor", 'selector_table_sibling': u"药材色泽" },
{ 'name': "TcmSurface", 'selector_table_sibling': u"药材表面" },
{ 'name': "TcmTexture", 'selector_table_sibling': u"药材质地" },
{ 'name': "TcmCrossSection", 'selector_table_sibling': u"药材断面" },
{ 'name': "TcmSmell", 'selector_table_sibling': u"药材之气" },
{ 'name': "TcmTaste", 'selector_table_sibling': u"药材之味" },
{ 'name': "AshContent", 'selector_table_sibling': u"灰分" },
{ 'name': "WaterContent", 'selector_table_sibling': u"水分" },
{ 'name': "Extractum", 'selector_table_sibling': u"浸出物" },
{ 'name': "DryingRate", 'selector_table_sibling': u"折干率" },
{ 'name': "BerberineContent", 'selector_table_sibling': u"小檗碱含量" },
{ 'name': "FingerprintSpectrum", 'selector_table_sibling': u"指纹图谱" },
{ 'name': "ChemicalFingerprintSpectrum", 'selector_table_sibling': u"化学指纹图谱" },
			],
            # 存完表格主要内容后，保存链接中的图片
			'res': {
				'selector_table_sibling': u'图像',
                # 如果有多张图片，会 fork 出多个下一段
				'selector_regex': '([A-Za-z0-9-]+.jpg)',
				'data_postprocessor': lambda filename, _: 'http://124.254.6.83:8088/photo/' + filename,
				'next_step': 'image'
			}
		},
        # 保存链接中的图片（特殊处理）
        # 注意，HTML 中内嵌或链接的图片，一般在 fields 解析中用 strip_tags: False 就能处理。这里是特殊情况，因为图片链接是 JavaScript 生成的。
		"image": {
			'type': "file",
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

