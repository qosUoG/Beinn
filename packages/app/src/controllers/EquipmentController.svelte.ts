import { dependency_controller } from "./DependencyController.svelte"
import { beinn_log_controller } from "./LogController.svelte"
import type { AllParamTypes } from "./Params.svelte"
import { workspace_controller } from "./WorkspaceController.svelte"

export type Imports = { module: string, cls: string }[]

export type Equipment = {
    name: string,
    module: string,
    cls: string,
    params: Record<string, AllParamTypes>,
    temp_params: Record<string, AllParamTypes>
}

class EquipmentController {

    #equipments = $state<Record<string, Equipment>>({})
    get equipments() {
        return Object.values(this.#equipments)
    }
    imports: Imports = $state([])

    temp_module: string = $state("")
    temp_cls: string = $state("")
    temp_name: string = $state("")

    constructor() {
        workspace_controller.registerOnOpen(() => {

        })
        workspace_controller.registerCallback("equipment:imports", (imports: Imports) => {
            this.imports = imports
        })
        workspace_controller.registerCallback("equipment:create", (equipment: Equipment) => {
            console.log(equipment)

            this.#equipments[equipment.name] = equipment

            if (equipment.name === this.temp_name && equipment.module === this.temp_module && equipment.cls === this.temp_cls) {
                this.temp_name = ""
                this.temp_module = ""
                this.temp_cls = ""
            }
        })
        workspace_controller.registerCallback("equipment:remove", (name: string) => {
            delete this.#equipments[name]
        })



    }

    updateImports() {
        workspace_controller.sendCommand("equipment:imports", { packages: dependency_controller.hasDriverPackageNames })
    }

    create() {
        for (const equipment of Object.values(this.#equipments)) {
            if (equipment.name === this.temp_name) {
                beinn_log_controller.append(`ERROR Equipment with name ${this.temp_name} already exists`)
                return
            }
        }
        const equipment: Equipment = {

            name: this.temp_name,
            module: this.temp_module,
            cls: this.temp_cls,
            params: {},
            temp_params: {}
        }
        workspace_controller.sendCommand("equipment:create", equipment)
    }

    remove(name: string) {
        if (!(name in this.#equipments)) {
            beinn_log_controller.append(`ERROR Equipment with name ${name} does not exist`)
            return
        }
        workspace_controller.sendCommand("equipment:remove", name)
    }
}

export const equipment_controller = $state(new EquipmentController())