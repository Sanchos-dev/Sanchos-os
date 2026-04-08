import QtQuick 2.15
import QtQuick.Controls 2.15
import SddmComponents 2.0
Rectangle {
    width: 1920
    height: 1080
    color: "#130f1b"
    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        source: "/usr/share/backgrounds/sanchos-os/purple/purple0.png"
        opacity: 0.45
    }
    Rectangle { anchors.fill: parent; color: "#110d16"; opacity: 0.45 }
    Rectangle {
        width: 520; height: 430; radius: 28
        color: "#20172acc"; border.color: "#4f3c69"; border.width: 1
        anchors.centerIn: parent
        Column {
            anchors.fill: parent; anchors.margins: 34; spacing: 18
            Text { text: "sanchos-os"; color: "#f5f1ff"; font.pixelSize: 34; font.bold: true }
            Text { text: "Warm desktop shell"; color: "#c8bedf"; font.pixelSize: 16 }
            ComboBox { id: userCombo; model: userModel; textRole: "name"; width: parent.width; height: 44 }
            TextField { id: password; echoMode: TextInput.Password; width: parent.width; height: 44; placeholderText: "Password"; focus: true; onAccepted: sddm.login(userCombo.currentText, text, session.index) }
            Button { text: "Sign in"; width: parent.width; height: 46; onClicked: sddm.login(userCombo.currentText, password.text, session.index) }
            Row { spacing: 12; Button { text: "Sleep"; onClicked: sddm.suspend() } Button { text: "Restart"; onClicked: sddm.reboot() } Button { text: "Power off"; onClicked: sddm.powerOff() } }
        }
    }
}
