
import { exists, mkdir, readDir, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse, stringify } from "smol-toml"
import { dependency_controller } from "./dependency.svelte"
import { tick } from "svelte"
import { confirm } from "@tauri-apps/plugin-dialog"
import { shell } from "$lib/utils"
import { equipment_controller } from "./equipment.svelte"
import { experiment_controller } from "./experiment.svelte"
import { log_controller } from "./log.svelte"

class WorkspaceController {
    path: string | null = $state(null)
    status: "empty" | "loading" | "ready" = $state("empty")

    async loadWorkspace(path: string) {
        dependency_controller.reset()
        equipment_controller.reset()
        experiment_controller.reset()
        log_controller.reset()



        const old_status = this.status
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
            if (!confirmation) {
                this.status = old_status
                return
            }
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

        // Check what needs to be installed
        const required_packages = ["pandas", "tables", "numpy"];
        let install_command = ["add"];
        for (const pkg of required_packages) {
            if (!(parsed.project.dependencies as string[]).find(dep => dep.startsWith(pkg)))
                install_command.push(pkg)
        }

        if (install_command.length > 1)
            await shell({ fn: "uv", cmd: install_command, cwd: path, description: "Installing " + install_command.join(", ") })

        if (!(parsed.project.dependencies as string[]).find(dep => dep.startsWith("cnoc")))
            await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc", cwd: path, description: "Installing cnoc" })

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