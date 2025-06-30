
export type GitSource = {
    type: "git",
    git: string,
    subdirectory: string,
    branch: string
}

export type PipSource = {
    type: "pip",
    package: string
}

export type PathSource = {
    type: "path",
    path: string,
    editable: boolean
}

export type DependencySource = GitSource | PipSource | PathSource

export type Dependency = {
    source: DependencySource
    name: string,
    fullname: string,
}
