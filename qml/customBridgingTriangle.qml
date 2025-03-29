// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customBridgingTriangle

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
        if (!validateInt(triangleWidth, 1)){
            widthValid = false;
            message += catalog.i18nc("@error:width_invalid", "Box width must be a whole number 1 or higher.<br>");
        }

        if (!validateInt(triangleDepth, 1)){
            depthValid = false;
            message += catalog.i18nc("@error:depth_invalid", "Box depth must be a whole number 1 or higher.<br>");
        }

        if (!validateInt(triangleHeight, 1)){
            heightValid = false;
            message += catalog.i18nc("@error:height_invalid", "Box height must be a whole number 1 or higher.<br>");
        }

        if (!validateFloat(triangleWallWidth, 0.1)){
            wallValid = false;
            message += catalog.i18nc("@error:wallWidth_invalid", "Box wall width must be 0.1 or higher.<br>");
        }

        if (!validateFloat(triangleRoofHeight, 0.1)){
            roofValid = false;
            message += catalog.i18nc("@error:roofThickness_invalid", "Roof thickness must be 0.1 or higher.<br>");
        }
        
        // Test fields for inter-dependencies
        let width = null
        let depth = null
        let height = null
        let wall = null
        let roof = null
        if (widthValid) {width = parseInt(triangleWidth)}
        if (depthValid) {depth = parseInt(triangleDepth)}
        if (heightValid) {height = parseInt(triangleHeight)}
        if (wallValid) {wall = parseFloat(triangleWallWidth)}
        if (roofValid) {roof = parseFloat(triangleRoofHeight)}

        if (width && wall){
            if (width <= wall * 2.5){
                message += catalog.i18nc("@error:width_wall", "Triangle width must be greater than 2.5x wall width.<br>");
                widthValid = false
                wallValid = false
            }
        }

        if (depth && wall){
            if (depth <= wall * 2.5){
                message += catalog.i18nc("@error:depth_wall", "Triangle depth must be greater than 2.5x wall width.<br>");
                depthValid = false
                wallValid = false
            }
        }

        if (height && roof){
            if (height <= roof){
                message += catalog.i18nc("@error:height_roof", "Triangle height must be greater than roof thickness.<br>");
                heightValid = false
                roofValid = false
            }
        }
        // Global property which controls "OK" button and ability to accept dialog with enter key
        inputsValid = (widthValid && depthValid && heightValid && wallValid && roofValid)
        // Global property which displays error message (duh)
        error_message = message

        // Set background for each box
        baseWidth.background.color = getBackgroundColour(widthValid)
        baseDepth.background.color = getBackgroundColour(depthValid)
        totalHeight.background.color = getBackgroundColour(heightValid)
        wallWidth.background.color = getBackgroundColour(wallValid)
        roofThickness.background.color = getBackgroundColour(roofValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first three are ints and the other two are reals. But I have no shortage
    of validation and never do maths with them here. */
    property string triangleWidth: "0"
    property string triangleDepth: "0"
    property string triangleHeight: "0"
    property string triangleWallWidth: "0.0"
    property string triangleRoofHeight: "0.0"

    property bool inputsValid: false
    property string error_message: ""

    Component.onCompleted: {
        triangleWidth = String(manager.bridging_triangle_base_width)
        triangleDepth = String(manager.bridging_triangle_base_depth)
        triangleHeight = String(manager.bridging_triangle_height)
        triangleWallWidth = String(manager.bridging_triangle_wall_width)
        triangleRoofHeight = String(manager.bridging_triangle_roof_height)
        Qt.callLater(validateInputs)
    }

    title: catalog.i18nc("@window_title", "Custom Bridging Triangle")
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
                id: baseWidthLabel
                text: catalog.i18nc("custom_bridging_triangle:base_width", "Base Width")
            }

            UM.TextFieldWithUnit{
                id: baseWidth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: triangleWidth
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    triangleWidth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: baseDepthLabel
                text: catalog.i18nc("custom_bridging_triangle:base_depth", "Base Depth")
            }

            UM.TextFieldWithUnit{
                id: baseDepth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: triangleDepth
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    triangleDepth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_bridging_triangle:total_height", "Total Height")
            }

            UM.TextFieldWithUnit{
                id: totalHeight
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: triangleHeight
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    triangleHeight = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: wallWidthLabel
                text: catalog.i18nc("custom_bridging_triangle:wall_width", "Wall Width")
            }

            UM.TextFieldWithUnit{
                id: wallWidth
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: triangleWallWidth
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    triangleWallWidth = text
                    Qt.callLater(validateInputs)
                }
            }

            UM.Label{
                id: roofThicknessLabel
                text: catalog.i18nc("custom_bridging_triangle:roof_thickness", "Roof Thickness")
            }

            UM.TextFieldWithUnit{
                id: roofThickness
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: triangleRoofHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    triangleRoofHeight = text
                    Qt.callLater(validateInputs)
                }
            }
        }

    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_bridging_triangle_cancel", "Cancel")

            onClicked:{
                customBridgingTriangle.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_bridging_triangle_ok", "OK")
            enabled: customBridgingTriangle.inputsValid

            onClicked: {
                customBridgingTriangle.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.bridging_triangle_base_width = parseInt(triangleWidth)
        manager.bridging_triangle_base_depth = parseInt(triangleDepth)
        manager.bridging_triangle_height = parseInt(triangleHeight)
        manager.bridging_triangle_wall_width = parseFloat(triangleWallWidth)
        manager.bridging_triangle_roof_height = parseFloat(triangleRoofHeight)

        manager.make_custom_bridging_triangle()
        customBridgingTriangle.close()
    }
}