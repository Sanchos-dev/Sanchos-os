import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    width: 1920
    height: 1080
    color: "#120d18"

    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        source: "/usr/share/backgrounds/sanchos-os/purple/purple0.png"
        opacity: 0.68
    }

    Rectangle { anchors.fill: parent; color: "#120d18"; opacity: 0.28 }

    Rectangle {
        width: 620; height: 480; radius: 30
        anchors.centerIn: parent
        color: "#1d1626dd"
        border.width: 1
        border.color: "#5e4790"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 36
            spacing: 16

            Label { text: "sanchos-os"; color: "#f5f1ff"; font.pixelSize: 34; font.bold: true }
            Label { text: "warm login shell"; color: "#ccbfe7"; font.pixelSize: 16 }

            TextField {
                id: username
                Layout.fillWidth: true
                implicitHeight: 44
                placeholderText: "Username"
                text: ""
            }

            TextField {
                id: password
                Layout.fillWidth: true
                implicitHeight: 44
                echoMode: TextInput.Password
                placeholderText: "Password"
                focus: true
                onAccepted: sddm.login(username.text, text, 0)
            }

            Button {
                text: "Sign in"
                Layout.fillWidth: true
                implicitHeight: 46
                onClicked: sddm.login(username.text, password.text, 0)
            }

            Item { Layout.fillHeight: true }

            RowLayout {
                Layout.fillWidth: true
                Label { text: Qt.formatDateTime(new Date(), "ddd dd MMM yyyy  •  hh:mm"); color: "#ccbfe7"; font.pixelSize: 14 }
                Item { Layout.fillWidth: true }
                Button { text: "Restart"; onClicked: sddm.reboot() }
                Button { text: "Shutdown"; onClicked: sddm.powerOff() }
            }
        }
    }
}
