#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import getpass
import os

class DataBase :

	def __init__ (self) :
		user = getpass.getuser()
		self.dbAddress = "/var/www/data/"

		self.table = 'house'

		if self.connect() == False:
			self.connStat = False
		else :
			self.connStat = True
			self.chkTable()

	def __del__ (self) :
		if self.connStat == True :
			self.disConn()	

	def connect (self) :
		try:
			if not os.path.exists(self.dbAddress) :
				os.makedirs(self.dbAddress)
			self.dbAddress += 'HouseData.db'
			self.conn = sqlite3.connect(self.dbAddress)
			self.cur = self.conn.cursor()
			return True
		except Exception, e:
			return False

	def create (self) :
		if self.connStat == False : return False

		sql = 'create table ' + self.table + ' (id integer PRIMARY KEY autoincrement, title text, url text, hType text, hSize text, district text, area text, comm text, price integer, agent text, source text, addtime text)'
		self.cur.execute(sql)

		self.createViews()


	def createViews (self) :
		views = [
			"CREATE VIEW \"2k~3.5k 可以住哪里\" AS select count(*) as `租房数`, district as `城区`, area as `街道`, comm as `社区`, round(avg(price)) as `均价`, max(price) as `最高价` from housewhere `城区` not in('顺义','昌平','大兴','通州','房山','平谷','怀柔')GROUP BY `社区` HAVING `均价` >= 2000 and `均价` <= 3500 and `租房数` >= 10ORDER BY `均价` asc;",
			"CREATE VIEW \"石景山居民区分布\" AS select count(*) as `租房数`, comm as `小区`, round(avg(price)) as `均价`, max(price) as `最高价` from house where district = '石景山' GROUP BY `小区` HAVING `租房数` > 10ORDER BY `均价` asc;",
			"CREATE VIEW \"石景山街道分布\" AS select count(*) as `租房数`, area as `街道`, round(avg(price)) as `均价`, max(price) as `最高价` from house where district = '石景山' GROUP BY `街道` ORDER BY `均价` asc;",
		]

		for sql in views:
			self.cur.execute(sql)


	def query (self, sql) :
		if self.connStat == False : return False

		self.cur.execute(sql)
		values = self.cur.fetchall()

		return values

	def getLast (self) :
		if self.connStat == False : return False

		sql = "SELECT * FROM " + self.table + " ORDER BY id DESC LIMIT 1"
		self.cur.execute(sql)
		values = self.cur.fetchone()
		if values == None :
			values = []
		return values

	def insert (self, data):
		if self.connStat == False : return False

		import sys
		reload(sys)
		sys.setdefaultencoding('utf-8')

		keyList = []
		valList = []
		for k, v in data.iteritems():
			keyList.append(k)
			valList.append(str(v).replace('"','\"').replace("'","''"))

		sql = "insert into " + self.table + " (`" + '`, `'.join(keyList) + "`) values ('" + "', '".join(valList) + "')"
		self.cur.execute(sql)
		self.conn.commit()

	def disConn (self) :
		if self.connStat == False : return False

		self.cur.close()
		self.conn.close()

	def chkTable (self) :
		if self.connStat == False : return False

		sql = "SELECT tbl_name FROM sqlite_master WHERE type='table'"
		tableStat = False

		self.cur.execute(sql)
		values = self.cur.fetchall()

		for x in values:
			if self.table in x :
				tableStat = True

		if tableStat == False :
			self.create()


