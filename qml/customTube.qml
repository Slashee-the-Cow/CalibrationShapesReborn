// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customTube

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
        let outerDiameterValid = true
        let innerDiameterValid = true
        let heightValid = true
        if (!validateFloat(tubeOuterDiameter, 0.1)){
            outerDiameterValid = false;
            message += catalog.i18nc("@error:outer_diameter_invalid", "Outer diameter must be 0.1 or higher.<br>");
        }

        if (!validateFloat(tubeInnerDiameter, 0.1)){
            innerDiameterValid = false;
            message += catalog.i18nc("@error:inner_diameter_invalid", "Inner diameter must be 0.1 or higher.<br>");
        }

        if (!validateFloat(tubeHeight, 0.1)){
            heightValid = false;
            message += catalog.i18nc("@error:height_invalid", "Height must be 0.1 or higher.<br>");
        }

        // Test fields for inter-dependencies
        let outer = null
        let inner = null
        if (outerDiameterValid) {outer = parseFloat(tubeOuterDiameter)}
        if (innerDiameterValid) {inner = parseFloat(tubeInnerDiameter)}

        if (outer && inner){
            if (outer <= inner){
                message += catalog.i18nc("@error:diameter_overlap", "Outer diameter must be greater than inner diameter.<br>");
                outerDiameterValid = false
                innerDiameterValid = false
            }
        }

        // Global property which controls "OK" button and ability to accept dialog with enter key
        inputsValid = (outerDiameterValid && innerDiameterValid && heightValid)
        // Global property which displays error message (duh)
        error_message = message

        // Set background for each box
        outerDiameter.background.color = getBackgroundColour(outerDiameterValid)
        innerDiameter.background.color = getBackgroundColour(innerDiameterValid)
        totalHeight.background.color = getBackgroundColour(heightValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first third is an int and the rest are reals. But I have no shortage
    of validation and never do maths with them here so binding strings is handy. */
    property string tubeOuterDiameter: "0"
    property string tubeInnerDiameter: "0"
    property string tubeHeight: "0"

    property bool inputsValid: false
    property string error_message: ""

    Component.onCompleted: {
        tubeOuterDiameter = String(manager.custom_tube_outer_diameter)
        tubeInnerDiameter = String(manager.custom_tube_inner_diameter)
        tubeHeight = String(manager.custom_tube_height)
        Qt.callLater(validateInputs)
    }

    title: catalog.i18nc("@window_title", "Custom Bridging Tube")
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
                id: outerDiameterLabel
                text: catalog.i18nc("custom_custom_tube:outer_diameter", "Outer Diameter")
            }

            UM.TextFieldWithUnit{
                id: outerDiameter
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: tubeOuterDiameter
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    tubeOuterDiameter = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: innerDiameterLabel
                text: catalog.i18nc("custom_custom_tube:inner_diameter", "Inner Diameter")
            }

            UM.TextFieldWithUnit{
                id: innerDiameter
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: tubeInnerDiameter
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    tubeInnerDiameter = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_custom_tube:total_height", "Total Height")
            }

            UM.TextFieldWithUnit{
                id: totalHeight
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: tubeHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    tubeHeight = text
                    Qt.callLater(validateInputs)
                }
            }
        }
        UM.Label{
            Layout.fillWidth: true
            id: error_text
            text: customTube.error_message
            color: UM.Theme.getColor("error")
            wrapMode: TextInput.Wrap
        }
    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_custom_tube_cancel", "Cancel")

            onClicked:{
                customTube.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_custom_tube_ok", "OK")
            enabled: customTube.inputsValid

            onClicked: {
                customTube.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.custom_tube_outer_diameter = parseFloat(tubeOuterDiameter)
        manager.custom_tube_inner_diameter = parseFloat(tubeInnerDiameter)
        manager.custom_tube_height = parseFloat(tubeHeight)

        manager.make_custom_tube()
        customTube.close()
    }
}