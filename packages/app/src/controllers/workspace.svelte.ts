
import { exists, mkdir, readDir, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse, stringify } from "smol-toml"
import { dependency_controller } from "./dependency.svelte"
import { tick } from "svelte"
import { confirm } from "@tauri-apps/plugin-dialog"
import { shell } from "$lib/utils"
import { equipment_controller } from "./equipment.svelte"
import { experiment_controller } from "./experiment.svelte"

class WorkspaceController {
    path: string | null = $state(null)
    status: "empty" | "loading" | "ready" = $state("empty")

    async loadWorkspace(path: string) {
        this.status = "loading"
        await tick()
        const pyproject_exists = await exists(path + "/pyproject.toml")
        const dir_empty = (await readDir(path)).length === 0

        // Not empty directory without pyproject.toml
        if (!pyproject_exists && !dir_empty) {
            const confirmation = await confirm(
                `${path} is not empty. Are you sure to setup workspace here?`,
                { title: 'Directory Not Empty', kind: 'warning' }
            );

            // Abort if user chooses not to
            if (!confirmation) return
        }

        // Empty directory
        if (dir_empty) await shell({ fn: "uv", cmd: "init", cwd: path, description: "Initializing uv workspace" })


        // Update the path
        this.path = path
        await tick()

        // Update pyproject.toml
        const parsed = parse(await readTextFile(path + "/pyproject.toml")) as any;
        if (parsed.tool === undefined) parsed.tool = {}
        if (parsed.tool.uv === undefined) parsed.tool.uv = {}
        if (parsed.tool.uv["link-mode"] === undefined) parsed.tool.uv["link-mode"] = "copy"
        await writeTextFile(path + "/pyproject.toml", stringify(parsed))

        await shell({ fn: "uv", cmd: "add pandas tables numpy", cwd: path, description: "Installing pandas, tables, numpy" })

        await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc", cwd: path, description: "Installing cnoc" })

        // In case cnoc is already installed and stale
        await shell({ fn: "uv", cmd: "lock --upgrade-package cnoc", cwd: path, description: "Updating cnoc" })

        await shell({ fn: "uv", cmd: "sync", cwd: path, description: "Syncing uv" })

        await dependency_controller.readPyprojectToml({ path })

        // Check if .beinn exists
        const save_exists = await exists(path + "/.beinn")
        if (!save_exists) {
            await mkdir(path + "/.beinn")
            await dependency_controller.save()
        }
        else {
            await dependency_controller.loadSave(path)
        }

        await Promise.all([equipment_controller.updateImports(), experiment_controller.updateImports()])

        await tick()

        await equipment_controller.loadSave(path)
        await experiment_controller.loadSave(path)



        this.status = "ready"


    }
}


export let workspace_controller = $state(new WorkspaceController())