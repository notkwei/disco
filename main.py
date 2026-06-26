# NOTE: shutil.copy requires Python 3.8 or higher, otherwise the project runs Python 3.6
from enum import Enum
import shutil
from pathlib import Path

try:
	import questionary
except ModuleNotFoundError:
	print("[ERROR] Questionary is required to run this program! Please install it with 'python -m pip install questionary' and try again.")
	exit(1)

try:
	from rich.console import Console
except ModuleNotFoundError:
	print("[ERROR] Rich is required to run this program! Please install it with 'python -m pip install rich' and try again.")
	exit(1)

try:
	import mutagen
except ModuleNotFoundError:
	print("[ERROR] Mutagen is required to run this program! Please install it with 'python -m pip install mutagen' and try again.")
	exit(1)

from generator.utils import PackConfig, format_string

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

DEFAULT_PACK_ID: str = "discodiscs"
DEFAULT_PACK_NAME: str = "Custom Music Disc Pack - Powered by Disco"
DEFAULT_PACK_DESCRIPTION: str = "Adds custom music discs"

DEFAULT_INPUT_PATH: Path = 				Path("input")
DEFAULT_JAVA_RP_PATH = 		Path("resource_pack")
DEFAULT_BEDROCK_RP_PATH = 	Path("resource_pack_bedrock")
DEFAULT_JAVA_DP_PATH: Path =			Path("data_pack")

DEFAULT_JAVA_RP_FORMAT: float = 88.0
DEFAULT_JAVA_DP_FORMAT: float = 107.2

DEFAULT_MUSIC_DISC_ITEM_STRING: str = "music_disc_wait"
DEFAULT_JUKEBOX_COMPARATOR_OUTPUT: int = 12
DEFAULT_AUDIO_RANGE: float = 64.0

#Settings ()
generate_bedrock_path: bool = False
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

					file = mutagen.File(item)
					if file is None:
						console.print("[ERROR] Could not read file", item, "! Cannot continue!", style="bold red")
						exit(1)

					icon = item.with_suffix(".png")
					if icon.exists():
						icon_path = icon
					else:
						console.print("Could not find icon for ", item, ", using default icon.", style="gray50")
						icon_path = DEFAULT_ICON_PATH

					if file.tags.get("title") and file.tags.get("artist"):
						track_description: str = file.tags.get("artist")[0] + " - " + file.tags.get("title")[0]
					else:
						track_description: str = item.stem

					audio_file_list[item.stem] = 				{}
					audio_file_list[item.stem]["audio_path"] = 	item
					audio_file_list[item.stem]["icon_path"] = 	icon_path
					audio_file_list[item.stem]["id_string"] =  	format_string(item.stem)
					audio_file_list[item.stem]["length"] = file.info.length
					audio_file_list[item.stem]["description"] = track_description
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
		pack_name = questionary.text("Enter pack name"),
		pack_description = questionary.text("Enter pack description", "Adds custom music discs"),
		pack_icon_path = questionary.path("Enter pack icon path"),
		disc_item_string = questionary.text("Enter disc item name to use for custom model data"),
		jukebox_comparator_output = questionary.text("Enter the jukebox redstone comparator output for the discs"),
		audio_range = questionary.text("Enter the audio range for the discs")
	).ask()
else:
	advanced_settings = {"pack_id": DEFAULT_PACK_ID,
						 "pack_description": DEFAULT_PACK_DESCRIPTION,
						 "pack_name": DEFAULT_PACK_NAME,
						 "pack_icon_path": DEFAULT_ICON_PATH,
						 "disc_item_string": DEFAULT_MUSIC_DISC_ITEM_STRING,
						 "jukebox_comparator_output": DEFAULT_JUKEBOX_COMPARATOR_OUTPUT,
						 "audio_range": DEFAULT_AUDIO_RANGE}

