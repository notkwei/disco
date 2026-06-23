# NOTE: shutil.copy requires Python 3.8 or higher, otherwise the project runs Python 3.6.
#TODO: Implement config file/interactive settings getting
#TODO: Do error handling on copy/move operations

from enum import Enum
import json
from pathlib import Path
import questionary


from generator.utils import PackConfig, format_string
from rich import print, prompt

print(r"""	'########::'####::'######:::'######:::'#######::'########::'####::'######:::'######:::'######::
			##.... ##:. ##::'##... ##:'##... ##:'##.... ##: ##.... ##:. ##::'##... ##:'##... ##:'##... ##:
			##:::: ##:: ##:: ##:::..:: ##:::..:: ##:::: ##: ##:::: ##:: ##:: ##:::..:: ##:::..:: ##:::..::
			##:::: ##:: ##::. ######:: ##::::::: ##:::: ##: ##:::: ##:: ##::. ######:: ##:::::::. ######::
			##:::: ##:: ##:::..... ##: ##::::::: ##:::: ##: ##:::: ##:: ##:::..... ##: ##::::::::..... ##:
			##:::: ##:: ##::'##::: ##: ##::: ##: ##:::: ##: ##:::: ##:: ##::'##::: ##: ##::: ##:'##::: ##:
			########::'####:. ######::. ######::. #######:: ########::'####:. ######::. ######::. ######::
			........:::....:::......::::......::::.......:::........:::....:::......::::......::::......:::""") # ooo pretty



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



def list_audio_files(path: Path):
	audio_file_list: dict = {}
	if Path.exists(path):
		i = 1
		for item in path.iterdir():

			if item.is_file():
				if item.suffix == ".ogg":
					icon = item.with_suffix(".png")
					if icon.exists():
						icon_path = icon
					else:
						print("Could not find icon for ", item, ", using default icon.")
						icon_path = DEFAULT_ICON_PATH

					audio_file_list[item.stem] = 				{}
					audio_file_list[item.stem]["audio_path"] = 	item
					audio_file_list[item.stem]["icon_path"] = 	icon_path
					audio_file_list[item.stem]["id_string"] =  	format_string(item.stem)
					audio_file_list[item.stem]["custom_model_data"] = i
					i += 1
		
			else:
				print("Skipping non-file " + item.name)
		return audio_file_list
	else:
		raise FileNotFoundError("Invalid input path: " + str(path))




print("[bold green]Welcome to Disco![/bold green]")

choice = prompt.Prompt.ask(
    "Please select a pack format.",
    choices=["Java Resource Pack", "Java Data Pack", "Bedrock Resource Pack"],
    default="Java Resource Pack",
)

output_path = prompt.Prompt.ask("Enter a valid output path (relative).")
if not Path(output_path).exists(): print("[yellow]Could not find output path, will create it[/yellow]")

input_path = Path(prompt.Prompt.ask("Enter a valid input path (relative)."))

if not input_path.exists():
	print("[bold red]Invalid input path! Cannot continue.[/bold red]")
	exit(1)

audio_files = list_audio_files(input_path)

if not audio_files:
	print("[bold red]Could not find any audio files in", input_path.absolute(), ". Cannot continue.[/bold red]")
	exit(1)


if choice == "Java Resource Pack":
	from generator.javarp.v88_0 import *

	config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH, pack_id=pack_id,
	                                pack_description=resource_pack_description, output_path=Path(output_path),
	                                disc_item_string=music_disc_item_string)
	generate(audio_files, config)








# audio_files: dict = list_audio_files(track_input_path)
#
# if audio_files:
# 	generate_java_resource_pack(audio_files)
# else:
# 	print(f"Could not find any audio files in {track_input_path.absolute()}! Are they all in .ogg OPUS audio format?")




#assets/disco/sounds/records/discname.ogg





