#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import time
import re

reload(sys)  
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Components import Site58
from Components import Siteganji
from Components import Sitesoufang

class App :

	def __init__ (self) :
		self.Site58 = Site58.Spider()
		self.Siteganji = Siteganji.Spider()
		self.Sitesoufang = Sitesoufang.Spider()

	def run (self) :
		# print "Mission Start !"

		self.Site58.getData()
		self.Siteganji.getData()
		self.Sitesoufang.getData()

		# print "Done Well !"

App = App()
App.run()
