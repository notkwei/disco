# TODO: Implement version picking between compatible RP version numbers (32, 34, and 42 should all work)
from generator.utils import write_json, move_audio, PackConfig
from pathlib import Path
from rich.console import Console

console = Console()


PACK_FORMAT: float = 88.0

def generate_rp(audio_files: dict, config: PackConfig): # meta holds pack metadata, like config.pack_id and the output path.
	pack_format: float = config.pack_format or PACK_FORMAT
	audio_output_dir = Path(config.output_path / "assets" / config.pack_id / "sounds" / "records")
	icon_output_dir = Path(config.output_path / "assets" / config.pack_id / "textures" / "item")

	audio_output_dir.mkdir(parents=True, exist_ok=True)
	icon_output_dir.mkdir(parents=True, exist_ok=True)


	Path(config.output_path / "assets" / config.pack_id / "models" / "item").mkdir(parents=True, exist_ok=True)
	Path(config.output_path / "assets" / "minecraft" / "items").mkdir(parents=True, exist_ok=True)

	if type(pack_format) is not int:
		versions = str(float(pack_format)).split(".")
	else:
		versions = [pack_format, 0]

	pack_mcmeta = {"pack": {"description": config.pack_description,
							"min_format": [int(versions[0]), int(versions[1])],
							"max_format": [int(versions[0]), int(versions[1])]}}  # Generate pack.mcmeta
	write_json(pack_mcmeta, config.output_path / "pack.mcmeta")

	move_audio(audio_files, config, audio_output_dir, icon_output_dir)

	sounds_json = {}
	model_data_mappings = \
		{"model": {
			"type": "select",
			"property": "custom_model_data",
			"fallback": {
				"type": "model",
				"model": f"item/{config.disc_item_string}"
			},
			"cases": []
		}
	}

	for disc in audio_files:
		disc_id = audio_files[disc]["id_string"]
		disc_custom_model_id = int(audio_files[disc]["custom_model_data"])
		console.print("[RP] Processing disc", disc_id, style="grey50")

		sounds_json["music_disc." + disc_id] = {"sounds": [{"name": config.pack_id + ":records/" + disc_id,
															"stream": True}]}  # formats sounds.json as music_disc.id_string = {"sounds"...}
		model_data_mappings["model"]["cases"].append({"when": f"music_disc_{disc_id}",
													  "model": {
														  "type": "model",
														  "model": f"{config.pack_id + ":item/music_disc_" + disc_id}"}
													  })


		item_json = {"parent": "item/generated",
					 "textures": {
						 "layer0": config.pack_id + ":item/" + disc_id
					 }}
		write_json(item_json, config.output_path / "assets" / config.pack_id / "models" / "item" / f"music_disc_{disc_id}.json")

	write_json(sounds_json, config.output_path / "assets" / config.pack_id / "sounds.json")
	write_json(model_data_mappings, config.output_path / "assets" / "minecraft" / "items" / f"{config.disc_item_string}.json")
