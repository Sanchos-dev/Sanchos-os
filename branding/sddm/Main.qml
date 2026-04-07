import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    width: 1920
    height: 1080
    color: "#120f18"

    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        source: "/usr/share/backgrounds/sanchos-os/purple/purple0.png"
        opacity: 0.55
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#120f18" }
            GradientStop { position: 1.0; color: "#1b1324" }
        }
        opacity: 0.82
    }

    Rectangle {
        anchors.centerIn: parent
        width: 520
        height: 390
        radius: 28
        color: "#1d1727"
        opacity: 0.94
        border.color: "#4e3770"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 34
            spacing: 18

            Label {
                text: "sanchos-os"
                color: "#f6f2ff"
                font.pixelSize: 30
                font.bold: true
            }

            Label {
                text: "Soft purple desktop, native virtualization and a warmer shell."
                color: "#cdbfe3"
                wrapMode: Text.WordWrap
                font.pixelSize: 15
            }

            Rectangle {
                Layout.fillWidth: true
                height: 44
                radius: 14
                color: "#2a2136"
                TextField {
                    anchors.fill: parent
                    anchors.margins: 10
                    placeholderText: "Username"
                    color: "#f6f2ff"
                    background: null
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 44
                radius: 14
                color: "#2a2136"
                TextField {
                    anchors.fill: parent
                    anchors.margins: 10
                    placeholderText: "Password"
                    echoMode: TextInput.Password
                    color: "#f6f2ff"
                    background: null
                }
            }

            Button {
                text: "Sign in"
                Layout.fillWidth: true
            }
        }
    }
}
