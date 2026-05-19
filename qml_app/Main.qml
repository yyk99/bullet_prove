import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

// On mobile the OS stretches this window to fill the screen.
// On desktop it opens as a fixed 400x640 window.
ApplicationWindow {
    id: window
    visible: true
    width: 400
    height: 640
    title: qsTr("Bullet Prove")

    FileDialog {
        id: fileDialog
        title: qsTr("Open target image")
        nameFilters: [
            qsTr("Image files (*.jpg *.jpeg *.png *.bmp *.heic)"),
            qsTr("All files (*)")
        ]
        onAccepted: targetImage.source = fileDialog.selectedFile
    }

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

        // Target image area
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 16
            width: 260
            height: 260
            color: palette.alternateBase
            border.color: palette.mid
            border.width: 1
            radius: 4
            clip: true

            Image {
                id: targetImage
                anchors.fill: parent
                anchors.margins: 4
                fillMode: Image.PreserveAspectFit
                visible: source != ""
            }

            Label {
                anchors.centerIn: parent
                text: qsTr("No image loaded")
                color: palette.mid
                visible: targetImage.source == ""
            }
        }

        Button {
            text: qsTr("Load Image")
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 8
            Layout.minimumWidth: 200
            Layout.minimumHeight: 48
            onClicked: fileDialog.open()
        }
    }
}
