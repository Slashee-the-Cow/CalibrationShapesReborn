// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customBridgingBox

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
        let wallValid = true
        let roofValid = true
        if (!validateInt(boxWidth, 1)){
            widthValid = false;
            message += catalog.i18nc("@error:width_invalid", "Box width must be a whole number 1 or higher.<br>");
        }

        if (!validateInt(boxDepth, 1)){
            depthValid = false;
            message += catalog.i18nc("@error:depth_invalid", "Box depth must be a whole number 1 or higher.<br>");
        }

        if (!validateInt(boxHeight, 1)){
            heightValid = false;
            message += catalog.i18nc("@error:height_invalid", "Box height must be a whole number 1 or higher.<br>");
        }

        if (!validateFloat(boxWallWidth, 0.1)){
            wallValid = false;
            message += catalog.i18nc("@error:wallWidth_invalid", "Box wall width must be 0.1 or higher.<br>");
        }

        if (!validateFloat(boxRoofHeight, 0.1)){
            roofValid = false;
            message += catalog.i18nc("@error:roofThickness_invalid", "Roof thickness must be 0.1 or higher.<br>");
        }
        
        // Test fields for inter-dependencies
        let width = null
        let depth = null
        let height = null
        let wall = null
        let roof = null
        if (widthValid) {width = parseInt(boxWidth)}
        if (depthValid) {depth = parseInt(boxDepth)}
        if (heightValid) {height = parseInt(boxHeight)}
        if (wallValid) {wall = parseFloat(boxWallWidth)}
        if (roofValid) {roof = parseFloat(boxRoofHeight)}

        if (width && wall){
            if (width <= wall * 2){
                message += catalog.i18nc("@error:width_wall", "Box width must be greater than twice wall width.<br>");
                widthValid = false
                wallValid = false
            }
        }

        if (depth && wall){
            if (depth <= wall * 2){
                message += catalog.i18nc("@error:depth_wall", "Box depth must be greater than twice wall width.<br>");
                depthValid = false
                wallValid = false
            }
        }

        if (height && roof){
            if (height <= roof){
                message += catalog.i18nc("@error:height_roof", "Box height must be greater than roof thickness.<br>");
                heightValid = false
                roofValid = false
            }
        }
        // Global property which controls "OK" button and ability to accept dialog with enter key
        inputsValid = (widthValid && depthValid && heightValid && wallValid && roofValid)
        // Global property which displays error message (duh)
        error_message = message

        // Set background for each box
        totalWidth.background.color = getBackgroundColour(widthValid)
        totalDepth.background.color = getBackgroundColour(depthValid)
        totalHeight.background.color = getBackgroundColour(heightValid)
        wallWidth.background.color = getBackgroundColour(wallValid)
        roofThickness.background.color = getBackgroundColour(roofValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first three are ints and the other two are reals. But I have no shortage
    of validation and never do maths with them here. */
    property string boxWidth: "0"
    property string boxDepth: "0"
    property string boxHeight: "0"
    property string boxWallWidth: "0.0"
    property string boxRoofHeight: "0.0"

    property bool inputsValid: false
    property string error_message: ""

    Component.onCompleted: {
        //default_field_background = totalWidth.background.color
        boxWidth = String(manager.bridging_box_width)
        boxDepth = String(manager.bridging_box_depth)
        boxHeight = String(manager.bridging_box_height)
        boxWallWidth = String(manager.bridging_box_wall_width)
        boxRoofHeight = String(manager.bridging_box_roof_height)
        Qt.callLater(validateInputs)
    }

    title: catalog.i18nc("@window_title", "Custom Bridging Box")
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
                text: catalog.i18nc("custom_bridging_box:total_width", "Total Width")
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
                    boxWidth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalDepthLabel
                text: catalog.i18nc("custom_bridging_box:total_depth", "Total Depth")
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
                    boxDepth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_bridging_box:total_height", "Total Height")
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
                    boxHeight = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: wallWidthLabel
                text: catalog.i18nc("custom_bridging_box:wall_width", "Wall Width")
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
                    boxWallWidth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: roofThicknessLabel
                text: catalog.i18nc("custom_bridging_box:roof_thickness", "Roof Thickness")
            }

            UM.TextFieldWithUnit{
                id: roofThickness
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: boxRoofHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    boxRoofHeight = text
                    Qt.callLater(validateInputs)
                }
            }
        }
        UM.Label{
            Layout.fillWidth: true
            id: error_text
            text: customBridgingBox.error_message
            color: UM.Theme.getColor("error")
            wrapMode: TextInput.Wrap
        }
    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_bridging_box_cancel", "Cancel")

            onClicked:{
                customBridgingBox.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_bridging_box_ok", "OK")
            enabled: customBridgingBox.inputsValid

            onClicked: {
                customBridgingBox.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.bridging_box_width = parseInt(boxWidth)
        manager.bridging_box_depth = parseInt(boxDepth)
        manager.bridging_box_height = parseInt(boxHeight)
        manager.bridging_box_wall_width = parseFloat(boxWallWidth)
        manager.bridging_box_roof_height = parseFloat(boxRoofHeight)

        manager.make_custom_bridging_box()
        customBridgingBox.close()
    }
}