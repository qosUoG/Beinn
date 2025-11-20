import { exists, readDir, readFile, remove, rename, writeFile } from "@tauri-apps/plugin-fs";
import { workspace_controller } from "./workspace.svelte";
import { tick } from "svelte";
import { react, update, type Data } from "plotly.js-dist-min";
import type { ArchivedParams } from "./params.svelte";
import wasmInit, { ParquetFile, readParquet, writeParquet, WriterPropertiesBuilder } from "parquet-wasm/esm";
import * as arrow from "@apache-arrow/ts";
import wasmUrl from "parquet-wasm/esm/parquet_wasm_bg.wasm?url";

await wasmInit(wasmUrl);



export class Tab {

    key: string
    temp_key: string
    time: number

    content: {
        x: string
        y: string[]
        y_label: string
        x_label: string
        data: { title: string, data: number[] }[]
        params: Record<string, ArchivedParams | Record<string, ArchivedParams>>
        note: string
        composite_opens: Record<string, boolean>
        mode: "lines" | "markers" | "lines+markers",

    } | undefined

    async rename_key(key: string) {
        if (analysis_controller.list.find(v => v.tab.key === key) !== undefined) return

        await rename(workspace_controller.path + "/data/" + this.key + ".parquet", workspace_controller.path + "/data/" + key + ".parquet");
        this.key = key
        this.temp_key = key
        await analysis_controller.load();
    }

    async set_x(value: string) {
        if (this.content === undefined) {
            await this.loadContent()
            this.content!.x = value
            await tick()
            this.plot()

        }
        else {
            this.content!.x = value
            await tick()
            this.plot()
        }
    }

    toggle_y(value: string) {
        if (this.content === undefined) this.loadContent().then(() => {
            const index = this.content!.y.indexOf(value)
            if (index !== -1) this.content!.y.splice(index, 1)
            else this.content!.y.push(value);
            this.plot()
        })
        else {
            const index = this.content!.y.indexOf(value)
            if (index !== -1) this.content!.y.splice(index, 1)
            else this.content!.y.push(value);
            this.plot()
        }
    }
    set_x_label(value: string) {
        if (this.content === undefined) this.loadContent().then(() => {
            this.content!.x_label = value
            update("plotly:div", {}, { xaxis: { title: { text: value } } })
        })
        else {
            this.content!.x_label = value
            update("plotly:div", {}, { xaxis: { title: { text: value } } })
        }
    }

    set_y_label(value: string) {
        if (this.content === undefined) this.loadContent().then(() => {
            this.content!.y_label = value
            update("plotly:div", {}, { yaxis: { title: { text: value } } })
        })

        else {
            this.content!.y_label = value
            update("plotly:div", {}, { yaxis: { title: { text: value } } })
        }
    }



    async save_note(value: string) {
        const raw = await readFile(workspace_controller.path + "/data/" + this.key + ".parquet");
        const file = await ParquetFile.fromFile(new Blob([raw]));
        const metadata = file.metadata().fileMetadata().keyValueMetadata();
        metadata.set("note", value)



        const bytes = writeParquet(await file.read(), new WriterPropertiesBuilder().setKeyValueMetadata(metadata).build());

        await writeFile(workspace_controller.path + "/data/" + this.key + ".parquet", bytes);

        file.free();

    }

    set_mode(value: "lines" | "markers" | "lines+markers") {
        if (this.content === undefined) this.loadContent().then(() => {
            this.content!.mode = value
            update("plotly:div", { mode: value }, {})
        })

        else {
            this.content!.mode = value
            update("plotly:div", { mode: value }, {})
        }

    }

    get titles() {
        return this.content!.data.map(d => d.title)
    }


    async delete() {
        await remove("data/" + this.key + ".parquet");
    }

    async loadContent() {
        const raw = await readFile(workspace_controller.path + "/data/" + this.key + ".parquet");
        const file = await ParquetFile.fromFile(new Blob([raw]));
        const metadata = file.metadata().fileMetadata().keyValueMetadata()

        const data: { title: string, data: number[] }[] = [];

        const table = arrow.tableFromIPC(readParquet(raw).intoIPCStream());
        for (const column of table.schema.fields) {
            data.push({ title: column.name, data: Array.from(table.getChild(column.name)!.toArray()).map(v => Number(v)) })
        }
        const params: Record<string, ArchivedParams | Record<string, ArchivedParams>> = JSON.parse(metadata.get("params"))
        const composite_opens: Record<string, boolean> = {}
        for (const [key, param] of Object.entries(params)) {
            if ("value" in param)
                continue
            composite_opens[key] = true
        }

        this.content = {
            x: data[0].title,
            y: [data[1].title],
            y_label: "",
            x_label: data[0].title,
            data,
            params,
            note: metadata.get("note"),
            composite_opens,
            mode: "lines",
        }

        file.free();
    }

    constructor(
        key: string,
        time: number,
        content: {
            x: string, y: string[], y_label: string, x_label: string,
            data: { title: string, data: number[] }[],
            params: Record<string, ArchivedParams | Record<string, ArchivedParams>>,
            composite_opens: Record<string, boolean>
            note: string,
            mode: "lines" | "markers" | "lines+markers",

        } | undefined = undefined) {

        this.content = $state(content)
        this.key = $state(key)
        this.temp_key = $state(key)
        this.time = time
    }


    async plot() {
        if (this.content === undefined) await this.loadContent()


        const {
            x, y, y_label, x_label, data, mode
        } = this.content!

        await tick()
        const x_data = data.find(d => d.title === x)!.data
        const traces = y.map((y) => {
            return {
                x: x_data,
                y: data.find(d => d.title === y)!.data,
                mode: mode,
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

        if (y_label !== "")
            layout["yaxis"] = {
                title: {
                    text: y_label,
                }

            }

        if (x_label !== "")
            layout["xaxis"] = {
                title: {
                    text: x_label,
                }
            }



        react("plotly:div", traces as Data[], layout)
    }
}

class AnalysisController {



    active_tab: Tab | undefined = $state(undefined)


    sort: "time_desc" | "time_asc" | "key_asc" | "key_desc" = $state("time_desc")
    #tabs: Record<string, Tab> = $state({})

    get list() {
        return Object.entries(this.#tabs).map(([k, v]) => ({ id: k, tab: v })).toSorted(({ tab: a }, { tab: b }) => {
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
        if (workspace_controller.path === null || !await exists(workspace_controller.path + "/data")) return

        let directory =
            (await readDir(workspace_controller.path + "/data"))
                .filter((entry) => entry.name.endsWith(".parquet"))
                .map(({ name }) => name.replace(".parquet", ""));

        const tabs: Record<string, Tab> = {};
        for (const key of directory) {
            const raw = await readFile(workspace_controller.path + "/data/" + key + ".parquet");
            const file = await ParquetFile.fromFile(new Blob([raw]));
            const metadata = file.metadata().fileMetadata().keyValueMetadata()
            const time = parseInt(metadata.get("time"));




            const old_tab = Object.values(this.#tabs).find(t => t.key === key)
            tabs[crypto.randomUUID()] = new Tab(key, time, old_tab?.content)
        }

        this.#tabs = tabs


        // Try to reload the tabs
        if (mode === "delete") {
            this.active_tab = undefined
            await tick()
        }
    }
}
export const analysis_controller = new AnalysisController();