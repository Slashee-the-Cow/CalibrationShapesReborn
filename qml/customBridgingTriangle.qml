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
    
    function validateInputs(){
        customBridgingTriangle.inputsValid = (
                        validateInt(triangleWidth, 1) &&
                        validateInt(triangleDepth, 1) &&
                        validateInt(triangleHeight, 1) &&
                        validateFloat(triangleWallWidth, 0.1) &&
                        validateFloat(triangleRoofHeight, 0.1))
        //manager.logMessage("validateInputs just set inputsValid to " + inputsValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first two are ints and the other two are reals. But I have no shortage
    of validation and never do maths with them here. */
    property string triangleWidth: "0"
    property string triangleDepth: "0"
    property string triangleHeight: "0"
    property string triangleWallWidth: "0.0"
    property string triangleRoofHeight: "0.0"

    property bool inputsValid: false

    Component.onCompleted: {
        triangleWidth = String(manager.bridging_triangle_base_width)
        triangleDepth = String(manager.bridging_triangle_base_depth)
        triangleHeight = String(manager.bridging_triangle_height)
        triangleWallWidth = String(manager.bridging_triangle_wall_width)
        triangleRoofHeight = String(manager.bridging_triangle_roof_height)
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
                    validateInputs()
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
                    validateInputs()
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
                    validateInputs()
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
                    validateInputs()
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
                    validateInputs()
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