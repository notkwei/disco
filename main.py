# NOTE: shutil.copy requires Python 3.8 or higher, otherwise the project runs Python 3.6.
#TODO: Implement config file/interactive settings getting
#TODO: Do error handling on copy/move operations

from enum import Enum
import json
import shutil
from pathlib import Path
import questionary
from rich.console import Console


from generator.utils import PackConfig, format_string
from rich import print, color

console = Console()
console.print("[white]" +
r"""'########::'####::'######:::'######:::'#######::'########::'####::'######:::'######:::'######::
 ##.... ##:. ##::'##... ##:'##... ##:'##.... ##: ##.... ##:. ##::'##... ##:'##... ##:'##... ##:
 ##:::: ##:: ##:: ##:::..:: ##:::..:: ##:::: ##: ##:::: ##:: ##:: ##:::..:: ##:::..:: ##:::..::
 ##:::: ##:: ##::. ######:: ##::::::: ##:::: ##: ##:::: ##:: ##::. ######:: ##:::::::. ######::
 ##:::: ##:: ##:::..... ##: ##::::::: ##:::: ##: ##:::: ##:: ##:::..... ##: ##::::::::..... ##:
 ##:::: ##:: ##::'##::: ##: ##::: ##: ##:::: ##: ##:::: ##:: ##::'##::: ##: ##::: ##:'##::: ##:
 ########::'####:. ######::. ######::. #######:: ########::'####:. ######::. ######::. ######::
........:::....:::......::::......::::.......:::........:::....:::......::::......::::......:::""" + "[/white]") # ooo pretty



DEFAULT_ICON_PATH = Path("resources/default_disc_icon.png")
DEFAULT_PACK_ICON_PATH = Path("resources/default_pack_icon.png")

class ResourcePackFormat(Enum):
	JAVA = 1
	BEDROCK = 2



#Paths for various things
DEFAULT_INPUT_PATH: Path = 				Path("input")
DEFAULT_JAVA_RP_PATH = 		Path("resource_pack")
DEFAULT_BEDROCK_RP_PATH = 	Path("resource_pack_bedrock")
DEFAULT_JAVA_DP_PATH: Path =			Path("data_pack")

DEFAULT_JAVA_RP_FORMAT: float = 88.0
DEFAULT_JAVA_DP_FORMAT: float = 107.2

DEFAULT_MUSIC_DISC_ITEM_STRING: str = "music_disc_wait"

#Settings ()
generate_bedrock_path: bool = False
java_resource_pack_format: float = 88.0 # Microsoft, why. Just. WHY. IT IS A VERSION NUMBER. MAKE IT A NUMBER. NOT A FLOAT.
datapack_format: float = 107.2	# *throws up*
resource_pack_description : str = "Adds music discs to the game."
pack_id : str = "discodiscs"


def ask_to_clear_path(path: Path = Path("")):
	consent: bool = questionary.confirm("Path exists. Continue? All contents will be permanently deleted. ").ask()
	if not consent:
		console.print("Path", path, "exists. Cannot continue.", style="bold red")
		exit(1)
	else:
		return True


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
						console.print("Could not find icon for ", item, ", using default icon.", style="gray50")
						icon_path = DEFAULT_ICON_PATH

					audio_file_list[item.stem] = 				{}
					audio_file_list[item.stem]["audio_path"] = 	item
					audio_file_list[item.stem]["icon_path"] = 	icon_path
					audio_file_list[item.stem]["id_string"] =  	format_string(item.stem)
					audio_file_list[item.stem]["custom_model_data"] = i
					i += 1
		
			else:
				console.print("Skipping non-file " + item.name)
		return audio_file_list
	else:
		raise FileNotFoundError("Invalid input path: " + str(path))

# control flow:
# action


console.print("[bold green]Welcome to Disco![/bold green]")

