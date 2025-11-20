import { tick } from "svelte"
import { workspace_controller } from "./workspace.svelte"
import { EEBaseController, Instance, type ConcInstance, type InstanceSave } from "./_ee.svelte"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { log_controller } from "./log.svelte"
import { Repl } from "./repl.svelte"
import { runtime2Save, save2Runtime, type RuntimeAllParamTypes } from "./params.svelte"

export class EquipmentController extends EEBaseController {

    temp = $state({
        name: "",
        module: "",
        cls: "",
    })

    equipments = $state<Instance[]>([])

    get equipment_names() {
        return this.equipments.map(i => i.name)
    }

    constructor() { super("equipment") }

    async create({ name, module, cls }: { name: string, module: string, cls: string }) {
        // Check if equipment with same name already exists
        if (name in this.equipment_names) {
            log_controller.appendError(`Equipment with name ${name} already exists`)
            return false
        }

        const equipment: Instance = new Instance(module, cls, name)

        await equipment.initialize()

        this.equipments.push(equipment)
        return true
    }

    async remove(name: string) {
        this.equipments = this.equipments.filter(e => e.name !== name)
        await tick()

        await this.save()
    }

    async save() {
        let save = this.equipments.map(e => e.toSave())

        await writeTextFile(workspace_controller.path! + "/.beinn/equipments.json",
            JSON.stringify(save))
    }

    async loadSave(path: string) {
        if (!await exists(path + "/.beinn/equipments.json")) return
        const save = JSON.parse(await readTextFile(path + "/.beinn/equipments.json")) as InstanceSave[]

        for (const equipment of save) {
            // Check if equipment is included in the imports
            const found = this.imports.find(imp => imp.module === equipment.module && imp.cls === equipment.cls)
            if (found === undefined) {
                log_controller.appendError(`Error while loading save of ${equipment.name} save:  ${equipment.module}  ${equipment.cls} not found`)
                continue
            }

            // Create the equipment
            const success = await this.create({ name: equipment.name, module: equipment.module, cls: equipment.cls })
            if (!success)
                log_controller.appendError(`Error while loading save of ${equipment.name} save:Cannot create equipment`)


        }

        for (const s of save) {
            const equipment = this.equipments.find(e => e.name === s.name)
            if (equipment === undefined) {
                log_controller.appendError(`Parameter of ${s.name} is not applied: equipment not found`)
                continue
            }

            // Apply the save
            equipment.assignParams(save2Runtime(s.params))
            await tick()


            equipment.param_opens = s.param_opens
            for (const key of Object.keys(s.composite_opens))
                if (key in equipment.composite_opens)
                    equipment.composite_opens = equipment.composite_opens
        }
    }

    repl: Repl | undefined = $state(undefined)

    async startREPL(equipment: Instance | undefined) {
        if (this.repl !== undefined) {
            log_controller.appendError(`REPL session of ${equipment?.name ? equipment.name : "all equipments"} already running`)
            return
        }

        // Create temporary file for repl initialization
        let text = [
            "import json",
            "from typing import Any",
            "from cnoc import EquipmentABC"
        ];

        let equipments: Instance[]

        if (equipment !== undefined) {
            equipments = [equipment]
            // Add all equipments referenced in the param list to the equipments list
            const addEquipment = (equipment: Instance) => {
                if (equipments.find(e => e.name === equipment.name)) return
                equipments.push(equipment)
            }

            for (const param of Object.values(equipment.params)) {
                if (param.type === "instance.equipment" && param.instance) {
                    addEquipment(param.instance)
                    continue
                }

                if (!("type" in param)) continue


                for (const child of Object.values(param as Record<string, RuntimeAllParamTypes>))
                    if (child.type === "instance.equipment" && child.instance)
                        addEquipment(child.instance)

            }
        }
        else
            equipments = this.equipments

        for (const equipment of equipments)
            text.push(`from ${equipment.module} import ${equipment.cls}`)

        for (const equipment of equipments)
            text.push(`${equipment.name} = ${equipment.cls}()`)

        text.push("equipments: dict[str,EquipmentABC[Any]] = {}")
        for (const equipment of equipments)
            text.push(`equipments["${equipment.name}"] = ${equipment.name}`)

        for (const equipment of equipments)
            text.push(`${equipment.name}.setParams(json.loads("""${JSON.stringify(equipment.params)}"""),equipments,${equipment.name}.params.__class__)\n`)

        for (const equipment of equipments)
            text.push(`${equipment.name}.interactive()`)


        await writeTextFile(workspace_controller.path! + "/.beinn/repl.py", text.join("\n"))
        this.repl = new Repl(text.join("\n"), equipments)
    }

    closeREPL() {
        if (this.repl && this.repl.online) this.repl.kill()

        this.repl = undefined
    }

    reset() {
        this.equipments = []
        super.reset()

        if (this.repl && this.repl.online) this.repl.kill()
        this.repl = undefined

        this.temp = {
            name: "",
            module: "",
            cls: "",
        }
    }
}

export const equipment_controller = $state(new EquipmentController())