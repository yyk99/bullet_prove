#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    // Pick a platform-native style; falls back to "Basic" if not available.
#if defined(Q_OS_ANDROID)
    QQuickStyle::setStyle(QStringLiteral("Material"));
#elif defined(Q_OS_IOS)
    QQuickStyle::setStyle(QStringLiteral("iOS"));
#else
    QQuickStyle::setStyle(QStringLiteral("Fusion"));
#endif

    QQmlApplicationEngine engine;

    // objectCreationFailed is emitted synchronously when the root component
    // cannot be created (QML syntax error, missing import, missing type, etc.).
    // QML engine already prints the individual errors to stderr; we add a
    // summary with actionable hints so the cause is obvious at a glance.
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() {
            qCritical("\n"
                      "Fatal: QML root object could not be created.\n"
                      "Likely causes:\n"
                      "  - QML syntax error in Main.qml (see errors above)\n"
                      "  - 'BulletProve' module not found on the QML import path\n"
                      "  - Qt Quick Controls or QuickDialogs2 libraries missing\n"
                      "Tip: set QML_IMPORT_TRACE=1 to trace import resolution.");
            QCoreApplication::exit(-1);
        },
        Qt::DirectConnection);

    engine.loadFromModule("BulletProve", "Main");

    return engine.rootObjects().isEmpty() ? -1 : app.exec();
}
