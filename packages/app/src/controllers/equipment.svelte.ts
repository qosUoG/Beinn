import { deepCopy } from "$lib/utils"
import { EEBaseController, type Instance } from "./eebase.svelte"
import { workspace_controller } from "./workspace.svelte"




export type Equipment = Instance

export class EquipmentController extends EEBaseController<Equipment> {

    constructor() {
        super("equipment", (instance) => ({ ...instance, temp_params: deepCopy(instance.params) }))


    }
}

export const equipment_controller = $state(new EquipmentController())