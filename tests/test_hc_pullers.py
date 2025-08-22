import sys

sys.path.append('OnePyFlow_ultra')

from isolated_modules.hctool_module import HCtoolPuller
from isolated_modules.phc_module import PHCpuller
from isolated_modules.backlog import BackLogPuller


def safe_call(name, fn):
    try:
        res = fn()
        print(f"{name}: ok, type={type(res).__name__}")
        if isinstance(res, list):
            print(f"{name}: len={len(res)}")
            if res and isinstance(res[0], dict):
                print(f"{name}: first_keys={list(res[0].keys())[:10]}")
        elif isinstance(res, dict):
            print(f"{name}: keys={list(res.keys())[:10]}")
        else:
            print(f"{name}: value={res}")
    except Exception as e:
        print(f"{name}: ERROR {e}")


if __name__ == "__main__":
    safe_call("HCtoolPuller", HCtoolPuller)
    safe_call("PHCpuller", PHCpuller)
    safe_call("BackLogPuller", BackLogPuller) 