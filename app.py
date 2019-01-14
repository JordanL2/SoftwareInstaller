#!/usr/bin/python3

class App:

	def __init__(self, source, id, name, desc):
		self.source = source
		self.id = id
		self.name = name
		self.desc = desc

	def install(self):
		self.source.install(self)

	def remove(self):
		self.source.remove(self)

	def installed(self):
		self.source.installed(self)
