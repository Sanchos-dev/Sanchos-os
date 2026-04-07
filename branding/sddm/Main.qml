import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    width: 1920
    height: 1080
    color: "#0d1017"

    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        source: "../wallpapers/sanchos-default.svg"
    }

    Rectangle {
        anchors.centerIn: parent
        width: 480
        height: 360
        radius: 20
        color: "#111724"
        opacity: 0.9
        border.color: "#2d3b57"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 18

            Label {
                text: "sanchos-os"
                color: "#f3f6fb"
                font.pixelSize: 28
                font.bold: true
            }

            Label {
                text: "Desktop platform with native virtualization"
                color: "#a9b7cb"
                wrapMode: Text.WordWrap
                font.pixelSize: 15
            }

            TextField {
                placeholderText: "Username"
            }

            TextField {
                placeholderText: "Password"
                echoMode: TextInput.Password
            }

            Button {
                text: "Sign in"
                Layout.fillWidth: true
            }
        }
    }
}
