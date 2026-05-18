import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// On mobile the OS stretches this window to fill the screen.
// On desktop it opens as a fixed 400x640 window.
ApplicationWindow {
    id: window
    visible: true
    width: 400
    height: 640
    title: qsTr("Bullet Prove")

    ColumnLayout {
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            topMargin: 56
        }
        spacing: 20

        Label {
            text: qsTr("Bullet Prove")
            font.pixelSize: 30
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: qsTr("Target Shooting Analyzer")
            font.pixelSize: 14
            color: palette.mid
            Layout.alignment: Qt.AlignHCenter
        }

        // Placeholder target image area
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 16
            width: 260
            height: 260
            color: palette.alternateBase
            border.color: palette.mid
            border.width: 1
            radius: 4

            Label {
                anchors.centerIn: parent
                text: qsTr("No image loaded")
                color: palette.mid
            }
        }

        Button {
            text: qsTr("Load Image")
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 8
            Layout.minimumWidth: 200
            Layout.minimumHeight: 48
            onClicked: statusLabel.text = qsTr("(image loading not yet implemented)")
        }

        Label {
            id: statusLabel
            text: ""
            color: palette.mid
            font.pixelSize: 12
            Layout.alignment: Qt.AlignHCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
