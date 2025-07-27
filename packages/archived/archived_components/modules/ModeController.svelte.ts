
export type AppMode = "Configuration" | "Runtime"
export const mode_controller: { mode: AppMode } = $state({ mode: "Configuration" })