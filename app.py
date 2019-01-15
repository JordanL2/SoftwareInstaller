#!/usr/bin/python3

class App:

	def __init__(self, source, id, name, desc, version, installed):
		self.source = source
		self.id = id
		self.name = name
		self.desc = desc
		self.version = version
		self.installed = installed

	def install(self):
		self.source.install(self)

	def remove(self):
		self.source.remove(self)

	def superid(self):
		return self.source.id + ':' + self.id

	def match(self, name):
		return (name.lower() in self.name.lower()
			 or name.lower() in self.id.lower()
			 or name.lower() in self.desc.lower())
