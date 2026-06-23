PACK_FORMAT = 88.0
"""
* move_audio_files implementation

rp description
rp output folder
pack id
music disc item string
output java folder


"""
def generate_java_resource_pack(audio_files: dict, meta: PackConfig): # meta holds pack metadata, like pack_id and the output path.
	move_audio_files(audio_files) # Also creates audio-related resource pack directories. Might move that elsewhere later.

	print("[>] Writing pack.mcmeta...")
	pack_mcmeta = {"pack": {"pack_format": PACK_FORMAT,
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
