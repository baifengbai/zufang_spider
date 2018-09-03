#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import time
import re
import StringIO
import gzip

reload(sys)  
sys.setdefaultencoding('utf8')

from Libs import Tools
from Libs import DB

class Spider :
	def __init__ (self) :
		self.T = Tools.Tools()
		self.DB = DB.DataBase()
		self.page = 1
		self.req = [
			'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding: gzip, deflate',
			'Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Cache-Control: no-cache',
			'Cookie: f=n; f=n; id58=c5/ns1i5D3mJ2bxpAyNlAg==; bj58_id58s="UytJdWxGdjItcFdTOTU3Nw=="; bdshare_firstime=1488523485383; _ga=GA1.2.560673662.1488523272; __utma=253535702.560673662.1488523272.1488523272.1491991488.2; 58home=bj; f=n; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; wmda_uuid=580e07bda17336625620458f5a24143b; wmda_new_uuid=1; wmda_session_id_2385390625025=1525335851458-b2ef1443-7b63-41fd; wmda_visited_projects=%3B2385390625025; commontopbar_ipcity=bj%7C%E5%8C%97%E4%BA%AC%7C0; 58tj_uuid=aa163157-47f7-44bc-971c-be9264682af5; new_uv=1; utm_source=; spm=; init_refer=; commontopbar_myfeet_tooltip=end; als=0; new_session=0',
			'DNT: 1',
			'Host: bj.58.com',
			'Pragma: no-cache',
			'Proxy-Connection: keep-alive',
			'Referer: http://bj.58.com/zufang/b12j2/pn3/?PGTID=0d300008-0000-17a5-d6a3-0a80cb231464&ClickID=1',
			'Upgrade-Insecure-Requests: 1',
			'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
		]
		self.urlList = [
			['http://bj.58.com/zufang/j2/pn%s/?PGTID=0d300008-0000-1168-a81f-698e30286ec1&ClickID=2', 70],
			['http://bj.58.com/chaoyang/zufang/j2/pn%s/?PGTID=0d300008-0047-971d-977c-bbffb2636640&ClickID=2', 70],
			['http://bj.58.com/dongcheng/zufang/j2/pn%s/?PGTID=0d300008-0047-971d-977c-bbffb2636640&ClickID=2', 70],
		]

	def getData (self) :
		for url in self.urlList :
			self.page = 1
			while self.page <= url[1] :
				target = url[0] % (self.page)
				# print "Fetching : " + target
				try:
					pageInfo = self.T.getPage(target, self.req)
					html = self.T.gzdecode(pageInfo['body'])
					houseList = self.formateData(html)

					self.addData(houseList)
				except Exception as e:
					pass

				self.page += 1
				time.sleep(5)

	def formateData (self, data) :
		result = []
		data = re.sub(r"\s", "", data)
		pageHouseZone = re.findall(r"class=\"listUl\">(.*?)<\/ul>", data)

		pageHouseZone = pageHouseZone[0]

		pagehouseList = re.findall(r"<li.*?>(.*?)<\/li>", pageHouseZone)

		for item in pagehouseList : 
			try:
				title = re.findall(r"<h2>(.*?)<\/h2>", item)
				url = re.findall(r"href=\"(.*?)\"", title[0])
				url = url[0]
				title = re.findall(r">(.*?)<\/a>", title[0])
				title = title[0]

				if title.find('主卧') >= 0 or title.find('次卧') >= 0 or title.find('合租') >= 0:
					continue

				size = re.findall(r"class=\"room\">(.*?)<\/p>", item)
				temp = size[0].split('&nbsp;&nbsp;&nbsp;&nbsp;')
				hType = temp[0]
				hSize = re.findall(r"(\d*)", temp[1])
				hSize = hSize[0]

				areaZone = re.findall(r"class=\"add\">(.*?)<\/p>", item)
				areaZone = re.findall(r"<a.*?>(.*?)<\/a>", areaZone[0])
				area = areaZone[0]
				comm = areaZone[1]

				district = self.getDist(area)

				if district == 'None' :
					district = area

				price = re.findall(r"<b>(\d*?)<\/b>", item)
				price = price[0]

				agentCom = re.findall(r"class=\"jjr_par_dp\">(.*?)<\/span>", item)
				agent = re.findall(r"class=\"listjjr\">(.*?)<\/span>", item)
				agent =  agentCom[0] + ' - ' + agent[0]

				house = {
					'url': url,
					'title': title,
					'hType': hType,
					'hSize': hSize,
					'district': district,
					'area': area,
					'comm': comm,
					'price': price,
					'agent': agent,
					'source': "58",
					'addtime': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
				}

				result.append(house)			
			except Exception as e:
				pass

		return result

	def getDist (self, area) :
		distList = {
			'朝阳': ['安慧桥','安贞','奥林匹克公园','百子湾','八里庄','北沙滩','北苑','CBD','常营','朝青板块','朝外大街','朝阳公园','朝阳周边','慈云寺','大山子','大屯','大望路','定福庄','东坝','东大桥','豆各庄','垡头','甘露园','高碑店','工体','广渠门','管庄','国贸','国展','和平街','红庙','花家地','欢乐谷','华威桥','惠新里','惠新西街','呼家楼','将台路','建外大街','健翔桥','京广桥','劲松','酒仙桥','来广营','柳芳','麦子店','媒体村','南磨房','南沙滩','农业展览馆','潘家园','三里屯','三元桥','芍药居','胜古','十八里店','石佛营','十里堡','十里河','首都机场','双井','双桥','水碓子','四惠','松榆里','孙河','太阳宫','甜水园','团结湖','望京','小关','小红门','西坝河','燕莎','姚家园','亚运村','亚运村小营','左家庄'],
			'海淀': ['安宁庄','白石桥','北航','北京大学','北太平庄','北洼路','厂洼','车道沟','大钟寺','定慧寺','恩济里','二里庄','甘家口','公主坟','海淀周边','航天桥','花园桥','交通大学','蓟门桥','金沟河','军博','联想桥','马连洼','明光桥','牡丹园','清河','清华大学','人民大学','上地','上庄','世纪城','双榆树','四季青','苏州街','苏州桥','田村','万柳','万泉河','万寿路','万寿寺','魏公村','温泉','五彩城','五道口','五棵松','五路居','香山','肖家河','小西天','西八里庄','西北旺','西二旗','西三旗','西山','西苑','学院路','学院路北','永定路','玉泉路','皂君庙','增光路','知春路','中关村','紫竹桥'],
			'东城': ['安定门','北京站','北新桥','朝阳门','灯市口','东城周边','东单','东四','东四十条','东直门','东直门外','海运仓','和平里','建国门','交道口','景山','沙滩','王府井','雍和宫'],
			'西城': ['百万庄','车公庄','德胜门','地安门','阜成门','复兴门','广安门外','官园','鼓楼','金融街','积水潭','六铺炕','马甸','木樨地','南礼士路','三里河','什刹海','小西天','西便门','西城周边','西单','新街口','西四','西直门','月坛','展览路','真武庙'],
			'崇文': ['崇文门','崇文周边','磁器口','东花市','法华寺','光明楼','广渠门','龙潭湖','前门','天坛','体育馆路','新世界','永定门'],
			'宣武': ['白广路','白纸坊','菜市口','长椿街','椿树街道','大观园','大栅栏','广安门内','和平门','红莲','虎坊桥','马连道','南菜园','牛街','陶然亭','天宁寺','天桥','宣武门','宣武周边','珠市口'],
			'丰台': ['北大地','菜户营','草桥','长辛店','成寿寺','大红门','东大街','东高地','东铁匠营','方庄','丰台路','丰台体育馆','丰台周边','丰益桥','和义','花乡','角门','嘉园','看丹桥','科技园区','莲花池','刘家窑','六里桥','丽泽桥','卢沟桥','马家堡','木樨园','南苑','蒲黄榆','七里庄','青塔','世界公园','石榴庄','宋家庄','太平桥','五里店','小屯路','西客站','西罗园','新发地','新宫','洋桥','右安门','岳各庄','云岗','玉泉营','赵公口','总部基地','左安门'],
			'通州': ['八里桥','八通轻轨沿线','北关','北关环岛','次渠','东关','果园','九棵树','临河里','梨园','潞城','马驹桥','乔庄','宋庄','通州北苑','通州周边','土桥','武夷花园','物资学院路','漷县','西门','新华大街','永乐店','永顺','运河大街','玉桥','张家湾','中仓'],
			'石景山': ['八宝山','八大处','八角','广宁','古城','金顶街','老山','鲁谷','模式口','苹果园','石景山周边','五里坨','西山','衙门口','杨庄','永乐','玉泉路'],
			'房山': ['长阳','窦店','房山城关','房山周边','韩村河','良乡','琉璃河','阎村','燕山','迎风','周口店'],
			'昌平': ['百善','北七家','昌平县城','昌平周边','城北','城南','东小口','回龙观','霍营','立水桥','龙泽','南口','南邵镇','沙河','天通苑','小汤山','阳坊'],
			'大兴': ['滨河','大兴周边','高米店','观音寺','海子角','河西区','黄村','旧宫','林校路','庞各庄','清源','生物医药基地','同兴园','西红门','兴丰大街','兴华大街','兴业大街','瀛海镇','亦庄','亦庄东区','亦庄西区','郁花园','枣园'],
			'顺义': ['东方太阳城','光明','后沙峪','建新','机场','李桥','马坡','南彩','胜利','石门','石园','顺义城区','顺义周边','天竺','新国展','杨镇','裕龙','中央别墅区'],
			'密云': ['密云城区','不老屯','溪翁庄','密云周边'],
			'怀柔': ['雁栖','桥梓','怀柔城区','渤海镇','庙城','怀柔周边'],
			'延庆': ['延庆城区','大榆树','八达岭','康庄','延庆周边'],
			'平谷': ['金海湖','滨河路','平谷城区','兴谷','渔阳','王辛庄','平谷周边'],
			'门头沟': ['大峪','东辛房','龙泉','城子街道','永定','潭柘寺','军庄','门头沟周边'],
			'燕郊': ['燕顺路','迎宾路','东市区','城区','潮白河','大厂'],
			'北京周边': ['霸州','大厂','固安','涞水','廊坊','其他','三河','香河','永清','涿州'],
		}

		for k, v in distList.iteritems() :
			if area in v :
				return k

	def addData (self, data):
		for x in data:
			sql = "select * from house where agent = '" + x['agent'] + "' and title = '" + x['title'] + "' and hType = '" + x['hType'] + "' and hSize = '" + x['hSize'] + "' and comm = '" + x['comm'] + "' and price = '" + x['price'] + "'"
			result = self.DB.query(sql)
			if len(result) == 0 :
				self.DB.insert(x)
