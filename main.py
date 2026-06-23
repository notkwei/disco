# NOTE: shutil.copy requires Python 3.8 or higher, otherwise the project runs Python 3.6.
#TODO: Implement config file/interactive settings getting
#TODO: Do error handling on copy/move operations

import shutil
from enum import Enum
import json
from pathlib import Path
import re
from generator.utils import PackConfig, format_string

DEFAULT_ICON_PATH = Path("resources/default_disc_icon.png")

class ResourcePackFormat(Enum):
	JAVA = 1
	BEDROCK = 2



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
					audio_file_list[item.stem]["id_string"] =  format_string(item.stem)
					audio_file_list[item.stem]["custom_model_data"] = i
					i += 1
		
			else:
				print("Skipping non-file " + item.name)
		return audio_file_list
	else:
		raise FileNotFoundError("Invalid input path: " + str(path))



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






audio_files: dict = list_audio_files(track_input_path)

if audio_files:
	generate_java_resource_pack(audio_files)
else:
	print(f"Could not find any audio files in {track_input_path.absolute()}! Are they all in .ogg OPUS audio format?")




#assets/disco/sounds/records/discname.ogg





