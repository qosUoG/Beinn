import type { Prettify } from "$lib/utils"
import { Command } from "@tauri-apps/plugin-shell"
import type { AllParamTypes } from "./params.svelte"
import { dependency_controller } from "./dependency.svelte"
import { workspace_controller } from "./workspace.svelte"
import { beinn_log_controller } from "./log.svelte"

export type Imports = { module: string, cls: string }[]

export type ConcInstance = {
    module: string,
    cls: string,
    params: Record<string, AllParamTypes>,
}


export abstract class EEBaseController {
    imports: Imports = $state([])



    eetype: "equipment" | "experiment"


    constructor(eetype: "equipment" | "experiment") {
        this.eetype = eetype
    }

    async updateImports() {

        const res = await Command.create(
            "uv",
            ["run", "imports", this.eetype, ...dependency_controller.has_driver_package_names]
            , {
                encoding: "utf8",
                cwd: workspace_controller.path!
            }).execute()

        if (res.code !== 0) {
            beinn_log_controller.append(`error while updating imports for equipment: ${res.stderr}`)
            return
        }

        this.imports = JSON.parse(res.stdout) as Imports

    }


}