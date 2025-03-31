// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customBox

    function validateInt(test, minimum = 0){
        if (test === ""){return false}
        let intTest = parseInt(test)
        if (isNaN(intTest)){return false}
        if (intTest < minimum){return false}
        return true
    }

    function validateFloat(test, minimum = 0.0){
        if (test === ""){return false}
        test = test.replace(",",".") // Use "correct" decimal separator
        let floatTest = parseFloat(test)
        if (isNaN(floatTest)){return false}
        if (floatTest < minimum){return false}
        return true
    }

    property var default_field_background: UM.Theme.getColor("detail_background")
    property var error_field_background: UM.Theme.getColor("setting_validation_error_background")

    function getBackgroundColour(valid){
        return valid ? default_field_background : error_field_background
    }
    
    function validateInputs(){
        let message = ""
        let widthValid = true
        let depthValid = true
        let heightValid = true
        if (!validateFloat(boxWidth, 0.1)){
            widthValid = false;
            message += catalog.i18nc("@error:width_invalid", "Width must be 0.1 or higher.<br>");
        }

        if (!validateFloat(boxDepth, 0.1)){
            depthValid = false;
            message += catalog.i18nc("@error:depth_invalid", "Depth must be 0.1 or higher.<br>");
        }

        if (!validateFloat(boxHeight, 0.1)){
            heightValid = false;
            message += catalog.i18nc("@error:height_invalid", "Height must be 0.1 or higher<br>");
        }
      
        // Global property which controls "OK" button and ability to accept dialog with enter key
        inputsValid = (widthValid && depthValid && heightValid)
        // Global property which displays error message (duh)
        error_message = message

        // Set background for each box
        totalWidth.background.color = getBackgroundColour(widthValid)
        totalDepth.background.color = getBackgroundColour(depthValid)
        totalHeight.background.color = getBackgroundColour(heightValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first third is an int and the rest are reals. But I have no shortage
    of validation and never do maths with them here so binding strings is handy. */
    property string boxWidth: "0"
    property string boxDepth: "0"
    property string boxHeight: "0"

    property bool inputsValid: false
    property string error_message: ""

    Component.onCompleted: {
        boxWidth = String(manager.custom_box_width)
        boxDepth = String(manager.custom_box_depth)
        boxHeight = String(manager.custom_box_height)
        Qt.callLater(validateInputs)
    }

    title: catalog.i18nc("@window_title", "Custom Box")
    buttonSpacing: UM.Theme.getSize("default_margin").width
    
    minimumWidth: Math.max((mainLayout.Layout.minimumWidth + 3 * UM.Theme.getSize("default_margin").width),
        (okButton.width + cancelButton.width + 4 * UM.Theme.getSize("default_margin").width))
    maximumWidth: minimumWidth
    width: minimumWidth
    minimumHeight: mainLayout.Layout.minimumHeight + (2 * UM.Theme.getSize("default_margin").height) + okButton.height + UM.Theme.getSize("default_lining").height + 20
    //minimumHeight: 300 * screenScaleFactor
    maximumHeight: minimumHeight
    height: minimumHeight

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent

        GridLayout {
            id: settingsControls
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop

            columns: 2
            columnSpacing: UM.Theme.getSize("default_margin").width
            rowSpacing: UM.Theme.getSize("default_margin").height

            UM.Label{
                id: totalWidthLabel
                text: catalog.i18nc("custom_box:width", "Width")
            }

            UM.TextFieldWithUnit{
                id: totalWidth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxWidth
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    boxWidth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalDepthLabel
                text: catalog.i18nc("custom_box:depth", "Depth")
            }

            UM.TextFieldWithUnit{
                id: totalDepth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxDepth
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    boxDepth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_box:total_height", "Height")
            }

            UM.TextFieldWithUnit{
                id: totalHeight
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    boxHeight = text
                    Qt.callLater(validateInputs)
                }
            }
        }
        UM.Label{
            Layout.fillWidth: true
            id: error_text
            text: customBox.error_message
            color: UM.Theme.getColor("error")
            wrapMode: TextInput.Wrap
        }
    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_box_cancel", "Cancel")

            onClicked:{
                customBox.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_box_ok", "OK")
            enabled: customBox.inputsValid

            onClicked: {
                customBox.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.custom_box_width = parseFloat(boxWidth)
        manager.custom_box_depth = parseFloat(boxDepth)
        manager.custom_box_height = parseFloat(boxHeight)

        manager.make_custom_box()
        customBox.close()
    }
}