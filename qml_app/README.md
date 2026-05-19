# qml_app - BulletProve Qt Quick UI

Minimal QML/C++ application that targets both desktop and mobile from a
single codebase.

## Structure

| File | Purpose |
|---|---|
| `CMakeLists.txt` | Qt6 CMake build; QML module URI is `BulletProve` |
| `main.cpp` | Selects a platform-native Controls style, loads the QML module |
| `Main.qml` | Shared UI: title, image placeholder, Load button |

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

## Build

### Desktop

```bash
cmake -B build -S . -DCMAKE_PREFIX_PATH=/home/yyk/Qt/6.8.1/gcc_64
cmake --build build
./build/BulletProveApp
```

### Android

```bash
cmake -B build-android -S . \
  -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a \
  -DCMAKE_PREFIX_PATH=/path/to/Qt6/android_arm64_v8a
cmake --build build-android
```

Android packaging (APK/AAB) is handled by Qt Creator or
`androiddeployqt` from the Qt installation.
