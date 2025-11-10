<script lang="ts">
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { readFile, readTextFile } from "@tauri-apps/plugin-fs";
	import h5wasm, { Dataset } from "h5wasm";
	const { FS } = await h5wasm.ready;

	let raw = await readFile(workspace_controller.path! + "/data.h5");
	FS.writeFile("data.h5", raw);
	let data = new h5wasm.File("data.h5", "r");
	console.log(data.keys());
	console.log(JSON.parse(data.get("pid3").attrs.metadata.value));
</script>
