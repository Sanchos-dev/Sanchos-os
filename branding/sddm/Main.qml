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
        opacity: 0.55
    }

    Rectangle { anchors.fill: parent; color: "#120d18"; opacity: 0.42 }

    Rectangle {
        width: 560; height: 460; radius: 30
        anchors.centerIn: parent
        color: "#1d1626dd"
        border.width: 1
        border.color: "#5e4790"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 34
            spacing: 16

            Label { text: "sanchos-os"; color: "#f5f1ff"; font.pixelSize: 34; font.bold: true }
            Label { text: "warm login shell"; color: "#ccbfe7"; font.pixelSize: 16 }

            ComboBox {
                id: userCombo
                model: userModel
                textRole: "name"
                Layout.fillWidth: true
                implicitHeight: 44
            }

            TextField {
                id: password
                Layout.fillWidth: true
                implicitHeight: 44
                echoMode: TextInput.Password
                placeholderText: "Password"
                focus: true
                onAccepted: sddm.login(userCombo.currentText, text, session.index)
            }

            ComboBox {
                id: session
                model: sessionModel
                textRole: "name"
                Layout.fillWidth: true
                implicitHeight: 40
            }

            Button {
                text: "Sign in"
                Layout.fillWidth: true
                implicitHeight: 46
                onClicked: sddm.login(userCombo.currentText, password.text, session.index)
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
