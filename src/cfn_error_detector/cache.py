from os import environ

ENABLE_CACHE = environ.get("DEV_CACHE", None) == "1"

if ENABLE_CACHE:
    import os
    import sys

    import percache  # type: ignore

    Cache = percache.Cache(os.path.join(sys.path[0], ".percache"), livesync=True)

    print("!! Cache enabled !!", file=sys.stderr)
else:

    def Cache(x):  # type: ignore
        return x
