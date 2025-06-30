
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

export type Dependency_NotInstalled = {
    installed: false
    source: DependencySource
}

export type Dependency_Installed = {
    installed: true
    source: DependencySource


    name: string,
    fullname: string,
}

export type Dependency = Dependency_Installed | Dependency_NotInstalled