from enum import Enum
import json
from pathlib import Path
import re

DEFAULT_ICON_PATH = Path("resources/default_disc_icon.png")

class ResourcePackFormat(Enum):
	JAVA = 1
	BEDROCK = 2

PACK_FORMATTER_REPLACEMENTS = {
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

#Paths for various things
track_input_path: Path = 					Path("input")
resource_pack_output_java_folder: Path = 		"resource_pack"
resource_pack_output_bedrock_path: Path = 	"resource_pack_bedrock"
datapack_output_path: Path = 				Path("data_pack")

#Settings (TODO: Implement config file/interactive settings getting)
generate_bedrock_path: bool = False
java_resource_pack_format: float = 88.0
datapack_format: float = 107.2
resource_pack_description : str = "Adds music discs to the game."
pack_id : str = "discodiscs"

def find_track_icon(trackPath: Path):
	target_icon_path: str = str(trackPath.parent) + '/' + trackPath.stem + ".png"

	if Path.exists(Path(target_icon_path)):
		return Path(target_icon_path)
	else:
		print("Could not find icon for " + trackPath + ", using default icon.")
		return DEFAULT_ICON_PATH

def list_audio_files(path: Path):
	audio_file_list: dict = {}
	if Path.exists(path):
		i = 1
		for item in path.iterdir():

			if item.is_file():
				if item.suffix == ".ogg":
					audio_file_list[item.stem] = 				{}
					audio_file_list[item.stem]["audio_path"] = 	item
					audio_file_list[item.stem]["icon_path"] = 	find_track_icon(item)
					audio_file_list[item.stem]["custom_model_data"] = i
					i += 1
		
			else:
				print("Skipping non-file " + item.name)
		return audio_file_list
	else:
		raise FileNotFoundError("Invalid input path: " + path)

def format_pack_filename_string(string: str):
	return re.sub(r'[^a-zA-Z]', '', str(string).translate(str.maketrans(PACK_FORMATTER_REPLACEMENTS))).lower()

def write_dict_to_json(dictionary: dict, file_path: Path):
	file = Path(file_path).open(mode="w", encoding='utf-8')
	json.dump(dictionary, file)




print("Hello, World!")

pack_mcmeta = {} # Generate pack.mcmeta
pack_mcmeta["pack"] = {"pack_format": java_resource_pack_format, "description": resource_pack_description}
write_dict_to_json(pack_mcmeta, Path("pack.mcmeta"))



audio_files: dict = list_audio_files(track_input_path)

#assets/disco/sounds/records/discname.ogg

records_dir = resource_pack_output_java_folder + "/assets/" + pack_id + "/sounds/records/"
icons_dir = resource_pack_output_java_folder + "/assets/" + pack_id + "/textures/item/"

Path(records_dir).mkdir(parents=True, exist_ok=True)
Path(icons_dir).mkdir(parents=True, exist_ok=True)

for i in audio_files:

	audio_path = audio_files[i]["audio_path"]
	icon_path = audio_files[i]["icon_path"]

	print("[*] Working on", audio_path.name + "...")
	Path(audio_path).rename(Path(records_dir + "/" + format_pack_filename_string(audio_path.stem) + ".ogg"))
	Path(icon_path).rename(Path(icons_dir + "/" + format_pack_filename_string(icon_path.stem) + ".png"))
