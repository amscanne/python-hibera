"""
    A simple wrapper around the Hibera tool.

    All commands are exposed as functions, with the appropriate return type.

    You pass position arguments are positional arguments in python.

    You can pass options as keyword arguments in python.

    Global keyword arguments:
        api - The API address.
        auth - The authentication token.
        delay - The general delay.

    Special keyword arguments:
        stdin - The stdin file or data.
        stdout - The stdout file or data.

    For example:

        list()

        remove(key)

        get(key, api=api)

        run(key, start="start command", limit=5)
"""

RAW = 0
LIST = 1
JSON = 2
BOOL = 3

COMMANDS = [
    ("nodes", LIST),
    ("active", LIST),
    ("info", JSON),
    ("activate", BOOL),
    ("deactivate", BOOL),
    ("tokens", LIST),
    ("access", JSON),
    ("grant", BOOL),
    ("revoke", BOOL),
    ("run", BOOL),
    ("members", LIST),
    ("in", RAW),
    ("out", RAW),
    ("list", LIST),
    ("get", RAW),
    ("set", BOOL),
    ("remove", BOOL),
    ("sync", BOOL),
    ("watch", BOOL),
    ("fire", BOOL),
]

def _exec(command, *args, **kwargs):
    cmd_args = ["hibera", command]
    for (name, value) in kwargs.items():
        cmd_args.append("-%s" % name)
        if isinstance(value, list):
            cmd_args.append(",".join(value))
        else:
            cmd_args.append(str(value))
    cmd_args.extend(args)

    def _find_file(name):
        if isinstance(kwargs.get(name), file):
            return kwargs.get(name)
        else:
            return subprocess.PIPE
    def _find_data(name):
        if not isinstance(kwargs.get(name), file):
            return kwargs.get(name)
        else:
            return None

    import subprocess
    proc = subprocess.Popen(
        cmd_args,
        close_fds=True,
        stdin=_find_file("stdin"),
        stdout=_find_file("stdout"),
        stderr=_find_file("stderr"))

    (stdout, stderr) = proc.communicate(_find_data("stdin"))
    if proc.returncode != 0:
        raise Exception(stderr)
    else:
        return stdout

for (command, data_type) in COMMANDS:
    def _gen_fn(command, data_type):
        def _fn(*args, **kwargs):
            if data_type == RAW:
                return _exec(command, *args, **kwargs)
            elif data_type == LIST:
                res = _exec(command, *args, **kwargs)
                return [line for line in res.split("\n") if line]
            elif data_type == JSON:
                import json
                return json.loads(_exec(command, *args, **kwargs))
            elif data_type == BOOL:
                try:
                    _exec(command, *args, **kwargs)
                    return True
                except:
                    return False
        _fn.__name__ = command
        return _fn
    globals()[command] = _gen_fn(command, data_type)
