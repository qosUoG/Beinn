import type { Directory } from "shared-types";

export let project_directory: Directory = $state({ files: [], dirs: {} })

export function setProjectDirectory(p: Directory) {
    project_directory = JSON.parse(JSON.stringify(p))
}