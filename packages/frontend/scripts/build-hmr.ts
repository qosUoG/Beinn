import { watch } from "fs";
import { $ } from "bun";


const watcher = watch(".", { recursive: true }, async (event, filename) => {

    if (filename?.startsWith("src"))
        await $`bun run build`;
});

process.on("SIGINT", () => {
    // close watcher when Ctrl-C is pressed
    console.log("Closing watcher...");
    watcher.close();

    process.exit(0);
});