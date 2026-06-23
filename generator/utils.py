import json
from pathlib import Path
from dataclasses import dataclass
import shutil
import re


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
	default_icon: Path

	pack_id: str
	pack_description: str
	output_path: Path
	disc_item_string: str

def format_string(string: str):
	return re.sub(r'[^a-zA-Z]', '', str(string).translate(str.maketrans(STRING_FORMATTER_REPLACEMENTS))).lower()

def move_audio(files: dict, config: PackConfig):
	if config.output_path.exists:
		print(f"Resource pack output path ({str(config.output_path)}) exists! To continue, the path must be removed. Continue? (y/N) ")
		yn = str(input())
		if yn == "y":
			print("Removing Java resource pack path...")
			shutil.rmtree(config.output_path)
			config.output_path.mkdir(parents=True, exist_ok=True)
		else:
			print("Cannot continue. Exiting.")
			exit(0)


	records_dir = config.output_path / "assets" / config.pack_id / "sounds/records/"
	icons_dir = config.output_path / "assets" / config.pack_id / "textures/item/"

	records_dir.mkdir(parents=True, exist_ok=True)
	icons_dir.mkdir(parents=True, exist_ok=True)

	for i in files:
		audio_path = files[i]["audio_path"]
		icon_path = files[i]["icon_path"]

		print("[*] Moving", audio_path.name + "...")
		shutil.move(Path(audio_path), records_dir / f"{format_string(audio_path.stem)}.ogg")
		if icon_path == config.default_icon:
			shutil.copy(Path(config.default_icon), icons_dir / f"{format_string(icon_path.stem)}.png")
		else:
			shutil.move(Path(icon_path), icons_dir / f"{format_string(icon_path.stem)}.png")

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