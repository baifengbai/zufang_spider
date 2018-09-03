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
			'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding:gzip, deflate',
			'Accept-Language:zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Cache-Control:no-cache',
			'Cookie:city=www; indexAdvLunbo=lb_ad2%2C0%7Clb_ad5%2C0; __utma=147393320.1057305881.1525413316.1525413316.1525413316.1; __utmc=147393320; __utmz=147393320.1525413316.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt_t0=1; __utmt_t1=1; __utmt_t2=1; global_cookie=ty97uht10qouu40ht8azaicik1sjgrjpbg3; integratecover=1; SoufunSessionID_Rent=1_1525413336_884; __utmt_tremove=1; ASP.NET_SessionId=quiwzagjuno5wdnifkpinckn; polling_imei=9461d04029b81f48; keyWord_recenthousebj=%5b%7b%22name%22%3a%22%e7%9f%b3%e6%99%af%e5%b1%b1%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a07%2f%22%2c%22sort%22%3a1%7d%5d; Rent_StatLog=ff4d7de5-6a6d-40b9-8524-845fbef76daf; Captcha=394E30774C2B5A4373753735684C4C7548554267624775744A67415068564D79594E6A6E6F464979636864752B594D2F766D4747396165414D666C383531416138485174516D36517179633D; __utmb=147393320.33.10.1525413316; unique_cookie=U_ty97uht10qouu40ht8azaicik1sjgrjpbg3*8',
			'DNT:1',
			'Host:zu.fang.com',
			'Pragma:no-cache',
			'Proxy-Connection:keep-alive',
			'Referer:http://zu.fang.com/house-a07/g22-i326-n31/',
			'Upgrade-Insecure-Requests:1',
			'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
		]
		self.urlList = [
			['http://zu.fang.com/house/g22-i3%s-n31/', 100],
			['http://zu.fang.com/house-a01/g22-i3%s-n31/', 25],
			['http://zu.fang.com/house-a02/g22-i3%s-n31/', 25],
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

		pagehouseList = re.findall(r"listhiddenMaprel.*?>(.*?)</dd></dl>", data)

		for item in pagehouseList : 
			try:
				item = item.decode('gbk')
				title = re.findall(r"<pclass=\"title\".*?>(.*?)<\/p>", item)
				url = re.findall(r"href=\"(.*?)\"", title[0])
				url = 'http://zu.fang.com' + url[0]
				title = re.findall(r">(.*?)<\/a>", title[0])
				title = title[0]

				if title.find('主卧') >= 0 or title.find('次卧') >= 0 or title.find('合租') >= 0:
					continue

				sizeZone = re.findall(r"class=\"font16mt20bold\">(.*?)<\/p>", item)
				sizeList = sizeZone[0].split('<spanclass="splitline">|</span>')
				hType = sizeList[1]
				hSize = re.findall(r"(\d*)", sizeList[2])
				hSize = hSize[0]

				areaZone = re.findall(r"class=\"gray6mt20\".*?>(.*?)<\/p>", item)
				areaZone = re.findall(r"<span>(.*?)<\/span>", areaZone[0])

				if len(areaZone) == 3 :
					district = areaZone[0]
					area = areaZone[1]
					comm = areaZone[2]
				else :
					continue

				price = re.findall(r"<spanclass=\"price\">(\d*?)<\/span>", item)
				price = price[0]

				house = {
					'url': url,
					'title': title,
					'hType': hType,
					'hSize': hSize,
					'district': district,
					'area': area,
					'comm': comm,
					'price': price,
					'agent': '',
					'source': "soufang",
					'addtime': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
				}

				result.append(house)
			except Exception as e:
				pass

		return result

	def addData (self, data):
		for x in data:
			sql = "select * from house where agent = '" + x['agent'] + "' and title = '" + x['title'] + "' and hType = '" + x['hType'] + "' and hSize = '" + x['hSize'] + "' and comm = '" + x['comm'] + "' and price = '" + x['price'] + "'"
			result = self.DB.query(sql)
			if len(result) == 0 :
				self.DB.insert(x)
