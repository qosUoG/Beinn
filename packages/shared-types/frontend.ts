export interface Directory {
    files: string[],
    dirs: Record<string, Directory>
}

export type ToFrontendMessage = {
    command: "Project-Directory-Info";
    payload: Directory
}
