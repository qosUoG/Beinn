
// import { access, constants, readdir } from "node:fs/promises";


// export async function getDirectoryInfo(path: string) {

//     const files = await readdir(path, { recursive: true, withFileTypes: true })

//     let root: Directory = {
//         files: [],
//         dirs: {}
//     }

//     for (const dirent of files) {

//         // put file in root.files directly
//         if (dirent.parentPath === path && !dirent.isDirectory()) {
//             root.files.push(dirent.name)
//             continue
//         }

//         // split recursed path, delete first "" entry
//         let p = dirent.parentPath.replace(path, "").split('/').toSpliced(0, 1)


//         let walk = root
//         while (p.length > 0) {
//             if (walk.dirs[p[0]] === undefined)
//                 walk.dirs[p[0]] = { files: [], dirs: {} }

//             walk = walk.dirs[p[0]]
//             p.shift()
//         }

//         if (dirent.isDirectory()) {
//             walk.dirs[dirent.name] = {
//                 files: [],
//                 dirs: {}
//             }
//         } else {
//             walk.files.push(dirent.name)
//         }
//     }


//     return root

// }

