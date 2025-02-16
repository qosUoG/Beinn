export const compileWorkerScript = (workerFunction: Function) => {
    //This stringifies the whole function
    let codeToString = workerFunction.toString();
    //This brings out the code in the bracket in string
    let mainCode = codeToString.substring(codeToString.indexOf('{') + 1, codeToString.lastIndexOf('}'));
    //convert the code into a raw data
    let blob = new Blob([mainCode], { type: 'application/javascript' });
    //A url is made out of the blob object and we're good to go
    return URL.createObjectURL(blob);
}