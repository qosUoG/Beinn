import { workspace_controller } from "$controllers/workspace.svelte"
import { Child, Command } from "@tauri-apps/plugin-shell"
import type { Instance } from "./_ee.svelte"


export class Repl {
    process: Child | undefined = undefined
    instances: Instance[]
    online: boolean = $state(false)

    constructor(preload: string, instances: Instance[]) {

        this.instances = $state(instances)
        const handler = Command.create(
            ".venv/bin/python", ["-u", "-i", "./.beinn/repl.py"], {
            encoding: "utf8",
            cwd: workspace_controller.path!,
        })

        handler.stdout.on("data", (line) => {
            this.log += line;

        })
        handler.stderr.on("data", (line) => {
            this.log += line;


        })

        handler.on("close", (data) => {
            this.process = undefined
            this.online = false
        })

        handler.on('error', error => console.error(`command error: "${error}"`));



        handler.spawn().then(async (process) => {
            this.process = process
            this.online = true

            this.log += ">>> " + preload + "\n";
        })

    }

    async write(code: string) {
        if (!this.process) return

        this.log += ">>> " + code;
        await this.process!.write(code)
    }



    async kill() {
        await this.process!.kill()
    }



    log = $state("")



}