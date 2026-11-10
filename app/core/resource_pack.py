from enum import Enum

import app.core.tracklist

class ResourcePackVersion(Enum):
	V34 = 1
	V88_0 = 2




class ResourcePack:
	
	def __init__(self, tracklist, version: ResourcePackVersion):
		self.version = version
		self.tracklist = tracklist


