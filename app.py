#!/usr/bin/python3

class App:

	def __init__(self, source, id, name, desc, installed):
		self.source = source
		self.id = id
		self.name = name
		self.desc = desc
		self.installed = installed

	def install(self):
		self.source.install(self)

	def remove(self):
		self.source.remove(self)
