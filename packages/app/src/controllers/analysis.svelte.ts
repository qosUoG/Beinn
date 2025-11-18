import { exists, readFile } from "@tauri-apps/plugin-fs";
import { File, ready, type Dataset, type Group } from "h5wasm";
import { workspace_controller } from "./workspace.svelte";
import { tick } from "svelte";
import { react, update, type Data } from "plotly.js-dist-min";
import type { ArchivedParams } from "./params.svelte";
import { shell } from "$lib/utils.svelte";
const { FS } = await ready


export class Tab {
    x: string
    y: string[]
    y_label: string
    x_label: string
    mode: "lines" | "markers" | "lines+markers"

    key: string

    temp_key: string
    time: number
    data: { title: string, data: number[] }[]
    params: Record<string, ArchivedParams | Record<string, ArchivedParams>>
    composite_opens: Record<string, boolean>
    note: string

    async rename_key(key: string) {
        await shell({
            fn: "uv",
            cmd: ["run", "rename_dataset", this.key, key],
            description: `Rename dataset from ${this.key} to ${key}`,
            cwd: workspace_controller.path!,
        })

        this.key = key
        this.temp_key = key
        await analysis_controller.load();

    }

    async set_x(value: string) {
        this.x = value
        await tick()
        this.plot()
    }

    toggle_y(value: string) {
        const index = this.y.indexOf(value)

        if (index !== -1) this.y.splice(index, 1)
        else this.y.push(value);
        this.plot()
    }
    set_x_label(value: string) {
        this.x_label = value


        update("plotly:div", {}, { xaxis: { title: { text: value } } })
    }

    set_y_label(value: string) {
        this.y_label = value


        update("plotly:div", {}, { yaxis: { title: { text: value } } })
    }



    async save_note(value: string) {
        await shell({
            fn: "uv",
            cmd: ["run", "save_note", this.key, value],
            description: `Save Note to ${this.key}`,
            cwd: workspace_controller.path!,
        })

        await analysis_controller.load();

    }

    set_mode(value: "lines" | "markers" | "lines+markers") {
        this.mode = value


        update("plotly:div", { mode: value }, {})
    }


    async delete() {
        await shell({
            fn: "uv",
            cmd: ["run", "delete_dataset", this.key],
            description: `Delete dataset ${this.key}`,
            cwd: workspace_controller.path!,
        })

        await analysis_controller.load();
    }

    get titles() {
        return this.data.map(d => d.title)
    }
    constructor(key: string, data: { title: string, data: number[] }[], params: Record<string, ArchivedParams | Record<string, ArchivedParams>>, note: string, time: number, x: string, y: string[], x_label: string, y_label: string, mode: "lines" | "markers" | "lines+markers") {
        this.key = $state(key)
        this.temp_key = $state(key)
        this.data = data
        this.x = $state(x)
        this.y = $state(y)
        this.params = $state(params)
        this.note = $state(note)
        this.time = time
        this.y_label = $state(y_label)
        this.x_label = $state(x_label)
        this.mode = $state(mode)

        const composite_opens: Record<string, boolean> = {}
        for (const [key, param] of Object.entries(params)) {
            if ("value" in param)
                continue
            composite_opens[key] = true
        }
        this.composite_opens = $state(composite_opens)
    }


    async plot() {
        await tick()
        const x = this.data.find(d => d.title === this.x)!.data
        const traces = this.y.map((y) => {
            return {
                x,
                y: this.data.find(d => d.title === y)!.data,
                mode: this.mode,
                type: "scatter",
                name: y,
            }
        })

        const layout: Partial<Plotly.Layout> = {
            autosize: true,

            margin: {
                pad: 4
            },


        }

        if (this.y_label !== "")
            layout["yaxis"] = {
                title: {
                    text: this.y_label,
                }

            }

        if (this.x_label !== "")
            layout["xaxis"] = {
                title: {
                    text: this.x_label,
                }
            }

        react("plotly:div", traces as Data[], layout)
    }
}

class AnalysisController {



    tabs: Record<string, Tab> = $state({})
    active_tab_index: string | undefined = $state(undefined)
    get active_tab() {
        if (this.active_tab_index === undefined) return undefined
        return this.tabs[this.active_tab_index]
    }
    sort: "time_desc" | "time_asc" | "key_asc" | "key_desc" = $state("time_desc")

    get list() {
        return Object.entries(this.tabs).map(([k, v]) => ({ id: k, tab: v })).toSorted(({ tab: a }, { tab: b }) => {
            switch (this.sort) {
                case "time_desc":
                    return b.time - a.time
                case "time_asc":
                    return a.time - b.time
                case "key_desc":
                    return b.key.localeCompare(a.key)
                case "key_asc":
                    return a.key.localeCompare(b.key)
            }
        })
    }

    async load(mode?: "delete") {
        if (workspace_controller.path === null || !await exists(workspace_controller.path + "/data.h5")) return

        let raw = await readFile(workspace_controller.path + "/data.h5");



        const randomuuid = crypto.randomUUID()
        FS.writeFile(randomuuid, raw);
        const file = new File(randomuuid, "r");

        const keys = file.keys()
        const tabs: Record<string, Tab> = {}
        for (const key of keys) {
            const metadata = JSON.parse((file.get(key) as Group).attrs["metadata"].value as string)

            const data: { title: string, data: number[] }[] = [];

            (metadata.columns as string[]).forEach((column) => {
                data.push({ title: column, data: [] })
            })

            const values = (file.get(key + "/table")! as Dataset).value! as number[][][]

            for (const vs of values)
                for (let i = 1; i < vs.length; i++)
                    data[i - 1].data.push(...vs[i])

            const old_tab = Object.values(this.tabs).find(t => t.key === key)
            if (old_tab !== undefined)
                tabs[crypto.randomUUID()] = new Tab(key, data, metadata.params, metadata.note, metadata.time, old_tab.x, old_tab.y, old_tab.x_label, old_tab.y_label, old_tab.mode)

            else
                tabs[crypto.randomUUID()] = new Tab(key, data, metadata.params, metadata.note, metadata.time, data[0].title, [data[1].title], data[0].title, "", "lines")


        }

        this.tabs = tabs


        // Try to reload the tabs
        if (mode === "delete") {
            this.active_tab_index = undefined

            await tick()


        }
    }
}
export const analysis_controller = new AnalysisController();