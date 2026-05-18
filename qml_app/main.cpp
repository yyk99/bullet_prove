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
    engine.loadFromModule("BulletProveApp", "Main");

    return engine.rootObjects().isEmpty() ? -1 : app.exec();
}
