import json
import typing


def dump(args: any) -> typing.Never:
    if isinstance(args, dict):
        print(json.dumps(args, indent=4))
        return

    print(args)


def dd(args: any) -> typing.Never:
    dump(args)
    exit()
