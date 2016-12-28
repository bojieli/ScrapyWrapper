#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://124.254.6.83:8088/querymain.asp"]
	steps = {
		"begin": {
			'req': {
				'encoding': 'gb2312'
			},
			'res': {
				'selector_xpath': '//a/@href',
				'selector_regex': u'(show.asp\?.*)',
				'next_step': 'content',
			}
		},
		"content": {
			'req': {
				'encoding': 'gb2312'
			},
			'res': [{
				'selector_xpath': '/html/body/table/tr[2]/td/font/table',
				'keep_html_tags': True,
				'next_step': 'db'
			},
			{
				'selector_href_text': u'下一页',
				'next_step': 'content'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "TcmSeedResource",
			'fields': [
{ 'name': "TcmSeedName", 'selector_table_sibling': u"种质名称", 'required': True },
{ 'name': "TcmSeedEnglishName", 'selector_table_sibling': u"种质外文名" },
{ 'name': "PlatformResNumber", 'selector_table_sibling': u"平台资源号" },
{ 'name': "ResNumber", 'selector_table_sibling': u"资源编号" },
{ 'name': "PlantFamilyName", 'selector_table_sibling': u"科名", 'selector_regex': '（(.*)）' },
{ 'name': "PlantGenusName", 'selector_table_sibling': u"属名", 'selector_regex': '（(.*)）' },
{ 'name': "PlantFamilyEnglishName", 'selector_table_sibling': u"科名", 'selector_regex': '(.*)（.*）' },
{ 'name': "PlantGenusEnglishName", 'selector_table_sibling': u"属名", 'selector_regex': '(.*)（.*）' },
{ 'name': "TcmName", 'selector_table_sibling': u"种名", 'selector_regex': '（(.*)）' },
{ 'name': "TcmEnglishName", 'selector_table_sibling': u"种名", 'selector_regex': '(.*)（.*）' },
{ 'name': "PlaceOfOriginID", 'reference': { 'field': 'PlaceOfOrigin', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' } },
{ 'name': "PlaceOfOrigin", 'selector_table_sibling': u"原产地" },
{ 'name': "SourceLocationID", 'reference': { 'field': 'SourceLocation', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' } },
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
{ 'name': "Pedigree", 'selector_table_sibling': u"系谱" },
{ 'name': "SeedSeletionOrg", 'selector_table_sibling': u"选育单位" },
{ 'name': "SeedSeletionYear", 'selector_table_sibling': u"选育年份" },
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
{ 'name': "ChemicalFingerprintSpectrum", 'selector_table_sibling': u"化学指纹图谱" }
			],
			'res': {
				'selector_xpath': '//tr[8]/td[8]/a',
				'selector_regex': '([A-Za-z0-9-].jpg)',
				'data_postprocessor': lambda filename: 'http://124.254.6.83:8088/photo/' + filename,
				'next_step': 'image'
			}
		},
		"image": {
			'type': "file",
			'table_name': "PictureInfo",
			'guid_field': "ID",
			'path_field': "PicUrl",
			'info_id_field': "InfoID",
			'info_table_field': "InfoTable"
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

