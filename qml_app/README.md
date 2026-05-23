# qml_app - BulletProve Qt Quick UI

Minimal QML/C++ application that targets both desktop and mobile from a
single codebase.

## Structure

| File | Purpose |
|---|---|
| `CMakeLists.txt` | Qt6 CMake build; QML module URI is `BulletProve` |
| `main.cpp` | Selects a platform-native Controls style, loads the QML module |
| `Main.qml` | Shared UI: title, image area with file dialog, Load button |
| `CMakePresets.json` | Shared configure/build presets (tracked in git) |
| `CMakeUserPresets.json` | Machine-specific presets that inherit from the shared ones |

## Platform styles

`main.cpp` picks a Qt Quick Controls style at compile time:

| Platform | Style |
|---|---|
| Android | Material |
| iOS | iOS |
| Desktop | Fusion |

The same `Main.qml` is used on all platforms unchanged. On mobile the OS
stretches the `ApplicationWindow` to fill the screen automatically.

## Rendering backend (RHI)

Qt 6 uses an RHI (Rendering Hardware Interface) abstraction so the same
QML renders on top of OpenGL, Vulkan, Metal, or Direct3D 11. The default
backend is chosen by Qt per platform (OpenGL on Linux/Android, Metal on
macOS/iOS, Direct3D on Windows). Vulkan is not used by default; to opt in:

```cpp
// in main.cpp, before creating QQmlApplicationEngine
app.setAttribute(Qt::AA_UseVulkan);
```

Or switch at runtime without recompiling:

```bash
QSG_RHI_BACKEND=vulkan ./BulletProveApp
```

## Build with presets

All shared presets use `Ninja Multi-Config`, so each platform requires only
one configure step; Debug and Release are selected at build time.
`CMakeUserPresets.json` provides machine-local overrides (Qt path, NDK path).

### List available presets

```bash
cmake --list-presets        # configure presets
cmake --list-presets build  # build presets
```

### Desktop — kestrel (Qt 6.8, installed)

```bash
cmake --preset kestrel
cmake --build --preset kestrel-debug
cmake --build --preset kestrel-release
./build/kestrel/Debug/BulletProveApp
```

### Desktop — silvana (Qt 6.11, built from source)

```bash
cmake --preset silvana
cmake --build --preset silvana-debug
cmake --build --preset silvana-release
```

### Android — kestrel

```bash
cmake --preset kestrel-android-arm64
cmake --build --preset kestrel-android-arm64-debug
```

Android packaging (APK/AAB) is handled by Qt Creator or
`androiddeployqt` from the Qt installation.

### Windows Desktop — quagga (Visual Studio 17 2022)

```cmd
cmake --preset quagga
cmake --build --preset quagga-debug
cmake --build --preset quagga-release
```

Qt path is set to `E:/qt6/6.6.0/msvc2019_64` via `CMAKE_PREFIX_PATH:UNINITIALIZED`
(the `UNINITIALIZED` type prevents CMake from mangling the Windows path separators).

### Build without presets

```bash
cmake -B build -S . -DCMAKE_PREFIX_PATH=/home/yyk/Qt/6.8.1/gcc_64
cmake --build build
./build/BulletProveApp
```

or (in Windows)

    cmake -B build -S . -DCMAKE_PREFIX_PATH:UNINITIALIZED=E:/qt6/6.6.0/msvc2019_64
    cmake --build build
