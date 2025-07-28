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

    constructor() {
        workspace_controller.registerOnOpen(() => {

        })
        workspace_controller.registerCommand("equipment:imports", (data: Imports) => {
            this.imports = data
        })
        workspace_controller.registerCommand("equipment:create", (data: Equipment) => {
            this.#equipments[data.name] = data
        })
        workspace_controller.registerCommand("equipment:remove", (name: string) => {
            delete this.#equipments[name]
        })

    }

    updateImports() {
        workspace_controller.sendCommand("equipment:imports", { packages: dependency_controller.hasDriverPackageNames })
    }

    create(name: string, module: string, cls: string) {
        for (const equipment of Object.values(this.#equipments)) {
            if (equipment.name === name) {
                beinn_log_controller.append(`ERROR Equipment with name ${name} already exists`)
                return
            }
        }
        const equipment: Equipment = {

            name,
            module,
            cls,
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