pack_types: list = []
while not pack_types:
	pack_types = questionary.checkbox(
		"Select pack type(s) to generate.",
		choices=["Java (Resource Pack + Datapack)", "Bedrock (Resource Pack Only, Requires Geyser + Java Datapack)"]).ask()
	if not pack_types:
		console.print("[red]Use space to select an item.[/red]")

input_path: Path = Path(questionary.path("Select input directory", "input").ask())

with console.status("Searching input directory...", spinner="dots"):
	audio_files = list_audio_files(input_path)

	if not audio_files:
		console.print("Could not find any audio files in", input_path.absolute(), ". Cannot continue.", style="bold red")
		exit(1)

use_advanced_settings = questionary.confirm("Set extended settings?", False).ask()

if use_advanced_settings:
	console.rule("[bold yellow]Extended Settings[/bold yellow]")

	advanced_settings = questionary.form(
		pack_id = questionary.text("Enter pack namespace string (lowercase letters only)", "discodiscs"),
		pack_description = questionary.text("Enter pack description", "Adds custom music discs"),
		pack_icon_path = questionary.path("Enter pack icon path"),
		disc_item_string = questionary.text("Enter disc item name to use for custom model data"),
	).ask()
else:
	advanced_settings = {"pack_id": "discodiscs",
						 "pack_description": "Adds custom music discs",
						 "pack_icon_path": DEFAULT_ICON_PATH,
						 "disc_item_string": DEFAULT_MUSIC_DISC_ITEM_STRING}

if "Java (Resource Pack + Datapack)" in pack_types:
	if use_advanced_settings:
		rp_format_id = questionary.text("Enter Java Resource Pack format number", str(DEFAULT_JAVA_RP_FORMAT)).ask()
		dp_format_id = questionary.text("Enter Datapack format number", str(DEFAULT_JAVA_DP_FORMAT)).ask()

		pack_id = format_string(advanced_settings["pack_id"]) or pack_id

	console.rule("[bold green]Java Settings[/bold green]")

	# TODO: Implement version selection for different pack versions. Skip if use_advanced_settings because we already asked the user.

	rp_output_path: Path = Path(questionary.text("Enter Java Resource Pack output directory", "resource_pack").ask())
	if rp_output_path.exists() and ask_to_clear_path(rp_output_path):
		shutil.rmtree(rp_output_path)

	dp_output_path: Path = Path(questionary.text("Enter Java Datapack output directory", "datapack").ask())
	if dp_output_path.exists() and ask_to_clear_path(dp_output_path):
		shutil.rmtree(dp_output_path)

	resource_pack_description = str(advanced_settings["pack_description"])
	music_disc_item_string = advanced_settings["disc_item_string"]
	java_resource_pack_format = float(advanced_settings["rp_format_id"])
	datapack_format = float(advanced_settings["dp_format_id"])

	pack_icon = Path(advanced_settings["pack_icon_path"])
	if not pack_icon.exists():
		console.print("Cannot find custom icon path, using default icon.", style="bold yellow")
		pack_icon = DEFAULT_PACK_ICON_PATH

	with console.status("Building selected packs...", spinner="dots"):

		rp_config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH, pack_id=pack_id,
											pack_description=resource_pack_description,
											output_path=Path(rp_output_path) or DEFAULT_JAVA_RP_PATH,
											disc_item_string=music_disc_item_string)

		dp_config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH,
										   pack_id=pack_id,
										   pack_description=resource_pack_description,
										   output_path=Path(dp_output_path) or DEFAULT_JAVA_RP_PATH,
										   disc_item_string=music_disc_item_string,
										   pack_format=datapack_format,
										   pack_icon=DEFAULT_ICON_PATH)

		from generator.javarp.v88_0 import generate_rp
		from generator.javadp.v107_1 import generate_dp

		generate_rp(audio_files, rp_config)
		generate_dp(audio_files, dp_config)

if "Bedrock (Resource Pack + Datapack)" in pack_types:
	rp_output_path: Path = Path(questionary.text("Enter Bedrock Resource Pack Output Directory", "resource_pack").ask())
