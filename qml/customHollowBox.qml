// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customHollowBox

    function validateInt(test, minimum = 0){
        if (test === ""){return false}
        intTest = parseInt(test)
        if (isNaN(intTest)){return false}
        if (intTest < minimum){return false}
        return true
    }

    function validateFloat(test, minimum = 0.0){
        if (test === ""){return false}
        floatTest = parseFloat(test)
        if (isNaN(floatTest)){return false}
        if (floatTest < minimum){return false}
        return true
    }
    
    function validateInputs(){
        inputsValid = (validateInt(boxWidth) &&
                        validateInt(boxDepth) &&
                        validateInt(boxHeight) &&
                        validateFloat(boxWallWidth) &&
                        validateFloat(boxCeilingHeight))
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    property int boxWidth: 0
    property int boxDepth: 0
    property int boxHeight: 0
    property real boxWallWidth: 0.0
    property real boxCeilingHeight: 0.0

    property bool inputsValid: false

    Component.onCompleted: {
        boxWidth = manager.hollow_box_width
        boxDepth = manager.hollow_box_depth
        boxHeight = manager.hollow_box_height
        boxWallWidth = manager.hollow_box_wall_width
        boxCeilingHeight = manager.hollow_box_ceiling_height
    }

    title: catalog.i18nc("@window_title", "Custom Hollow Box")

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent

        GridLayout {
            id: settingsControls
            anchors.fill: parent
            columns: 2
            spacing: UM.Theme.getSize("default_margin").width

            UM.Label{
                id: totalWidthLabel
                text: catalog.i18nc("custom_hollow_box:total_width", "Total Width")
            }

            UM.TextFieldWithUnit{
                id: totalWidth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxWidth
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    validateInputs()
                }
            }

            UM.Label{
                id: totalDepthLabel
                text: catalog.i18nc("custom_hollow_box:total_depth", "Total Depth")
            }

            UM.TextFieldWithUnit{
                id: totalDepth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxDepth
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    validateInputs()
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_hollow_box:total_height", "Total Height")
            }

            UM.TextFieldWithUnit{
                id: totalHeight
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxHeight
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    validateInputs()
                }
            }

            UM.Label{
                id: wallWidthLabel
                text: catalog.i18nc("custom_hollow_box:wall_width", "Wall Width")
            }

            UM.TextFieldWithUnit{
                id: wallWidth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxWallWidth
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    validateInputs()
                }
            }

            UM.Label{
                id: roofThicknessLabel
                text: catalog.i18nc("custom_hollow_box:roof_thickness", "Roof Thickness")
            }

            UM.TextFieldWithUnit{
                id: roofThickness
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxCeilingHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    validateInputs()
                }
            }
        }

        // Buttons
        rightButtons: [
            Cura.SecondaryButton{
                id: cancelButton
                text: catalog.i18nc("custom_hollow_box_cancel", "Cancel")

                onClicked:{
                    customHollowBox.reject()
                }
            },
            Cura.PrimaryButton{
                id:okButton
                text: catalog.i18nc("custom_hollow_box_ok", "OK")
                enabled: inputsValid

                onClicked: {
                    manager.hollow_box_width = parseInt(boxWidth)
                    manager.hollow_box_depth = parseInt(boxDepth)
                    manager.hollow_box_height = parseInt(boxHeight)
                    manager.hollow_box_wall_width = parseFloat(boxWallWidth)
                    manager.hollow_box_ceiling_height = parseFloat(boxCeilingHeight)

                    manager.make_custom_hollow_box()
                    
                    customHollowBox.accept()
                }
            }
        ]
    }
}