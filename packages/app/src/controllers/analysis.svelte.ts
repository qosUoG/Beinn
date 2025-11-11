import { exists, readFile, readTextFile } from "@tauri-apps/plugin-fs";
import h5wasm, { Dataset, Group, type File } from "h5wasm";
import { workspace_controller } from "./workspace.svelte";
import { tick } from "svelte";
import Plotly, { type Data } from "plotly.js-dist-min";
import type { ArchivedParams } from "./params.svelte";
import { shell } from "$lib/utils";



export class Tab {
    #key: string
    #temp_key: string
    time: number
    key_input: HTMLInputElement | undefined = $state(undefined)
    set_key(value: string) {
        this.#temp_key = value
    }
    async rename_key(key: string) {
        await shell({
            fn: "uv",
            cmd: ["run", "rename_dataset", this.#key, key],
            description: `Rename dataset from ${this.#key} to ${key}`,
            cwd: workspace_controller.path!,
        })

        this.#key = key
        this.#temp_key = key
        await analysis_controller.load("key");

    }
    get_key() {
        return this.#temp_key
    }
    data: { title: string, data: number[] }[]
    #x: string
    params: Record<string, ArchivedParams | Record<string, ArchivedParams>>
    composite_opens: Record<string, boolean>
    note_textarea: HTMLTextAreaElement | undefined = $state(undefined)


    get_x() {
        return this.#x
    }
    set_x(value: string) {
        this.#x = value
        this.plot()
    }
    #y: string[]
    y_includes(y: string) {
        return this.#y.includes(y)
    }
    toggle_y(value: string) {
        const index = this.#y.indexOf(value)

        if (index !== -1) this.#y.splice(index, 1)
        else this.#y.push(value);
        this.plot()
    }
    #y_label: string = $state("")
    set_y_label(value: string) {
        this.#y_label = value


        Plotly.update("plotly:div", {}, { yaxis: { title: { text: value } } })
    }
    get_y_label() {
        return this.#y_label
    }

    #note: string
    set_note(value: string) {
        this.#note = value
    }
    async save_note(value: string) {
        await shell({
            fn: "uv",
            cmd: ["run", "save_note", this.#key, value],
            description: `Save Note to ${this.#key}`,
            cwd: workspace_controller.path!,
        })

        await analysis_controller.load("note");

    }
    get_note() {
        return this.#note
    }

    #mode: "lines" | "markers" | "lines+markers" = "lines"
    set_mode(value: "lines" | "markers" | "lines+markers") {
        this.#mode = value


        Plotly.update("plotly:div", { mode: value }, {})
    }
    get_mode() {
        return this.#mode
    }

    async delete() {
        await shell({
            fn: "uv",
            cmd: ["run", "delete_dataset", this.#key],
            description: `Delete dataset ${this.#key}`,
            cwd: workspace_controller.path!,
        })

        await analysis_controller.load("delete");
    }

    get titles() {
        return this.data.map(d => d.title)
    }
    constructor(key: string, data: { title: string, data: number[] }[], params: Record<string, ArchivedParams | Record<string, ArchivedParams>>, note: string, time: number) {
        this.#key = $state(key)
        this.#temp_key = $state(key)
        this.data = data
        this.#x = $state(data[0].title)
        this.#y = $state(data.slice(1).map(d => d.title))
        this.params = $state(params)
        this.#note = $state(note)
        this.time = time

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
        const x = this.data.find(d => d.title === this.#x)!.data
        const traces = this.#y.map((y) => {
            return {
                x,
                y: this.data.find(d => d.title === y)!.data,
                mode: "markers",
                type: "scatter",
                name: y,
            }
        })

        const layout: Partial<Plotly.Layout> = {
            autosize: true,

            margin: {
                pad: 4
            },

            xaxis: {
                title: {
                    text: this.#x,
                }
            },
        }

        if (this.#y_label !== "")
            layout["yaxis"] = {
                title: {
                    text: this.#y_label,
                }
            }

        Plotly.react("plotly:div", traces as Data[], layout)
    }
}

class AnalysisController {



    tabs: Tab[] = $state([])
    active_tab_index: number | undefined = $state(undefined)
    get active_tab() {
        if (this.active_tab_index === undefined) return undefined
        return this.tabs[this.active_tab_index]
    }
    sort: "time_desc" | "time_asc" | "key_asc" | "key_desc" = $state("time_desc")



    get list() {
        return this.tabs.toSorted((a, b) => {
            switch (this.sort) {
                case "time_desc":
                    return b.time - a.time
                case "time_asc":
                    return a.time - b.time
                case "key_desc":
                    return b.get_key().localeCompare(a.get_key())
                case "key_asc":
                    return a.get_key().localeCompare(b.get_key())
            }
        })
    }

    async load(mode?: "note" | "key" | "delete") {
        if (workspace_controller.path === null || !await exists(workspace_controller.path + "/data.h5")) return

        const old_active_tab_index = this.active_tab_index

        let raw = await readFile(workspace_controller.path + "/data.h5");


        const { FS } = await h5wasm.ready
        const randomuuid = crypto.randomUUID()
        FS.writeFile(randomuuid, raw);
        const file = new h5wasm.File(randomuuid, "r");

        const keys = file.keys()
        const tabs: Tab[] = []
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
            tabs.push(new Tab(key, data, metadata.params, metadata.note, metadata.time))
        }

        this.tabs = tabs


        // Try to reload the tabs
        if (old_active_tab_index !== undefined)
            this.active_tab_index = old_active_tab_index

        await tick()

        if (mode === "note") {
            this.tabs[this.active_tab_index!]!.note_textarea!.focus()
        }

        if (mode === "key") {
            this.tabs[this.active_tab_index!]!.key_input!.focus()
        }

    }
}
export const analysis_controller = new AnalysisController();