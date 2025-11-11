import { exists, readFile, readTextFile } from "@tauri-apps/plugin-fs";
import h5wasm, { Dataset, Group, type File } from "h5wasm";
import { workspace_controller } from "./workspace.svelte";
import { tick } from "svelte";
import Plotly, { type Data } from "plotly.js-dist-min";
import type { ArchivedParams } from "./params.svelte";
import { shell } from "$lib/utils";



export class Tab {
    key: string
    data: { title: string, data: number[] }[]
    #x: string
    params: Record<string, ArchivedParams | Record<string, ArchivedParams>>
    composite_opens: Record<string, boolean>
    note_textarea: HTMLTextAreaElement | undefined = $state(undefined)
    #plot_div: HTMLDivElement | undefined = $state(undefined)
    mount(plot_div: HTMLDivElement) {
        this.#plot_div = plot_div

        tick().then(() => {
            this.plot()
        })
    }
    unmount() {
        this.#plot_div = undefined
    }

    get_x() {
        return this.#x
    }
    set_x(value: string) {
        this.#x = value
        if (this.#plot_div === undefined) return

        tick().then(() => {
            this.plot()
        })
    }
    #y: string[]
    y_includes(y: string) {
        return this.#y.includes(y)
    }
    async toggle_y(value: string) {
        const index = this.#y.indexOf(value)

        if (index !== -1) this.#y.splice(index, 1)
        else this.#y.push(value);

        if (this.#plot_div === undefined) return

        await tick()
        this.plot()
    }
    #y_label: string = $state("")
    set_y_label(value: string) {
        this.#y_label = value
        if (this.#plot_div === undefined) return

        Plotly.update(this.#plot_div, {}, { yaxis: { title: { text: value } } })
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
            cmd: ["run", "save_note", this.key, value],
            description: `Save Note to ${this.key}`,
            cwd: workspace_controller.path!,
        })

        await analysis_controller.load(true);

    }
    get_note() {
        return this.#note
    }

    #mode: "lines" | "markers" | "lines+markers" = "lines"
    set mode(value: "lines" | "markers" | "lines+markers") {
        this.#mode = value
        if (this.#plot_div === undefined) return

        Plotly.update(this.#plot_div, { mode: value }, {})
    }
    get mode() {
        return this.#mode
    }

    get titles() {
        return this.data.map(d => d.title)
    }
    constructor(key: string, data: { title: string, data: number[] }[], params: Record<string, ArchivedParams | Record<string, ArchivedParams>>, note: string) {
        this.key = key
        this.data = data
        this.#x = $state(data[0].title)
        this.#y = $state(data.slice(1).map(d => d.title))
        this.params = $state(params)
        this.#note = $state(note)

        const composite_opens: Record<string, boolean> = {}
        for (const [key, param] of Object.entries(params)) {
            if ("value" in param)
                continue
            composite_opens[key] = true
        }
        this.composite_opens = $state(composite_opens)
    }


    plot() {

        if (this.#plot_div === undefined) return

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

        Plotly.react(this.#plot_div, traces as Data[], layout)
    }
}

class AnalysisController {


    file: File | undefined = $state(undefined)
    tabs: (Tab | undefined)[] = $state([])
    active_tab_index: number | undefined = $state(undefined)
    get active_tab() {
        if (this.active_tab_index === undefined) return undefined
        return this.tabs[this.active_tab_index]
    }
    #list: { time: number, key: string }[] = $state([])
    sort: "time_desc" | "time_asc" | "key_asc" | "key_desc" = $state("time_desc")



    constructor() {

    }

    get list() {
        return this.#list.toSorted((a, b) => {
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

    async load(focus_note?: boolean) {
        if (workspace_controller.path === null || !await exists(workspace_controller.path + "/data.h5")) return

        let raw = await readFile(workspace_controller.path + "/data.h5");


        const { FS } = await h5wasm.ready
        const randomuuid = crypto.randomUUID()
        FS.writeFile(randomuuid, raw);
        const file = new h5wasm.File(randomuuid, "r");

        const keys = file.keys()
        const list: { time: number, key: string }[] = []
        for (const key of keys) {
            const metadata = JSON.parse((file.get(key) as Group).attrs["metadata"].value as string)
            list.push({ time: metadata.time, key })
        }

        this.#list = list
        this.file = file

        // Try to reload the tabs
        const old_tabs = this.tabs
        const old_active_tab_index = this.active_tab_index
        this.active_tab_index = undefined
        this.tabs = []
        await tick()

        for (const tab of old_tabs) {
            if (tab === undefined) {
                await this.addTab()
                continue
            }
            if (this.#list.find(t => t.key === tab.key) === undefined) await this.addTab()

            await this.addTab(tab.key)
        }

        this.active_tab_index = old_active_tab_index
        await tick()

        if (focus_note) {
            this.tabs[this.active_tab_index!]!.note_textarea!.focus()
        }

    }

    async addTab(key?: string) {
        if (key === undefined) {
            this.tabs.push(undefined)
            await tick()
            this.active_tab_index = this.tabs.length - 1
            return
        }



        const data: { title: string, data: number[] }[] = []

        const metadata: any = JSON.parse((this.file!.get(key) as Group).attrs["metadata"].value as string);

        (metadata.columns as string[]).forEach((column) => {
            data.push({ title: column, data: [] })
        })

        const values = (this.file!.get(key + "/table")! as Dataset).value! as number[][][]

        for (const vs of values)
            for (let i = 1; i < vs.length; i++)
                data[i - 1].data.push(...vs[i])

        this.tabs.push(new Tab(key, data, metadata.params, metadata.note))
        await tick()
        this.active_tab_index = this.tabs.length - 1

    }

    setTab(key: string) {
        const data: { title: string, data: number[] }[] = []
        const metadata = JSON.parse((this.file!.get(key) as Group).attrs["metadata"].value as string);

        (metadata.columns as string[]).forEach(column => {
            data.push({ title: column, data: [] })
        })

        const values = (this.file!.get(key + "/table")! as Dataset).value! as number[][][]

        for (const vs of values)
            for (let i = 1; i < vs.length; i++)
                data[i - 1].data.push(...vs[i])

        this.tabs[this.active_tab_index!] = new Tab(key, data, metadata.params, metadata.note)
    }

    removeTab(index: number) {
        this.tabs.splice(index, 1)

        if (this.active_tab_index === undefined) return

        if (index === this.active_tab_index) {
            this.active_tab_index = undefined
            return
        }

        if (this.active_tab_index > index) {
            this.active_tab_index--
            return
        }
    }





}
export const analysis_controller = new AnalysisController();