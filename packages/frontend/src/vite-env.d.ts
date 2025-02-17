/// <reference types="svelte" />
/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_DEFAULT_EXPERIMENT_PATH: string
    // more env variables...
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}