import { workspace_controller } from "$controllers/workspace.svelte"
import { Child, Command } from "@tauri-apps/plugin-shell"
import type { Instance } from "./_ee.svelte"
import { Cli } from "./cli.svelte"

export class Repl {
    cli: Cli = $state(new Cli())

    process: Child | undefined = undefined
    instances: Instance[]
    online: boolean = $state(false)

    constructor(preload: string, instances: Instance[]) {

        this.instances = $state(instances)
        const commands = ["run", "python", "-u", "-i", "./.beinn/repl.py"]


        const handler = Command.create(
            "uv", commands, {
            encoding: "utf8",
            cwd: workspace_controller.path!,
        })

        handler.stdout.on("data", (line) => {
            this.cli.logs.append(line);

        })
        handler.stderr.on("data", (line) => {
            this.cli.logs.append(line);


        })

        handler.on("close", (data) => {
            this.process = undefined
            this.online = false
        })

        handler.on('error', error => console.error(`command error: "${error}"`));



        handler.spawn().then(async (process) => {
            this.process = process
            this.online = true
            this.cli.logs.append(">>> " + preload);

        })

    }

    async write(code: string) {
        if (!this.process) return
        this.cli.logs.append(">>> " + code);
        this.cli.history.add(code);
        await this.process.write(code)
    }



    async kill() {
        await this.process!.kill()
    }

}