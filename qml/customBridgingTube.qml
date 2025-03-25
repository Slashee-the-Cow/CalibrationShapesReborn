// Calibration Shapes Reborn by Slashee the Cow
// Copyright 2025

import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog {

    id: customBridgingTube

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
        customBridgingTube.inputsValid = (validateFloat(tubeOuterDiameter, 1) &&
                        validateFloat(tubeInnerDiameter, 1) &&
                        validateInt(tubeHeight, 1) &&
                        validateFloat(tubeRoofHeight, 0.1))
        //manager.logMessage("validateInputs just set inputsValid to " + inputsValid)
    }

    property variant catalog: UM.I18nCatalog {name: "calibrationshapresreborn" }
    /* The first three are ints and the last one are reals. But I have no shortage
    of validation and never do maths with them here. */
    property string tubeOuterDiameter: "0"
    property string tubeInnerDiameter: "0"
    property string tubeHeight: "0"
    property string tubeRoofHeight: "0.0"

    property bool inputsValid: false

    Component.onCompleted: {
        tubeOuterDiameter = String(manager.bridging_tube_outer_diameter)
        tubeInnerDiameter = String(manager.bridging_tube_inner_diameter)
        tubeHeight = String(manager.bridging_tube_height)
        tubeRoofHeight = String(manager.bridging_tube_roof_height)
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
                text: catalog.i18nc("custom_bridging_tube:outer_diameter", "Outer Diameter")
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
                    validateInputs()
                    //manager.logMessage("totalWidth was just changed. tubeOuterDiameter is now " + tubeOuterDiameter + " and inputsValid is " + inputsValid + " and customBridgingTube.tubeOuterDiameter is " + customBridgingTube.tubeOuterDiameter)
                }
            }

            UM.Label{
                id: innerDiameterLabel
                text: catalog.i18nc("custom_bridging_tube:inner_diameter", "Inner Diameter")
            }

            UM.TextFieldWithUnit{
                id: totalDepth
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
                    validateInputs()
                }
            }

            UM.Label{
                id: totalHeightLabel
                text: catalog.i18nc("custom_bridging_tube:total_height", "Total Height")
            }

            UM.TextFieldWithUnit{
                id: totalHeight
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: tubeHeight
                validator: IntValidator {
                    bottom: 1
                }
                onTextChanged: {
                    tubeHeight = text
                    validateInputs()
                }
            }

            UM.Label{
                id: roofThicknessLabel
                text: catalog.i18nc("custom_bridging_tube:roof_thickness", "Roof Thickness")
            }

            UM.TextFieldWithUnit{
                id: roofThickness
                Layout.minimumWidth: 75
                height: UM.Theme.getSize("setting_control").height
                unit: "mm"
                text: tubeRoofHeight
                validator: DoubleValidator {
                    bottom: 0.1
                    decimals: 1
                    notation: DoubleValidator.StandardNotation
                }
                onTextChanged: {
                    tubeRoofHeight = text
                    validateInputs()
                }
            }
        }

    }
    // Buttons
    rightButtons: [
        Cura.SecondaryButton{
            id: cancelButton
            text: catalog.i18nc("custom_bridging_tube_cancel", "Cancel")

            onClicked:{
                customBridgingTube.reject()
            }
        },
        Cura.PrimaryButton{
            id:okButton
            text: catalog.i18nc("custom_bridging_tube_ok", "OK")
            enabled: customBridgingTube.inputsValid

            onClicked: {
                customBridgingTube.accept()
            }
        }
    ]

    onAccepted: {
        if(!inputsValid){
            manager.logMessage("onAccepted{} triggered while inputsValid is false")
            return
        }

        manager.bridging_tube_outer_diameter = parseFloat(tubeOuterDiameter)
        manager.bridging_tube_inner_diameter = parseFloat(tubeInnerDiameter)
        manager.bridging_tube_height = parseInt(tubeHeight)
        manager.bridging_tube_roof_height = parseFloat(tubeRoofHeight)

        manager.make_custom_bridging_tube()
        customBridgingTube.close()
    }
}