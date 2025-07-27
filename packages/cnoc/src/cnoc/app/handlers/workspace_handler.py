import importlib
import inspect
import json
import pkgutil
from struct import pack
from typing import TypedDict
import warnings

# from ...public.params import ParamModels2Params

# from ..state.state import State

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection

commands = {}

escapes = [
    "__future__",
    "__hello__",
    "__phello__",
    "_android_support",
    "_collections_abc",
    "_colorize",
    "_compression",
    "_ios_support",
    "_markupbase",
    "_py_abc",
    "_pydatetime",
    "_pydecimal",
    "_pyio",
    "_pyrepl",
    "_sitebuiltins",
    "_strptime",
    "_threading_local",
    "_weakrefset",
    "abc",
    "argparse",
    "ast",
    "asyncio",
    "bdb",
    "bz2",
    "cProfile",
    "calendar",
    "cmd",
    "code",
    "codecs",
    "codeop",
    "collections",
    "compileall",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "copyreg",
    "csv",
    "ctypes",
    "curses",
    "dataclasses",
    "datetime",
    "dbm",
    "decimal",
    "difflib",
    "dis",
    "doctest",
    "email",
    "encodings",
    "ensurepip",
    "enum",
    "filecmp",
    "fileinput",
    "fractions",
    "ftplib",
    "functools",
    "genericpath",
    "getopt",
    "getpass",
    "gettext",
    "glob",
    "graphlib",
    "gzip",
    "hashlib",
    "hmac",
    "html",
    "http",
    "idlelib",
    "imaplib",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "json",
    "locale",
    "logging",
    "lzma",
    "mailbox",
    "mimetypes",
    "modulefinder",
    "multiprocessing",
    "netrc",
    "ntpath",
    "numbers",
    "operator",
    "optparse",
    "os",
    "pathlib",
    "pdb",
    "pickle",
    "pickletools",
    "pkgutil",
    "platform",
    "plistlib",
    "poplib",
    "posixpath",
    "pprint",
    "profile",
    "pstats",
    "py_compile",
    "pyclbr",
    "pydoc",
    "queue",
    "random",
    "re",
    "reprlib",
    "rlcompleter",
    "runpy",
    "sched",
    "secrets",
    "selectors",
    "shelve",
    "shlex",
    "shutil",
    "signal",
    "site",
    "smtplib",
    "socket",
    "socketserver",
    "sqlite3",
    "sre_compile",
    "sre_constants",
    "sre_parse",
    "ssl",
    "stat",
    "statistics",
    "string",
    "struct",
    "subprocess",
    "symtable",
    "tabnanny",
    "tarfile",
    "tempfile",
    "textwrap",
    "threading",
    "timeit",
    "tkinter",
    "tokenize",
    "tomllib",
    "trace",
    "traceback",
    "tracemalloc",
    "tty",
    "turtle",
    "turtledemo",
    "types",
    "typing",
    "unittest",
    "urllib",
    "uuid",
    "venv",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "wsgiref",
    "xml",
    "xmlrpc",
    "zipapp",
    "zipfile",
    "zipimport",
    "zoneinfo",
    "_virtualenv",
    "_yaml",
    "aiosqlite",
    "annotated_types",
    "anyio",
    "click",
    "dateutil",
    "dns",
    "dotenv",
    "email_validator",
    "fastapi",
    "fastapi_cli",
    "h11",
    "httpcore",
    "httptools",
    "httpx",
    "idna",
    "jinja2",
    "markdown_it",
    "markupsafe",
    "mdurl",
    "multipart",
    "numpy",
    "pandas",
    "pydantic",
    "pydantic_core",
    "pygments",
    "python_multipart",
    "pytz",
    "rich",
    "rich_toolkit",
    "shellingham",
    "six",
    "sniffio",
    "starlette",
    "typer",
    "typing_extensions",
    "typing_inspection",
    "uvicorn",
    "uvloop",
    "watchfiles",
    "websockets",
    "yaml",
]


def eeImports[T: type[ExperimentABC] | type[EquipmentABC]](eetype: T):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    res: dict[T, ReturnType] = {}
    temp_res = []

    warnings.filterwarnings("ignore")

    # Check all possible paths
    for package in pkgutil.walk_packages():
        # Exclude these

        if package.name.startswith(tuple(escapes)):
            continue
        if package.name.endswith("__main__"):
            continue
        if package.name.startswith("xkcd"):
            print(f"Skipping {package.name} as it starts with xkcd")
            continue
        try:
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(package.name), inspect.isclass
            ):
                # print(package.name)
                if package.name not in temp_res:
                    temp_res.append(package.name)

                # if not issubclass(clsT, eetype) or clsT is eetype:
                #     continue

                # if clsT not in res:

                # res[clsT] = {"modules": [package.name], "cls": cls}
                # else:

                # res[clsT]["modules"].append(package.name)

        except Exception:
            pass

    warnings.filterwarnings("default")

    # return list(res.keys())
    return temp_res


async def workspaceHandler(ws: ServerConnection):
    async for message in ws:
        req = json.loads(message)
        command: str = req["command"]
        match command:
            case "equipment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "equipment:imports",
                            "value": eeImports(EquipmentABC),
                        }
                    )
                )
                break
            case "experiment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "experiment:imports",
                            "value": eeImports(ExperimentABC),
                        }
                    )
                )
                break
            case "equipment:create":
                # State.create("equipment", req["id"], req["module"], req["cls"])
                pass
            case "experiment:create":
                # State.create("experiment", req["id"], req["module"], req["cls"])
                pass
            # case "set_params":
            #     State.setParams(req["id"], ParamModels2Params(req["params"]))
            #     break
