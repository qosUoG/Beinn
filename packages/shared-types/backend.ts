

export type ToBackendMessage = {
    command: "Set-Directory";
    payload: { path: string }
} | {
    command: "Start-Experiment";
    payload: {
        cwd: string,
        script_name: string
    }
}

