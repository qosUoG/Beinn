<script lang="ts">
	import Disk from "$icons/Disk.svelte";
	import Loader from "$icons/Loader.svelte";
	import { getRandomId } from "$lib/utils";

	import {
		disconnectWorkspace,
		readAllUvDependencies,
		loadWorkspace,
		saveWorkspace,
		addDependency,
	} from "$services/backend.svelte";
	import {
		connnectCliWs,
		createEE,
		getAvailableEEs,
		setEEParams,
	} from "$services/qoslabapp.svelte";

	import { gstore, resetGstore } from "$states/global.svelte";
	import { type Dependency } from "qoslab-shared";
	import { tick } from "svelte";

	let loading = $state(false);
</script>

<label class=" frow-1 flex-grow">
	<div class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
		Project Directory
	</div>
	<input
		spellcheck="false"
		class="flex-grow wrapped bg-slate-200"
		type="text"
		bind:value={gstore.workspace.path} />

	{#if loading}
		<div class="min-w-20 slate rounded flex">
			<div class="slate icon-btn m-auto"><Loader /></div>
		</div>
	{:else if gstore.workspace.connected}
		<button
			class="wrapped slate min-w-20"
			onclick={async () => {
				loading = true;
				gstore.workspace.connected = false;
				await tick();
				// shutdown the workspace
				await disconnectWorkspace();
				resetGstore();

				// reset gstore
				loading = false;
			}}>Disconnect</button>
		<button class="wrapped slate" onclick={saveWorkspace}>Save</button>
		<!-- <button
			class="wrapped slate text-nowrap"
			onclick={() => {
				// Save the whole configuration to another path
			}}>Save as</button> -->
	{:else}
		<button
			class="wrapped slate min-w-20"
			onclick={async () => {
				loading = true;
				await tick();
				// set the project directory
				const load = await loadWorkspace();

				// fetch the dependency from pyproject.toml
				const new_dependencies: Record<string, Dependency> = {};

				(await readAllUvDependencies()).forEach((d) => {
					const id = getRandomId(Object.keys(new_dependencies));

					new_dependencies[id] = { ...d, id };
				});

				if (load.save !== undefined) {
					// Try to establish all dependencies
					Object.values(load.save.dependencies).forEach((d) => {
						if (d.confirmed && d.source.type === "local") {
							const id = getRandomId(
								Object.keys(new_dependencies)
							);
							d.id = id;
							gstore.workspace.dependencies[id] = d;
						}
					});
				}

				gstore.workspace.dependencies = new_dependencies;

				await tick();
				if (load.save !== undefined) {
					// Then try to install dependencies that is not being installed
					Object.values(load.save.dependencies).forEach(async (d) => {
						if (!d.confirmed || d.add_string === undefined) return;
						if (
							!Object.values(gstore.workspace.dependencies).find(
								(gd) => {
									// type check
									if (!gd.confirmed) return true;

									if (gd.fullname === d.fullname) return true;
									if (gd.source.type === "local") return true;
									if (gd.add_string === undefined)
										return true;
								}
							)
						) {
							// Not found dependency, try to install
							await addDependency(d.add_string);

							// Read All dependencies and figure out which is the new one
							const allDependencies =
								await readAllUvDependencies();

							const current_dependency_names = Object.values(
								$state.snapshot(gstore.workspace.dependencies)
							)
								.filter((d) => d.confirmed)
								.map((d) => d.name);

							Object.values(allDependencies).forEach((d) => {
								if (
									!current_dependency_names.includes(d.name)
								) {
									const id = getRandomId(
										Object.keys(
											gstore.workspace.dependencies
										)
									);
									gstore.workspace.dependencies[id] = {
										...d,
										id,
										add_string: d.add_string,
									};
								}
							});

							await tick();
						}
					});
				}

				// Connect to cli ws
				gstore.log_socket = connnectCliWs<string>({
					onmessage: (message) => {
						const res = JSON.parse(message.data) as
							| {
									type: "exec";
									result: null;
							  }
							| { type: "eval"; result: string }
							| {
									type: "error";
									result: string;
							  };

						if (res.type !== "exec")
							gstore.logs.push({
								source: "equipment",
								timestamp: Date.now(),
								content: res.result,
							});
					},
				});

				gstore.workspace.available_equipments =
					await getAvailableEEs("equipment");

				gstore.workspace.available_experiments =
					await getAvailableEEs("experiment");

				await tick();

				if (load.save !== undefined) {
					// Try to create all equipments and experiments
					Object.values(load.save.equipments).forEach(async (e) => {
						if (!e.created) return;
						// First check if equipment is available in dependency

						if (
							!gstore.workspace.available_equipments.find(
								({ modules, cls }) => {
									return (
										e.module_cls.cls === cls &&
										modules.includes(e.module_cls.module)
									);
								}
							)
						)
							return;

						// Create the equipment
						const id = getRandomId(
							Object.keys(gstore.workspace.available_equipments)
						);
						gstore.equipments[id] = {
							...e,
							id,
						};

						await createEE("equipment", e);
						await tick();
					});

					Object.values(load.save.experiments).forEach(async (e) => {
						if (!e.created) return;
						// First check if experiment is available in dependency

						if (
							!gstore.workspace.available_experiments.find(
								({ modules, cls }) => {
									return (
										e.module_cls.cls === cls &&
										modules.includes(e.module_cls.module)
									);
								}
							)
						)
							return;

						// Create the experiment
						const id = getRandomId(
							Object.keys(gstore.workspace.available_experiments)
						);
						gstore.experiments[id] = {
							...e,
							id,
						};

						await createEE("experiment", e);
						await tick();
					});

					await tick();

					// Then try to set params
					Object.values(gstore.equipments).forEach(async (e) => {
						if (!e.created) return;

						await setEEParams("equipment", e);
						await tick();
					});

					Object.values(gstore.experiments).forEach(async (e) => {
						if (!e.created) return;

						await setEEParams("experiment", e);
						await tick();
					});
				}

				gstore.workspace.connected = true;

				loading = false;
			}}>Connect</button>
	{/if}
</label>
