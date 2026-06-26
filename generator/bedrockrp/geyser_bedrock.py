# TODO: Add Resource Pack Description
from pathlib import Path
import uuid

from generator.utils import PackConfig, write_json, move_audio
from rich.console import Console

console = Console()

def generate_bedrock_rp(audio_files: dict, config: PackConfig): # meta holds pack metadata, like config.pack_id and the output path.
	pack_output_dir = config.output_path / "pack"

	audio_output_dir = pack_output_dir / "sounds" / "records"
	icon_output_dir = pack_output_dir / "textures" / "items"

	audio_output_dir.mkdir(parents=True, exist_ok=True)
	icon_output_dir.mkdir(parents=True, exist_ok=True)

	manifest_json = {"format_version": 2,
                     "header": {
                         "name": config.pack_description,
                         "description": config.pack_description,
                         "uuid": str(uuid.uuid4()),
                         "version": [
                             0,
                             0,
                             0
                         ],
                         "min_engine_version": [
                             1,
                             21,
                             0
                         ]
                     },
                     "modules": [
                         {"type": "resources",
                          "uuid": str(uuid.uuid4()),
                          "version": [
                                0,
                                0,
                                0
						  ]
						  }
    				 ]
	}
	write_json(manifest_json, pack_output_dir / "manifest.json")

	move_audio(audio_files, config, audio_output_dir, icon_output_dir)

	sounds_json = {"individual_event_sounds": {
						"events": {}
	}}

	sound_definitions_json = {"format_version": "1.14.0",
							  "sound_definitions": {}}

	item_texture_json = {"resource_pack_name": config.pack_id,
						 "texture_name": "atlas.items",
						 "texture_data": {}}
	custom_discs_json = {"format_version": 2,
						 "items": {
							 f"minecraft:{config.disc_item_string}": [{
								"model": f"minecraft:{config.disc_item_string}",
								 "definitions": [
									 # stuff from loop goes here
								 ],
								 "type": "group"
						 	}]
						 }}

	for disc in audio_files:
		disc_id = audio_files[disc]["id_string"]
		disc_custom_model_id = int(audio_files[disc]["custom_model_data"])
		console.print("[BEDROCK RP] Processing disc", disc_id, style="grey50")

		sounds_json["individual_event_sounds"]["events"][config.pack_id + ":music_disc." + disc_id] = {"sound": config.pack_id + ":music_disc." + disc_id,
																										"volume": 10,
																										"pitch": 1
																									   }
		sound_definitions_json["sound_definitions"][config.pack_id + ":music_disc." + disc_id] = {
			"sounds": [
				{
					"name": f"sounds/records/{disc_id}",
					"stream": True,
					"volume": 2
				}
			]
		}
		item_texture_json["texture_data"][config.pack_id + ".item_" + disc_id] = {
			"textures": [
				"textures/items/" + disc_id
			]
		}
		custom_discs_json["items"][f"minecraft:{config.disc_item_string}"][0]["definitions"].append({
			"bedrock_identifier": f"{config.pack_id}:item/music_disc_{disc_id}",
			"display_name": audio_files[disc]["description"],
			"predicate": {
				"value": f"music_disc_{disc_id}",
				"property": "custom_model_data",
				"type": "match"
			},
			"bedrock_options": {
				"icon": f"{config.pack_id}.item_{disc_id}",
			},
			"type": "definition"
		})

	write_json(custom_discs_json, config.output_path / "geyser_custom_discs.json")

	write_json(sounds_json, pack_output_dir  / "sounds.json")
	write_json(sound_definitions_json, pack_output_dir / "sounds" / "sound_definitions.json")
	write_json(item_texture_json, pack_output_dir / "textures" / "item_texture.json")
