
import { EE, type EET } from "./ee.svelte";
import { meallCreateEE, meallGetAvailableEEs, meallRemoveEE, meallSetEEParams } from "$lib/meall.svelte";
import { gstore, type Availables } from "./global.svelte";
import { getRandomId } from "$lib/utils";
import { tick } from "svelte";
import type { ModuleCls } from "./dependency.svelte";

export class Equipment extends EE {
    constructor(id: string, name?: string) {
        super(id, "equipment", name)
    }

}

export class Equipments {
    private _equipments: Record<string, Equipment> = $state({})
    get equipments() {
        return this._equipments
    }
    private _available_module_cls: Availables = $state([])

    toSave: () => EET[] = () => {
        return Object.values(this._equipments).map(e => e.toSave())
    }
    cleanup: (() => void) | undefined = undefined

    instantiate(payload?: { id?: string, name?: string }) {
        let id: string | undefined, name: string | undefined
        if (payload) {
            id = payload.id
            name = payload.name
        }

        if (!id) id = getRandomId(Object.keys(this._equipments))

        const new_equipment = new Equipment(id, name)
        this._equipments[id] = new_equipment



        return new_equipment
    }

    moduleClsValid(module_cls: ModuleCls) {
        return this._available_module_cls.find(({ modules, cls }) =>
            modules.includes(module_cls.module) && module_cls.cls === cls
        ) !== undefined
    }



    async refreshAvailables() {
        this._available_module_cls = await meallGetAvailableEEs("equipment", { prefixes: gstore.workspace.dependencies?.prefixes ?? [] })
    }

    get available_module_cls() {
        return this._available_module_cls
    }

    getInstanceables(id: string) {

        return Object.values(this._equipments)
            // Split here for type check sake
            .filter((e) => e.created)
            // Name needs to be defiend
            .filter((e) => e.id !== id && e.name && e.name.length > 0)
            .map((e) => ({ key: e.name, value: e.id }))

    }


}