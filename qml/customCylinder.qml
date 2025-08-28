// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customCylinder

    function validateInt(test, minimum = 0, maximum = Infinity){
        if (test === ""){return false}
        let intTest = parseInt(test)
        if (isNaN(intTest)){return false}
        if (intTest < minimum){return false}
        if (intTest > maximum){return false}
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
        let diameterValid = true
        let heightValid = true
        let segmentsValid = true
        if (!validateFloat(cylinderDiameter, 0.1)){
            diameterValid = false;
            message += catalog.i18nc("@error:diameter_invalid", "Diameter must be 0.1 or higher.<br>");
        }

        if (!validateFloat(cylinderHeight, 0.1)){
            heightValid = false;
            message += catalog.i18nc("@error:height_invalid", "Height must be 0.1 or higher<br>");
        }

        if (!validateInt(cylinderSegments, 3, 7200)){
            segmentsValid = false;
            message += catalog.i18nc("@error:segments_invalid", "Due to limitations in Euclidean geometry and processing power, segments must be between 3 and 7200.<br>")
        }
      
        // Global property which controls "OK" button and ability to accept dialog with enter key
        inputsValid = (diameterValid && heightValid && segmentsValid)
        // Global property which displays error message (duh)
        error_message = message

        // Set background for each box
        diameterField.background.color = getBackgroundColour(diameterValid)
        heightField.background.color = getBackgroundColour(heightValid)
        segmentsField.background.color = getBackgroundColour(segmentsValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first third is an int and the rest are reals. But I have no shortage
    of validation and never do maths with them here so binding strings is handy. */
    property string cylinderDiameter: "0"
    property string cylinderHeight: "0"
    property string cylinderSegments: "0"

    property bool inputsValid: false
    property string error_message: ""

    Component.onCompleted: {
        cylinderDiameter = String(manager.custom_cylinder_diameter)
        cylinderHeight = String(manager.custom_cylinder_height)
        cylinderSegments = String(manager.custom_cylinder_segments)
        Qt.callLater(validateInputs)
    }

    title: catalog.i18nc("@window_title", "Custom Cylinder")
    buttonSpacing: UM.Theme.getSize("default_margin").width
    
    minimumWidth: Math.max((mainLayout.Layout.minimumWidth + 3 * UM.Theme.getSize("default_margin").width),
        (okButton.width + cancelButton.width + 4 * UM.Theme.getSize("default_margin").width))
    maximumWidth: minimumWidth
    width: minimumWidth
    minimumHeight: mainLayout.Layout.minimumHeight + (3 * UM.Theme.getSize("default_margin").height) + okButton.height + UM.Theme.getSize("default_lining").height + 20
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
                id: diameterLabel
                text: catalog.i18nc("custom_cylinder:diameter", "Diameter")
            }

            UM.TextFieldWithUnit{
                id: diameterField
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: cylinderDiameter
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    cylinderDiameter = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: heightLabel
                text: catalog.i18nc("custom_cylinder:height", "Height")
            }

            UM.TextFieldWithUnit{
                id: heightField
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: cylinderHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    cylinderHeight = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: segmentsLabel
                text: catalog.i18nc("custom_cylinder:segments", "Segments (sides)")
            }

            UM.TextFieldWithUnit{
                id: segmentsField
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: ""
                text: cylinderSegments
                validator: IntValidator {
                    bottom: 3
                    top: 7200
                }
                onTextChanged: {
                    cylinderSegments = text
                    Qt.callLater(validateInputs)
                }
            }
        }
        UM.Label{
            Layout.fillWidth: true
            id: error_text
            text: customCylinder.error_message
            color: UM.Theme.getColor("error")
            wrapMode: TextInput.Wrap
        }
    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_cylinder_cancel", "Cancel")

            onClicked:{
                customCylinder.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_cylinder_ok", "OK")
            enabled: customCylinder.inputsValid

            onClicked: {
                customCylinder.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.custom_cylinder_diameter = parseFloat(cylinderDiameter)
        manager.custom_cylinder_height = parseFloat(cylinderHeight)
        manager.custom_cylinder_segments = parseInt(cylinderSegments)

        manager.make_custom_cylinder()
        customCylinder.close()
    }
}