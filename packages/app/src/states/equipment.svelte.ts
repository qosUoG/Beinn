
import { EE, type Availables, type EET } from "./ee.svelte";


import { beginProcedure, getRandomId, type StepT } from "$lib/utils";

import type { ModuleCls } from "./dependency.svelte";
import { meallGetAvailableEEs_throwable } from "$lib/meall.svelte";
import { workspace } from "./workspace.svelte";

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

    async instantiate(payload?: { id?: string, name?: string }) {
        const { step, completed, unhandled } = await beginProcedure("INSTANTIATE EQUIPMENT")
        try {
            const res = this.instantiate_throwable(step, payload)
            await completed()
            return res
        } catch (e) {
            await unhandled(e)
        }
    }

    async instantiate_throwable(step: StepT, payload?: { id?: string, name?: string }) {
        const new_equipment = await (step as unknown as StepT<Equipment>)("Instantiate equipment",
            () => {
                let id: string | undefined, name: string | undefined
                if (payload) {
                    id = payload.id
                    name = payload.name
                }

                if (!id) id = getRandomId(Object.keys(this._equipments))

                const new_equipment = new Equipment(id, name)
                this._equipments[id] = new_equipment

                return new_equipment
            })



        await step("Refresh available equipment list",
            async () => {
                await this.refreshAvailables_throwable();
            })


        return new_equipment

    }

    moduleClsValid(module_cls: ModuleCls) {
        return this._available_module_cls.find(({ modules, cls }) =>
            modules.includes(module_cls.module) && module_cls.cls === cls
        ) !== undefined
    }



    async refreshAvailables_throwable() {

        this._available_module_cls = await meallGetAvailableEEs_throwable("equipment", { prefixes: workspace.dependencies?.prefixes ?? [] })
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