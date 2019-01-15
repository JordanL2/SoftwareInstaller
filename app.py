#!/usr/bin/python3


class App:

	def __init__(self, source, id, name, desc, version, installed):
		# Reference to the source this came from
		self.source = source
		# Unique identifier within the source (does NOT contain source ID)
		self.id = id
		# Name of app
		self.name = name
		# Free-text description of app
		self.desc = desc
		# Version available in remote source
		self.version = version
		# Version installed locally, '' if not installed
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

	def status(self):
		indicator = 'N'
		if self.installed != '':
			indicator = 'I'
			if self.installed != self.version and self.version != '[Not Found]':
				indicator = 'U'
		return indicator