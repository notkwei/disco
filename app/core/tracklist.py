from pathlib import Path
import mutagen
from mutagen.oggvorbis import OggVorbis
import re

from app.utils import ReturnCode


class Track:

	def __init__(self, trackPath: Path, iconPath: Path):
		file = mutagen.File(trackPath)

		self.invalid: bool = False
		if file is None:
			self.invalid = True
		elif not isinstance(file, OggVorbis):
			self.invalid = True
		
		self.path: Path = trackPath
		self.icon: Path = iconPath

		self.id: str = re.sub(r"\W", "", trackPath.stem)
		
		self.length: float = file.info.length

		if file.tags.get("title") and file.tags.get("artist"):
			self.title = file.tags.get("artist")[0] + " - " + file.tags.get("title")[0]
		else:
			self.title = trackPath.stem
		



class TrackList:
	def __init__(self, tracklist: list[Track]):
		self.tracks: list[Track] = tracklist
		self.length: int = len(tracklist)
	
	def add_track(self, track: Track):
		self.tracks.append(track)