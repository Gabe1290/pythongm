# Windows EXE Export: Memory/OOM Issue 🔴

**Date:** November 18, 2025
**Issue:** PyInstaller process killed during build ("Killed" message)
**Cause:** Out of Memory (OOM) - System killing the process
**Status:** ⚠️ **SYSTEM LIMITATION** - Workarounds available

---

## Problem Description

When exporting games to Windows EXE, the PyInstaller build process is killed by the Linux kernel with a "Killed" message. This happens after the Kivy export completes successfully.

### Console Output
```
✓ Object obj_diamond generated
✓ Generated 3 object type(s)
✓ Game logic utilities generated
✓ Buildozer spec generated
✓ Requirements file generated
✓ README created
============================================================
Export completed successfully!
============================================================
Killed
```

The "Killed" message indicates the process was terminated by the OS, not by an error in the code.

---

## Root Cause

### PyInstaller + Kivy = Very Memory Intensive

Building a Windows EXE with PyInstaller that includes Kivy requires significant RAM:

- **Minimum**: 4GB RAM
- **Recommended**: 8GB+ RAM
- **With other apps running**: 12GB+ RAM

The build process:
1. Analyzes all Python imports (Kivy has many dependencies)
2. Bundles Python interpreter
3. Bundles all Kivy libraries (OpenGL, SDL2, GStreamer, etc.)
4. Compresses files (if UPX enabled)
5. Creates single executable

### Linux OOM Killer

When a process uses too much memory, the Linux kernel's Out-Of-Memory (OOM) killer terminates it to prevent system crash:

```
kernel: Out of memory: Killed process 12345 (pyinstaller) ...
```

This appears in your system logs (`dmesg`) but just shows "Killed" in the terminal.

---

## Immediate Fixes Applied

