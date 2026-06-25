import json
from pathlib import Path
from dataclasses import dataclass
import shutil
import re
from rich.console import Console


console = Console()


STRING_FORMATTER_REPLACEMENTS = {
	"1": "one",
	"2": "two",
	"3": "three",
	"4": "four",
	"5": "five",
	"6": "six",
	"7": "seven",
	"8": "eight",
	"9": "nine",
	"0": "zero"
}


@dataclass
class PackConfig:
	pack_icon: Path
	default_icon: Path

	pack_format: float

	pack_id: str
	pack_description: str
	output_path: Path
	disc_item_string: str
	jukebox_comparator_output: int
	audio_range: float

def format_string(string: str):
	return re.sub(r'[^a-zA-Z]', '', str(string).translate(str.maketrans(STRING_FORMATTER_REPLACEMENTS))).lower()

def move_audio(files: dict, config: PackConfig, audio_output_path: Path, icon_output_path: Path):
	for i in files:
		audio_path = files[i]["audio_path"]
		icon_path = files[i]["icon_path"]

		console.print("[*] Copying", audio_path.name + "...")
		shutil.copy(Path(audio_path), audio_output_path / f"{format_string(audio_path.stem)}.ogg")
		if icon_path == config.default_icon:
			shutil.copy(Path(config.default_icon), icon_output_path / f"{format_string(icon_path.stem)}.png")
		else:
			shutil.copy(Path(icon_path), icon_output_path / f"{format_string(icon_path.stem)}.png")

def write_json(dictionary: dict, file_path: Path):
	try:
		with open(file_path, "w", encoding='utf-8') as file:
			json.dump(dictionary, file, indent=4)

	except FileNotFoundError:
		print("[ERROR]: '" + str(file_path) + "', parent path does not exist! Cannot continue!")
		exit(1)
	except PermissionError:
		print("[ERROR] Permission error: '" + str(file_path) + "', please make sure you have write access! Cannot continue!")
		exit(1)