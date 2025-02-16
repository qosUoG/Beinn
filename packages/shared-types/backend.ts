

export type BackendMessage = {
    command: "Set-Directory";
    payload: { path: string }
}

