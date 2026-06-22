# NOTE: shutil.copy requires Python 3.8 or higher, otherwise the project runs Python 3.6.
#TODO: Implement config file/interactive settings getting
#TODO: Do error handling on copy/move operations

import shutil
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
track_input_path: Path = 				Path("input")
resource_pack_output_java_folder = 		Path("resource_pack")
resource_pack_output_bedrock_path = 	Path("resource_pack_bedrock")
datapack_output_path: Path =			Path("data_pack")

#Settings ()
generate_bedrock_path: bool = False
music_disc_item_string: str = "music_disc_wait"
java_resource_pack_format: float = 88.0 # Microsoft, why. Just. WHY. IT IS A VERSION NUMBER. MAKE IT A NUMBER. NOT A FLOAT.
datapack_format: float = 107.2	# *throws up*
resource_pack_description : str = "Adds music discs to the game."
pack_id : str = "discodiscs"



def generate_java_resource_pack(audio_files: dict):
	move_audio_files(audio_files) # Also creates audio-related resource pack directories. Might move that elsewhere later.

	print("[>] Writing pack.mcmeta...")
	pack_mcmeta = {"pack": {"pack_format": java_resource_pack_format,
							"description": resource_pack_description}}  # Generate pack.mcmeta
	write_dict_to_json(pack_mcmeta, resource_pack_output_java_folder / "pack.mcmeta")

	Path(resource_pack_output_java_folder / "assets" / pack_id / "models" / "item").mkdir(parents=True, exist_ok=True)
	Path(resource_pack_output_java_folder / "assets/minecraft/models/item").mkdir(parents=True, exist_ok=True)

	sounds_json = {}
	model_data_mappings = {"parent": "item/generated",
						   "textures": {
							   "layer0": f"item/{music_disc_item_string}"
						   },
						   "overrides": []
						   }

	for disc in audio_files:
		disc_id = audio_files[disc]["id_string"]
	disc_custom_model_id = int(audio_files[disc]["custom_model_data"])
	print("[*] Processing disc", disc_id)

	sounds_json["music_disc." + disc_id] = {"sounds": [{"name": pack_id + ":records/" + disc_id,
														"stream": True}]}  # formats sounds.json as music_disc.id_string = {"sounds"...
	model_data_mappings["overrides"].append({"predicate": {"custom_model_data": disc_custom_model_id},
											 "model": f"{pack_id}:item/music_disc_{disc_id}"})  # I promise at one point in time this looked nice


	item_json = {"parent": "item/generated",
				 "textures": {
					 "layer0": pack_id + ":item/" + disc_id
				 }}
	write_dict_to_json(item_json,
					   resource_pack_output_java_folder / "assets" / pack_id / "models" / "item" / f"music_disc_{disc_id}.json")

	write_dict_to_json(sounds_json, resource_pack_output_java_folder / "assets" / pack_id / "sounds.json")
	write_dict_to_json(model_data_mappings,
					   resource_pack_output_java_folder / "assets/minecraft/models/item/" / f"{music_disc_item_string}.json")


def find_track_icon(track_path: Path):
	target_icon_path: Path = track_path.parent / f"{track_path.stem}.png"

	if Path.exists(target_icon_path):
		return Path(target_icon_path)
	else:
		print("Could not find icon for " + str(track_path) + ", using default icon.")
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
					audio_file_list[item.stem]["id_string"] =  format_pack_filename_string(item.stem)
					audio_file_list[item.stem]["custom_model_data"] = i
					i += 1
		
			else:
				print("Skipping non-file " + item.name)
		return audio_file_list
	else:
		raise FileNotFoundError("Invalid input path: " + str(path))

def format_pack_filename_string(string: str):
	return re.sub(r'[^a-zA-Z]', '', str(string).translate(str.maketrans(PACK_FORMATTER_REPLACEMENTS))).lower()

def write_dict_to_json(dictionary: dict, file_path: Path):
	try:
		with open(file_path, "w", encoding='utf-8') as file:
			json.dump(dictionary, file, indent=4)

	except FileNotFoundError:
		print("[ERROR]: '" + str(file_path) + "', parent folder does not exist! Cannot continue!")
		exit(1)
	except PermissionError:
		print("[ERROR] Permission error: '" + str(file_path) + "', please make sure you have write access! Cannot continue!")
		exit(1)
	except:
		print("[ERROR] Unknown error while writing", str(file_path))
		exit(1)


def move_audio_files(files: dict):
	if resource_pack_output_java_folder.exists:
		print(f"Resource pack output folder ({str(resource_pack_output_java_folder)}) exists! To continue, the folder must be removed. Continue? (y/N) ")
		yn = str(input())
		if yn == "y":
			print("Removing Java resource pack folder...")
			shutil.rmtree(resource_pack_output_java_folder)
			resource_pack_output_java_folder.mkdir(parents=True, exist_ok=True)
		else:
			print("Cannot continue. Exiting.")
			exit(0)


	records_dir = resource_pack_output_java_folder / "assets" / pack_id / "sounds/records/"
	icons_dir = resource_pack_output_java_folder / "assets" / pack_id / "textures/item/"

	records_dir.mkdir(parents=True, exist_ok=True)
	icons_dir.mkdir(parents=True, exist_ok=True)

	for i in files:
		audio_path = files[i]["audio_path"]
		icon_path = files[i]["icon_path"]

		print("[*] Moving", audio_path.name + "...")
		shutil.move(Path(audio_path), records_dir / f"{format_pack_filename_string(audio_path.stem)}.ogg")
		if icon_path == DEFAULT_ICON_PATH:
			shutil.copy(Path(DEFAULT_ICON_PATH), icons_dir / f"{format_pack_filename_string(icon_path.stem)}.png")
		else:
			shutil.move(Path(icon_path), icons_dir / f"{format_pack_filename_string(icon_path.stem)}.png")



audio_files: dict = list_audio_files(track_input_path)

if audio_files:
	generate_java_resource_pack(audio_files)
else:
	print(f"Could not find any audio files in {track_input_path.absolute()}! Are they all in .ogg OPUS audio format?")




#assets/disco/sounds/records/discname.ogg