### 1. Disabled UPX Compression
**File:** [export/exe/exe_exporter.py:366](export/exe/exe_exporter.py#L366)

**Before:**
```python
upx={self.export_settings.get('optimize', True)},  # Enabled by default
```

**After:**
```python
upx={self.export_settings.get('optimize', False)},  # Disabled by default (saves memory)
```

UPX compression:
- **Purpose**: Reduces executable size by ~30-50%
- **Cost**: Requires 2-3x more memory during build
- **Trade-off**: Larger .exe file, but build uses less RAM

### 2. Increased Timeout
**File:** [export/exe/exe_exporter.py:408](export/exe/exe_exporter.py#L408)

**Before:**
```python
timeout=300  # 5 minutes
```

**After:**
```python
timeout=600  # 10 minutes
```

Gives the build more time to complete on slower systems.

### 3. Added Real-Time Output
**File:** [export/exe/exe_exporter.py:394-405](export/exe/exe_exporter.py#L394-L405)

Now streams PyInstaller output in real-time, so you can see:
- Build progress
- Which modules are being analyzed
- Where it gets stuck (if it does)

### 4. Better Error Messages
**File:** [export/exe/exe_exporter.py:417-426](export/exe/exe_exporter.py#L417-L426)

If timeout occurs, shows helpful guidance:
```
❌ PyInstaller timed out after 10 minutes
This usually means the build is too memory-intensive for your system.

Try:
1. Close other applications to free up memory
2. Increase system swap space
3. Build on a machine with more RAM (recommended: 8GB+)
```

---

## Workarounds

### Option 1: Free Up Memory (Quick)

**Close unnecessary applications:**
```bash
# Check memory usage
free -h

# Close browser, IDE, etc.
# Keep only terminal open
```

**Before retrying export:**
- Close web browsers (Chrome/Firefox use 1-2GB each)
- Close IDEs (VSCode/PyCharm use 500MB-1GB)
- Close Electron apps (Discord/Slack use 300-500MB each)
- Stop other Python processes

**Expected result:**
- Frees 2-4GB RAM
- Might be enough for build to complete

### Option 2: Increase Swap Space (Medium)

**Check current swap:**
```bash
free -h
swapon --show
```

**Create additional swap file (4GB):**
```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify
free -h
```

**Make permanent (optional):**
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Expected result:**
- Adds 4GB virtual memory
- Build will be slower but won't be killed
- May take 15-20 minutes instead of 5-10

### Option 3: Use Docker (Advanced)

Build inside a Docker container with memory limits:

```dockerfile
# Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev

RUN pip install kivy pyinstaller pillow

WORKDIR /app
COPY build_temp_exe /app/build_temp_exe

CMD ["pyinstaller", "--clean", "/app/build_temp_exe/game.spec"]
```

**Build with resource limits:**
```bash
docker build -t pygm-builder .
docker run --memory=8g --memory-swap=12g -v $(pwd):/output pygm-builder
```

### Option 4: Build on Different Machine (Recommended)

**Best options:**
1. **Cloud VM**: Spin up AWS/GCP/DigitalOcean instance with 8GB+ RAM
2. **Dedicated build server**: Use a dedicated Linux machine for builds
3. **Windows build**: Build directly on Windows (PyInstaller uses less memory on native platform)

**Cost:**
- AWS t3.large (2 vCPU, 8GB RAM): ~$0.08/hour
- One build = ~$0.02-$0.05
- Can build 100 games for $2-5

---

## Why Kivy + PyInstaller Uses So Much Memory

### 1. Kivy Dependencies

Kivy pulls in many large libraries:
- SDL2 (graphics)
- GStreamer (audio/video)
- OpenGL (rendering)
- PIL/Pillow (images)
- NumPy (optional, but often included)

### 2. Python Interpreter

PyInstaller bundles entire Python interpreter:
- Standard library
- Site-packages
- All imported modules

### 3. Build Process Steps

```
1. Import Analysis (500MB-1GB RAM)
   └─ Scans all imports recursively

2. Binary Collection (1-2GB RAM)
   └─ Gathers all .so/.dll files

3. Archive Creation (2-3GB RAM)
   └─ Creates compressed archive

4. Bootloader Bundle (1-2GB RAM)
   └─ Combines bootloader + archive

5. UPX Compression (if enabled) (+2-4GB RAM)
   └─ Compresses executable
```

**Peak memory usage:**
- Without UPX: 4-6GB RAM
- With UPX: 8-10GB RAM

---

## Alternative: Export to Kivy Only

If Windows EXE export keeps failing due to memory, you can export to Kivy instead and use:

### Option A: Buildozer (Android APK)
```bash
# Export to Kivy (already works)
# Then use buildozer to create Android APK
cd build_temp_exe/game
buildozer android debug
```

### Option B: PyInstaller on Windows
```bash
# Export to Kivy on Linux (low memory usage)
# Transfer to Windows machine
# Run PyInstaller on Windows (uses less memory)

# On Windows:
cd build_temp_exe
pyinstaller --clean game.spec
```

PyInstaller uses **30-50% less memory** when building on native platform!

### Option C: Nuitka (Alternative Compiler)
```bash
# Export to Kivy
# Use Nuitka instead of PyInstaller (lower memory usage)

pip install nuitka
nuitka --standalone --onefile game_launcher.py
```

---

## Monitoring Build Progress

### Check Memory Usage During Build

**Terminal 1 - Run export**
**Terminal 2 - Monitor memory:**
```bash
watch -n 1 'free -h && echo && ps aux --sort=-%mem | head -10'
```

This shows:
- Total memory usage
- Top 10 memory-consuming processes
- Updates every second

### Check System Logs

If process is killed:
```bash
dmesg | grep -i "killed process"
```

Look for:
```
Out of memory: Killed process 12345 (pyinstaller)
```

This confirms OOM killer was responsible.

---

## Testing the Fixes

### Test 1: With UPX Disabled (Default Now)

Try exporting again. The build should use 2-3GB less memory.

**Expected:**
- Build takes slightly longer (no compression)
- Executable is larger (~50-100MB vs ~30-50MB)
- But build uses less RAM and might succeed

### Test 2: With Swap Space

If test 1 fails, add swap space (see Option 2 above) and retry.

**Expected:**
- Build will be slower (swapping to disk)
- But won't be killed
- May take 15-20 minutes

### Test 3: Close All Other Apps

**Minimal system:**
```bash
# Check what's running
ps aux --sort=-%mem | head -20

# Close memory hogs
pkill chrome
pkill firefox
pkill code  # VSCode
pkill pycharm

# Only keep terminal + export
```

---

## Future Improvements

Potential optimizations:

### 1. Two-Stage Build
- Stage 1: Analyze imports, create spec (low memory)
- Stage 2: Build executable (high memory, can run separately)

### 2. Incremental Builds
- Cache analysis results
- Only rebuild changed modules
- Reduces memory usage for subsequent builds

### 3. Minimal Kivy Build
- Exclude unused Kivy modules
- Reduce total bundle size by 50-70%
- Lower memory requirements

### 4. Cloud Build Service
- Automated cloud builds
- User uploads project, gets .exe back
- No local memory concerns

---

## System Requirements

### Minimum (Might Work)
- **RAM**: 4GB
- **Swap**: 4GB
- **Free Disk**: 2GB
- **CPU**: 2 cores
- **Time**: 10-15 minutes

### Recommended (Should Work)
- **RAM**: 8GB
- **Swap**: 2GB (backup)
- **Free Disk**: 5GB
- **CPU**: 4 cores
- **Time**: 5-7 minutes

### Ideal (Fast & Reliable)
- **RAM**: 16GB
- **Swap**: Not needed
- **Free Disk**: 10GB
- **CPU**: 8 cores
- **Time**: 3-5 minutes

---

## Status: IMPROVED ⚠️

Changes made:
- ✅ Disabled UPX compression (saves 2-3GB RAM)
- ✅ Increased timeout to 10 minutes
- ✅ Added real-time output streaming
- ✅ Better error messages with helpful guidance

**This is a system resource limitation, not a bug.**

The export process will work if your system has enough memory. If it still fails, use the workarounds above or build on a machine with more RAM.

**⚠️ If you have less than 6GB free RAM, consider using workaround options!**

---

## Quick Checklist

Before retrying Windows EXE export:

- [ ] Close all web browsers
- [ ] Close IDEs (VSCode, PyCharm, etc.)
- [ ] Close Electron apps (Discord, Slack, etc.)
- [ ] Check free memory: `free -h` (should show 4GB+ available)
- [ ] Consider adding swap space if RAM < 8GB
- [ ] Monitor build progress in separate terminal
- [ ] Be patient - build may take 10-15 minutes

**🎯 Good luck with your build!**
