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
        opacity: status === Image.Ready ? 0.55 : 0.0
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#100d16" }
            GradientStop { position: 1.0; color: "#1b1324" }
        }
        opacity: 0.82
    }

    Rectangle {
        anchors.centerIn: parent
        width: 560
        height: 420
        radius: 32
        color: "#1a1524"
        opacity: 0.95
        border.width: 1
        border.color: "#5d42a6"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 36
            spacing: 18

            Label { text: "sanchos-os"; color: "#f6f2ff"; font.pixelSize: 32; font.bold: true }
            Label { text: "warm desktop · native virtualization · soft purple shell"; color: "#cdbfe3"; font.pixelSize: 14 }
            Rectangle { Layout.fillWidth: true; height: 48; radius: 16; color: "#272032" }
            Rectangle { Layout.fillWidth: true; height: 48; radius: 16; color: "#272032" }
            Rectangle { Layout.fillWidth: true; height: 50; radius: 16; color: "#8b5cf6"
                Label { anchors.centerIn: parent; text: "Sign in"; color: "white"; font.bold: true }
            }
        }
    }
}
