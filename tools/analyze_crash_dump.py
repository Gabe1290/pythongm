#!/usr/bin/env python3
"""Say where a Windows ``python.exe`` crash dump crashed.

Written for the intermittent "Windows fatal exception: access violation" that
kills a full pytest run inside a QtWebEngine test (docs/OPEN_WORK_2026-10-29.md,
A1). Python's faulthandler only shows the Python frame that was running; the dump
shows which *native* library crashed and the chain of libraries that called it.

    py -3.12 -m pip install minidump        # not a project requirement
    py -3.12 tools/analyze_crash_dump.py            # newest dump in %LOCALAPPDATA%\\CrashDumps
    py -3.12 tools/analyze_crash_dump.py path\\to\\python.exe.1234.dmp

Output: the exception code, the faulting module and its offset (the same offset
in the same DLL build is the same bug -- three October 1 dumps all say
``Qt6Quick.dll + 0x11593b``), and the sequence of modules found on the crashing
thread's stack, innermost first. It reads the stack for return addresses
without symbols, so treat the chain as a hint, not a backtrace.
"""
import glob
import os
import struct
import sys

OS_DLLS = {"kernelbase.dll", "kernel32.dll", "ntdll.dll"}   # return addresses of no interest


def newest_dump():
    folder = os.path.expandvars(r"%LOCALAPPDATA%\CrashDumps")
    dumps = glob.glob(os.path.join(folder, "python.exe.*.dmp"))
    if not dumps:
        sys.exit(f"no python.exe dumps in {folder}")
    return max(dumps, key=os.path.getmtime)


def analyse(path):
    from minidump.minidumpfile import MinidumpFile
    dump = MinidumpFile.parse(path)
    record = dump.exception.exception_records[0]
    rec = record.ExceptionRecord
    modules = sorted((m.baseaddress, m.baseaddress + m.size, os.path.basename(m.name))
                     for m in dump.modules.modules)

    def module_of(address):
        for low, high, name in modules:
            if low <= address < high:
                return name, address - low
        return None

    fault = module_of(rec.ExceptionAddress)
    thread = next(t for t in dump.threads.threads if t.ThreadId == record.ThreadId)
    stack = dump.get_reader().read(thread.Stack.StartOfMemoryRange, thread.Stack.DataSize)
    chain = []
    for i in range(0, len(stack) - 7, 8):
        hit = module_of(struct.unpack_from("<Q", stack, i)[0])
        if hit and hit[0].lower() not in OS_DLLS and (not chain or chain[-1] != hit[0]):
            chain.append(hit[0])
    return {
        "dump": path,
        "code": str(rec.ExceptionCode),
        "fault": f"{fault[0]} + {hex(fault[1])}" if fault else hex(rec.ExceptionAddress),
        "loaded": {"webengine": any("webengine" in m[2].lower() for m in modules),
                   "pygame": any("sdl2" in m[2].lower() or "pygame" in m[2].lower() for m in modules)},
        "chain": chain,
    }


def main(argv):
    try:
        import minidump  # noqa: F401
    except ImportError:
        sys.exit("needs the 'minidump' package: py -3.12 -m pip install minidump")
    path = argv[1] if len(argv) > 1 else newest_dump()
    info = analyse(path)
    print(f"dump:    {info['dump']}")
    print(f"code:    {info['code']}")
    print(f"fault:   {info['fault']}")
    print(f"loaded:  {info['loaded']}")
    print("callers: " + " -> ".join(info["chain"][:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