if "Java (Resource Pack + Datapack)" in pack_types:
	if use_advanced_settings:
		rp_format_id = questionary.text("Enter Java Resource Pack format number", str(DEFAULT_JAVA_RP_FORMAT)).ask()
		dp_format_id = questionary.text("Enter Datapack format number", str(DEFAULT_JAVA_DP_FORMAT)).ask()
	else:
		rp_format_id = DEFAULT_JAVA_RP_FORMAT
		dp_format_id = DEFAULT_JAVA_DP_FORMAT


	console.rule("[bold green]Java Settings[/bold green]")

	# TODO: Implement version selection for different pack versions. Skip if use_advanced_settings because we already asked the user.

	rp_output_path: Path = Path(questionary.text("Enter Java Resource Pack output directory", "resource_pack").ask())
	if rp_output_path.exists() and ask_to_clear_path(rp_output_path):
		shutil.rmtree(rp_output_path)

	dp_output_path: Path = Path(questionary.text("Enter Java Datapack output directory", "datapack").ask())
	if dp_output_path.exists() and ask_to_clear_path(dp_output_path):
		shutil.rmtree(dp_output_path)

	pack_id = format_string(advanced_settings["pack_id"]) or DEFAULT_PACK_ID
	pack_name = str(advanced_settings["pack_name"])
	resource_pack_description = str(advanced_settings["pack_description"])
	music_disc_item_string = advanced_settings["disc_item_string"]
	java_resource_pack_format = float(rp_format_id)
	datapack_format = float(dp_format_id)
	jukebox_comparator_output = int(advanced_settings["jukebox_comparator_output"])
	audio_range = float(advanced_settings["audio_range"])

	pack_icon = Path(advanced_settings["pack_icon_path"])
	if not pack_icon.exists():
		console.print("Cannot find custom icon path, using default icon.", style="bold yellow")
		pack_icon = DEFAULT_PACK_ICON_PATH

	with console.status("Building Java packs...", spinner="dots"):

		rp_config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH,
											pack_id=pack_id,
											pack_description=resource_pack_description,
											output_path=Path(rp_output_path) or DEFAULT_JAVA_RP_PATH,
											disc_item_string=music_disc_item_string,
										   	jukebox_comparator_output=jukebox_comparator_output,
										   	pack_icon=pack_icon,
										   pack_format=java_resource_pack_format,
										   audio_range=audio_range,
										   pack_name=pack_name)

		dp_config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH,
										   pack_id=pack_id,
										   pack_description=resource_pack_description,
										   output_path=Path(dp_output_path) or DEFAULT_JAVA_RP_PATH,
										   disc_item_string=music_disc_item_string,
										   pack_icon=DEFAULT_ICON_PATH,
										   jukebox_comparator_output=jukebox_comparator_output,
										   pack_format=datapack_format,
										   audio_range=audio_range,
										   pack_name=pack_name)

		from generator.javarp.v88_0 import generate_rp
		from generator.javadp.v107_1 import generate_dp

		generate_rp(audio_files, rp_config)
		generate_dp(audio_files, dp_config)
	console.print("*** Java generation done!", style="green")

if "Bedrock (Resource Pack Only, Requires Geyser + Java Datapack)" in pack_types:
	console.rule("[bold green] Bedrock Settings [/bold green]")
	bedrock_rp_output_path = Path(questionary.text("Enter Bedrock Resource Pack output directory", str(DEFAULT_BEDROCK_RP_PATH)).ask())

	if bedrock_rp_output_path.exists() and ask_to_clear_path(bedrock_rp_output_path):
		shutil.rmtree(bedrock_rp_output_path)

	bedrock_rp_output_path.mkdir(parents=True, exist_ok=True)


	pack_id = format_string(advanced_settings["pack_id"]) or DEFAULT_PACK_ID
	pack_name = str(advanced_settings["pack_name"])
	resource_pack_description = str(advanced_settings["pack_description"])
	music_disc_item_string = advanced_settings["disc_item_string"]
	pack_icon = Path(advanced_settings["pack_icon_path"]) or DEFAULT_PACK_ICON_PATH
	jukebox_comparator_output = int(advanced_settings["jukebox_comparator_output"])
	audio_range = float(advanced_settings["audio_range"])

	with console.status("Building Bedrock packs...", spinner="dots"):
		rp_config: PackConfig = PackConfig(default_icon=DEFAULT_ICON_PATH,
										   pack_id=pack_id,
										   pack_description=resource_pack_description,
										   output_path=bedrock_rp_output_path or DEFAULT_BEDROCK_RP_PATH, # The actual pack is written to the "pack" subdir so that the Geyser mappings aren't included.
										   disc_item_string=music_disc_item_string,
										   jukebox_comparator_output=jukebox_comparator_output,
										   pack_icon=pack_icon,
										   pack_format=0.0,
										   audio_range=audio_range,
										   pack_name=pack_name)

		from generator.bedrockrp.geyser_bedrock import generate_bedrock_rp

		generate_bedrock_rp(audio_files, rp_config)
	console.print("*** Bedrock generation done!", style="green")
	console.print(f"NOTE: Bedrock packs do not currently work by themselves! A Geyser-enabled Java Edition server is required. Don't forget to put {bedrock_rp_output_path / "geyser_custom_discs.json"} into Geyser's item mapping folder!", style="yellow")
