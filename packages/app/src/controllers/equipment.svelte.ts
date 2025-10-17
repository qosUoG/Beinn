import { deepCopy, shell, type Prettify } from "$lib/utils"
import { tick } from "svelte"
import type { SelectFloatParam, SelectStrParam, SimpleParamType } from "./params.svelte"
import { workspace_controller } from "./workspace.svelte"
import { Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, Instance, type ConcInstance, type InstanceSave } from "./_ee.svelte"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { log_controller } from "./log.svelte"

export class EquipmentController extends EEBaseController {

    temp = $state({
        name: "",
        module: "",
        cls: "",
    })

    #equipments = $state<Record<string, Instance>>({})
    get equipment_instances() {
        return Object.values(this.#equipments)
    }
    get equipment_names() {
        return this.equipment_instances.map(i => i.name)
    }

    constructor() { super("equipment") }

    async create({ name, module, cls, id }: { name: string, module: string, cls: string, id?: string }) {
        // Check if equipment with same name already exists
        if (name in this.equipment_names) {
            log_controller.appendError(`Equipment with name ${name} already exists`)
            return false
        }

        const equipment: Instance = new Instance(module, cls, name)

        await equipment.initialize()

        this.#equipments[id ?? crypto.randomUUID()] = equipment

        return true
    }

    async remove(name: string) {
        delete this.#equipments[name]

        await tick()

        await this.save()
    }

    async save() {
        let save: Record<string, InstanceSave> = {}
        for (const [id, equipment] of Object.entries(this.#equipments))
            save[id] = equipment.toSave()
        await writeTextFile(workspace_controller.path! + "/.beinn/equipments.json",
            JSON.stringify(save))
    }

    async loadSave(path: string) {
        if (!await exists(path + "/.beinn/equipments.json")) return
        const save = JSON.parse(await readTextFile(path + "/.beinn/equipments.json")) as Record<string, InstanceSave>

        for (const [id, equipment] of Object.entries(save)) {
            // Check if equipment is included in the imports
            const found = this.imports.find(imp => imp.module === equipment.module && imp.cls === equipment.cls)
            if (found === undefined) continue

            // Create the equipment
            const success = await this.create({ name: equipment.name, module: equipment.module, cls: equipment.cls, id })
            if (!success) continue
        }

        for (const [id, equipment] of Object.entries(save)) {
            if (!(id in this.#equipments)) continue
            // Apply the save
            this.#equipments[id].assignParams(equipment.params)
            this.#equipments[id].param_opens = equipment.param_opens
            for (const key of Object.keys(equipment.composite_opens))
                if (key in this.#equipments[id].composite_opens)
                    this.#equipments[id].composite_opens = equipment.composite_opens
        }
    }

    reset() {
        this.#equipments = {}
        this.imports = []
        this.temp = {
            name: "",
            module: "",
            cls: "",
        }
    }
}

export const equipment_controller = $state(new EquipmentController())