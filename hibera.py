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
BOOL = 2
INDEXED = 3
REV = 128

COMMANDS = [
    ("run", BOOL),
    ("members", INDEXED|REV),
    ("in", RAW|REV),
    ("out", RAW|REV),
    ("list", LIST),
    ("get", RAW|REV),
    ("set", BOOL|REV),
    ("remove", BOOL|REV),
    ("sync", BOOL),
    ("watch", BOOL|REV),
    ("fire", BOOL|REV),
]

def _exec(command, *args, **kwargs):
    cmd_args = ["hibera", command]
    for (name, value) in kwargs.items():
        cmd_args.append("-%s" % name)
        if isinstance(value, type([])):
            cmd_args.append(",".join(value))
        else:
            cmd_args.append(str(value))
    cmd_args.extend(args)

    def _find_file(name):
        if isinstance(kwargs.get(name), file):
            return kwargs.get(name)
        else:
            return None
    def _find_data(name):
        if not isinstance(kwargs.get(name), file):
            return kwargs.get(name)
        else:
            return None

    # Print the command being executed.
    import sys
    sys.stderr.write("exec: %s\n" % " ".join(cmd_args))

    # Execute the command.
    import subprocess
    proc = subprocess.Popen(
        cmd_args,
        close_fds=True,
        stdin=_find_file("stdin") or subprocess.PIPE,
        stdout=_find_file("stdout") or subprocess.PIPE,
        stderr=_find_file("stderr") or subprocess.PIPE)

    (stdout, stderr) = proc.communicate(_find_data("stdin"))
    if proc.returncode != 0:
        raise Exception(stderr)
    else:
        return (stdout, stderr)

for (command, type_info) in COMMANDS:
    def _gen_fn(command, type_info):
        def _fn(*args, **kwargs):
            data_type = type_info & (~REV)
            with_rev = (type_info & REV != 0)
            if data_type == RAW:
                (rval, rev) = _exec(command, *args, **kwargs)
            elif data_type == LIST:
                (res, rev) = _exec(command, *args, **kwargs)
                rval = [line for line in res.split("\n") if line]
            elif data_type == INDEXED:
                (res, rev) = _exec(command, *args, **kwargs)
                rval = [line for line in res.split("\n") if line]
                rval = [int(rval[0]), rval[1:]]
            elif data_type == BOOL:
                try:
                    (_, rev) = _exec(command, *args, **kwargs)
                    rval = True
                except:
                    rval = False
            if with_rev:
                return (rval, int(rev))
            else:
                return rval
        _fn.__name__ = command
        return _fn
    globals()[command] = _gen_fn(command, type_info)
