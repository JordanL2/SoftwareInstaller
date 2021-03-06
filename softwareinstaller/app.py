#!/usr/bin/python3


class App:

	statuses = ('N', 'I', 'U')

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

	def copy(self):
		return App(self.source, self.id, self.name, self.desc, self.version, self.installed)

	def install(self):
		self.source.install(self)

	def remove(self):
		self.source.remove(self)

	def match(self, terms):
		for term in terms:
			if not (term.lower() in self.name.lower() or term.lower() in self.id.lower() or term.lower() in self.desc.lower()):
				return False
		return True

	def status(self):
		indicator = 'N'
		if self.installed is not None:
			indicator = 'I'
			if self.installed != self.version and self.version is not None:
				indicator = 'U'
		return indicator

	def isinstalled(self):
		return (self.installed is not None);
