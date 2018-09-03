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
			'Accept-Language:zh-CN,zh;q=0.9,en;q=0.8',
			'Cookie:statistics_clientid=me; ganji_uuid=8415437994638160033440; ganji_xuuid=797824bb-f08f-4828-bc26-6e234ba63bf0.1492199131148; _gl_tracker=%7B%22ca_source%22%3A%22-%22%2C%22ca_name%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_id%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22sid%22%3A5945585321%7D; GANJISESSID=9d4lngcivsndustgcik8n9e49b; gj_footprint=%5B%5B%22%5Cu79df%5Cu623f%22%2C%22http%3A%5C%2F%5C%2Fbj.ganji.com%5C%2Ffang1%5C%2F%22%5D%5D; lg=1; __utma=32156897.1741429046.1492199125.1492199125.1525369153.2; __utmc=32156897; __utmz=32156897.1525369153.2.1.utmcsr=bj.ganji.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; xxzl_deviceid=6DiWSZx5mSSzrPTbAs5oyL8fatxkXaUkyhHVXgYEcokxnXW72Nm20P1bVjtNEPcA; gj_recommend=%7B%22house%22%3A%5B%22%5Cu79df%5Cu623f%26nbsp%5Cu6574%5Cu79df%26nbsp2%5Cu5ba4%22%2C%22http%3A%5C%2F%5C%2Fbj.ganji.com%5C%2Ffang1%5C%2Fh2m1o70%5C%2F%22%5D%7D; ganji_login_act=1525369439210; __utmb=32156897.27.10.1525369153',
			'DNT:1',
			'Host:bj.ganji.com',
			'Proxy-Connection:keep-alive',
			'Upgrade-Insecure-Requests:1',
			'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
		]
		self.urlList = [
			['http://bj.ganji.com/fang1/h2m1o%s/', 100],
			['http://bj.ganji.com/fang1/choayang/h2m1o%s/', 25],
			['http://bj.ganji.com/fang1/dongcheng/h2m1o%s/', 30],
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

		pagehouseList = re.findall(r"f-list-itemershoufang-list.*?>(.*?)</dd></dl></div>", data)

		for item in pagehouseList : 
			try:
				title = re.findall(r"dd-itemtitle\">(.*?)<\/dd>", item)
				url = re.findall(r"href=\"(.*?)\"", title[0])
				url = 'http://bj.ganji.com' + url[0]
				title = re.findall(r">(.*?)<\/a>", title[0])
				title = title[0]

				if title.find('主卧') >= 0 or title.find('次卧') >= 0 or title.find('合租') >= 0:
					continue

				hType = re.findall(r"data-huxing=\"(.*?)\"", item)
				hType = hType[0]
				hSize = re.findall(r"data-area=\"(\d*)", item)
				hSize = hSize[0]

				areaZone = re.findall(r"class=\"address-eara\".*?>(.*?)<\/a>", item)
				if len(areaZone) == 3 :
					district = areaZone[0]
					area = areaZone[1].replace('租房', '')
					comm = areaZone[2]
				else :
					continue					

				price = re.findall(r"class=\"num\">(\d*?)<\/span>", item)
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
					'source': "ganji",
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
