import { $ } from "bun";

await $`bun build  --compile ./index.ts ./static/**/*.jss ./static/**/*.css    ./static/index.html --outfile qoslab`
