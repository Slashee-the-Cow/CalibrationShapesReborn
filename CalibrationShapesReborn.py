# Part of initial code by fieldOfView 2018
# Based on Calibration Shapes by 5@xes 2020-2022
# Reborn edition by Slashee the Cow 2025-

# Version history (Reborn)
# 1.0.0:    Initial release.
#       - Rebranded.
#       - Removed towers and tests that require use of post-processing scripts
#           AutoTowers Generator does them so much better and asking the user to add a script is a pain.
#       - Removed support for Cura versions below 5.0 to get rid of legacy code.
# 1.0.1:
#       - Replaced "default size" settings box with something you wouldn't be afraid to take how to meet your parents for the first time.
#       - This will have definitely broken the existing translations so they have been removed. If you're happy to help translate this, I'm happier to have you help!
#       - Removed some more old, dead code.
#       - Fixed a couple of typos in code that didn't affect functionality but bugged me.
#       - Fixed a couple of typos in original code that would affect functionality.
# 1.0.2:
#       - Removed even more dead code - but now it uses less RAM than before!
#       - Removed errant function call which broke functionality in older 5.x versions.
# 1.1.0:
#       - Added custom bridging boxes, tubes and triangles thanks to an audience request (see, I want your ideas!)
#       - Removed even more dead code.


import math
import os

import numpy
import trimesh
from UM.Application import Application
from cura.CuraApplication import CuraApplication
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from UM.Extension import Extension
from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.Math.Vector import Vector
from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Message import Message
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Resources import Resources
from UM.Scene.SceneNode import SceneNode
from UM.Scene.SceneNodeSettings import SceneNodeSettings
from UM.Scene.Selection import Selection
from UM.Settings.SettingInstance import SettingInstance
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

import trimesh.creation

DEBUG_MODE = False

def log(level, message):
    """Wrapper function for logging messages using Cura's Logger, but with debug mode so as not to spam you."""
    if level == "d" and DEBUG_MODE:
        Logger.log("d", message)
    elif level == "i":
        Logger.log("i", message)
    elif level == "w":
        Logger.log("w", message)
    elif level == "e":
        Logger.log("e", message)
    elif level == "c":
        Logger.log("c", message)
    elif DEBUG_MODE:
        Logger.log("w", f"Invalid log level: {level} for message {message}")

# Suggested solution from fieldOfView . in this discussion solved in Cura 4.9
# https://github.com/5axes/Calibration-Shapes/issues/1
# Cura are able to find the scripts from inside the plugin folder if the scripts are into a folder named resources
Resources.addSearchPath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources')
)  # Plugin translation file import

catalog = i18nCatalog("calibrationshapesreborn")

if catalog.hasTranslationLoaded():
    Logger.log("i", "Calibration Shapes Reborn Plugin translation loaded!")

class CalibrationShapesReborn(QObject, Extension):
       
    def __init__(self, parent = None) -> None:
        super().__init__()
        
        # set the preferences to store the default value
        self._preferences = CuraApplication.getInstance().getPreferences()
        self._preferences.addPreference("calibrationshapesreborn/shapesize", 20)
        
        self._preferences.addPreference("calibrationshapesreborn/bridging_box_width", 50)
        self._preferences.addPreference("calibrationshapesreborn/bridging_box_depth", 40)
        self._preferences.addPreference("calibrationshapesreborn/bridging_box_height", 40)
        self._preferences.addPreference("calibrationshapesreborn/bridging_box_wall_width", 3)
        self._preferences.addPreference("calibrationshapesreborn/bridging_box_roof_height", 3)
        
        self._preferences.addPreference("calibrationshapesreborn/bridging_tube_outer_diameter", 30)
        self._preferences.addPreference("calibrationshapesreborn/bridging_tube_inner_diameter", 26)
        self._preferences.addPreference("calibrationshapesreborn/bridging_tube_height", 10)
        self._preferences.addPreference("calibrationshapesreborn/bridging_tube_roof_height", 2)
        
        self._preferences.addPreference("calibrationshapesreborn/bridging_triangle_base_width", 40)
        self._preferences.addPreference("calibrationshapesreborn/bridging_triangle_base_depth", 50)
        self._preferences.addPreference("calibrationshapesreborn/bridging_triangle_height", 40)
        self._preferences.addPreference("calibrationshapesreborn/bridging_triangle_wall_width", 3)
        self._preferences.addPreference("calibrationshapesreborn/bridging_triangle_roof_height", 1)

        self._shape_size = float(self._preferences.getValue \
            ("calibrationshapesreborn/shapesize"))
        
        self._bridging_box_width = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_box_width"))
        self._bridging_box_depth = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_box_depth"))
        self._bridging_box_height = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_box_height"))
        self._bridging_box_wall_width = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_box_wall_width"))
        self._bridging_box_roof_height = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_box_roof_height"))

        self._bridging_tube_outer_diameter = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_tube_outer_diameter"))
        self._bridging_tube_inner_diameter = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_tube_inner_diameter"))
        self._bridging_tube_height = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_tube_height"))
        self._bridging_tube_roof_height = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_tube_roof_height"))
            
        self._bridging_triangle_base_width = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_triangle_base_width"))
        self._bridging_triangle_base_depth = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_triangle_base_depth"))
        self._bridging_triangle_height = int(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_triangle_height"))
        self._bridging_triangle_wall_width = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_triangle_wall_width"))
        self._bridging_triangle_roof_height = float(self._preferences.getValue \
            ("calibrationshapesreborn/bridging_triangle_roof_height"))

        self._settings_popup = None
        
        self._bridging_box_dialog = None
        self._bridging_tube_dialog = None
        self._bridging_triangle_dialog = None
        
        # self._settings_qml = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "settings.qml")
        self._settings_qml = os.path.abspath(os.path.join(os.path.dirname(__file__), "qml", "settings.qml"))
        self._bridging_box_qml = os.path.abspath(os.path.join(os.path.dirname(__file__), "qml", "customBridgingBox.qml"))
        self._bridging_tube_qml = os.path.abspath(os.path.join(os.path.dirname(__file__), "qml", "customBridgingTube.qml"))
        self._bridging_triangle_qml = os.path.abspath(os.path.join(os.path.dirname(__file__), "qml", "customBridgingTriangle.qml"))
        
        self._controller = CuraApplication.getInstance().getController()
        
        self.setMenuName(catalog.i18nc("@item:inmenu", "Calibration Shapes"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a cube"), self.addCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a cylinder"), self.addCylinder)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a sphere"), self.addSphere)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a tube"), self.addTube)
        self.addMenuItem("   ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Custom Bridging Hollow Box"), \
            self.add_bridging_box_dialog)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Custom Bridging Tube"), \
            self.add_bridging_tube_dialog)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Custom Bridging Triangle"), \
            self.add_bridging_triangle_dialog)
        self.addMenuItem("    ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Calibration Cube"), self.addCalibrationCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Layer Adhesion Test"), self.addLayerAdhesion)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Retract Test"), self.addRetractTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a XY Calibration Test"), self.addXYCalibration)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Dimensional Accuracy Test"), self.addDimensionalTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Tolerance Test"), self.addTolerance)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Hole Test"), self.addHoleTest)
        
        # self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Junction Deviation Tower"), self.addJunctionDeviationTower)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Bridge Test"), self.addBridgeTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Thin Wall Test"), self.addThinWall)
        # self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Thin Wall Test Cura 5.0"), self.addThinWall2)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add an Overhang Test"), self.addOverhangTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Flow Test"), self.addFlowTest)
        
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Support Test"), self.addSupportTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Lithophane Test"), self.addLithophaneTest)
        
        # self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a MultiCube Calibration"), self.addMultiCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Bed Level Calibration"), self.addBedLevelCalibration)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Backlash Test"), self.addBacklashTest)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Linear/Pressure Adv Tower"), self.addPressureAdvTower)
        self.addMenuItem("     ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Cube bi-color"), self.addCubeBiColor)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Bi-Color Calibration Cube"), self.addHollowCalibrationCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add an Extruder Offset Calibration Part"), self.addExtruderOffsetCalibration)        
        self.addMenuItem("      ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set default size"), self.showSettingsPopup)
        
    @pyqtSlot(str)
    def logMessage(self, value: str) -> None:
        """Wrapper function so QML can log stuff since its own logging doesn't get into Cura's logs."""
        log("d", f"StacksOfShapes QML Log: {value}")

    def showSettingsPopup(self):
        if self._settings_popup is None:
            self._createSettingsPopup()
        self._settings_popup.show()
            
    def _createSettingsPopup(self):
        #qml_file_path = os.path.join(os.path.dirname(__file__), "qml", "settings.qml")
        self._settings_popup = CuraApplication.getInstance().createQmlComponent(self._settings_qml, {"manager": self})
    
    _shape_size_changed = pyqtSignal()
    
    @pyqtSlot(int)
    def SetShapeSize(self, value: int) -> None:
        #Logger.log("d", f"Attempting to set ShapeSize from pyqtProperty: {value}")
        self._preferences.setValue("calibrationshapesreborn/shapesize", value)
        self._shape_size = value
        self._shape_size_changed.emit()

    @pyqtProperty(int, notify = _shape_size_changed)
    def ShapeSize(self) -> int:
        #Logger.log("d", f"ShapeSize pyqtProperty accessed: {self._shape_size}, cast to {int(self._shape_size)}")
        return int(self._shape_size)
    
    _bridging_box_width_changed = pyqtSignal()
    _bridging_box_depth_changed = pyqtSignal()
    _bridging_box_height_changed = pyqtSignal()
    _bridging_box_wall_width_changed = pyqtSignal()
    _bridging_box_roof_height_changed = pyqtSignal()

    def _set_bridging_box_width(self, value: int) -> None:
        log("d", f"_set_bridging_box_width is running with a value of {value}")
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_box_width got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_box_width", new_value)
        self._bridging_box_width = new_value
        self._bridging_box_width_changed.emit()

    @pyqtProperty(int, notify=_bridging_box_width_changed, fset=_set_bridging_box_width)
    def bridging_box_width(self) -> int:
        return self._bridging_box_width

    def _set_bridging_box_depth(self, value: int) -> None:
        log("d", f"_set_bridging_box_depth is running with a value of {value}")
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_box_depth got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_box_depth", new_value)
        self._bridging_box_depth = new_value
        self._bridging_box_depth_changed.emit()
        
    @pyqtProperty(int, notify=_bridging_box_depth_changed, fset=_set_bridging_box_depth)
    def bridging_box_depth(self) -> int:
        return self._bridging_box_depth

    def _set_bridging_box_height(self, value: int) -> None:
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_box_height got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_box_height", new_value)
        self._bridging_box_height = new_value
        self._bridging_box_height_changed.emit()
        
    @pyqtProperty(int, notify=_bridging_box_height_changed, fset=_set_bridging_box_height)
    def bridging_box_height(self) -> int:
        return self._bridging_box_height

    def _set_bridging_box_wall_width(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "set_bridging_box_wall_width got passed a non-float")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_box_wall_width", new_value)
        self._bridging_box_wall_width = new_value
        self._bridging_box_wall_width_changed.emit()
        
    @pyqtProperty(float, notify=_bridging_box_wall_width_changed, fset=_set_bridging_box_wall_width)
    def bridging_box_wall_width(self) -> float:
        return self._bridging_box_wall_width

    def _set_bridging_box_roof_height(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "set_bridging_box_roof_height got passed a non-float")
        self._preferences.setValue(
            "calibrationshapesreborn/bridging_box_roof_height", new_value)
        self._bridging_box_roof_height = new_value
        self._bridging_box_roof_height_changed.emit()

    @pyqtProperty(float, notify=_bridging_box_roof_height_changed, fset=_set_bridging_box_roof_height)
    def bridging_box_roof_height(self) -> float:
        return self._bridging_box_roof_height
    
    def add_bridging_box_dialog(self):
        """Loads the dialog to make a custom bridging box"""
        if self._bridging_box_dialog is None:
            self._create_bridging_box_dialog()
        self._bridging_box_dialog.show()

    def _create_bridging_box_dialog(self) -> None:
        """Creates the custom bridging box dialog if
        it doesn't already exist"""
        context_dict = {
            "manager": self,
        }
        self._bridging_box_dialog = CuraApplication.getInstance().\
            createQmlComponent(self._bridging_box_qml, context_dict)
            
    _bridging_tube_outer_diameter_changed = pyqtSignal()
    _bridging_tube_inner_diameter_changed = pyqtSignal()
    _bridging_tube_height_changed = pyqtSignal()
    _bridging_tube_roof_height_changed = pyqtSignal()

    def _set_bridging_tube_outer_diameter(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "_set_bridging_tube_outer_diameter got passed a non-float")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_tube_outer_diameter", new_value)
        self._bridging_tube_outer_diameter = new_value
        self._bridging_tube_outer_diameter_changed.emit()

    @pyqtProperty(float, notify=_bridging_tube_outer_diameter_changed, fset=_set_bridging_tube_outer_diameter)
    def bridging_tube_outer_diameter(self) -> float:
        return self._bridging_tube_outer_diameter

    def _set_bridging_tube_inner_diameter(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "_set_bridging_tube_inner_diameter got passed a non-float")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_tube_inner_diameter", new_value)
        self._bridging_tube_inner_diameter = new_value
        self._bridging_tube_inner_diameter_changed.emit()
        
    @pyqtProperty(float, notify=_bridging_tube_inner_diameter_changed, fset=_set_bridging_tube_inner_diameter)
    def bridging_tube_inner_diameter(self) -> int:
        return self._bridging_tube_inner_diameter

    def _set_bridging_tube_height(self, value: int) -> None:
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_tube_height got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_tube_height", new_value)
        self._bridging_tube_height = new_value
        self._bridging_tube_height_changed.emit()
        
    @pyqtProperty(int, notify=_bridging_tube_height_changed, fset=_set_bridging_tube_height)
    def bridging_tube_height(self) -> int:
        return self._bridging_tube_height

    def _set_bridging_tube_roof_height(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "set_bridging_tube_roof_height got passed a non-float")
        self._preferences.setValue(
            "calibrationshapesreborn/bridging_tube_roof_height", new_value)
        self._bridging_tube_roof_height = new_value
        self._bridging_tube_roof_height_changed.emit()

    @pyqtProperty(float, notify=_bridging_tube_roof_height_changed, fset=_set_bridging_tube_roof_height)
    def bridging_tube_roof_height(self) -> float:
        return self._bridging_tube_roof_height
    
    def add_bridging_tube_dialog(self):
        """Loads the dialog to make a custom bridging tube"""
        if self._bridging_tube_dialog is None:
            self._create_bridging_tube_dialog()
        self._bridging_tube_dialog.show()

    def _create_bridging_tube_dialog(self) -> None:
        """Creates the custom bridging tube dialog if
        it doesn't already exist"""
        context_dict = {
            "manager": self,
        }
        self._bridging_tube_dialog = CuraApplication.getInstance().\
            createQmlComponent(self._bridging_tube_qml, context_dict)
            
    _bridging_triangle_base_width_changed = pyqtSignal()
    _bridging_triangle_base_depth_changed = pyqtSignal()
    _bridging_triangle_height_changed = pyqtSignal()
    _bridging_triangle_wall_width_changed = pyqtSignal()
    _bridging_triangle_roof_height_changed = pyqtSignal()
    
    def _set_bridging_triangle_base_width(self, value: int) -> None:
        log("d", f"_set_bridging_triangle_base_width is running with a value of {value}")
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_triangle_base_width got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_triangle_base_width", new_value)
        self._bridging_triangle_base_width = new_value
        self._bridging_triangle_base_width_changed.emit()
            
    @pyqtProperty(int, notify=_bridging_triangle_base_width_changed, fset=_set_bridging_triangle_base_width)
    def bridging_triangle_base_width(self) -> int:
        return self._bridging_triangle_base_width
    
    def _set_bridging_triangle_base_depth(self, value: int) -> None:
        log("d", f"_set_bridging_triangle_base_depth is running with a value of {value}")
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_triangle_base_depth got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_triangle_base_depth", new_value)
        self._bridging_triangle_base_depth = new_value
        self._bridging_triangle_base_depth_changed.emit()
            
    @pyqtProperty(int, notify=_bridging_triangle_base_depth_changed, fset=_set_bridging_triangle_base_depth)
    def bridging_triangle_base_depth(self) -> int:
        return self._bridging_triangle_base_depth

    def _set_bridging_triangle_height(self, value: int) -> None:
        try:
            new_value = int(value)
        except ValueError:
            log("w", "_set_bridging_triangle_height got passed a non-int")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_triangle_height", new_value)
        self._bridging_triangle_height = new_value
        self._bridging_triangle_height_changed.emit()
        
    @pyqtProperty(int, notify=_bridging_triangle_height_changed, fset=_set_bridging_triangle_height)
    def bridging_triangle_height(self) -> int:
        return self._bridging_triangle_height

    def _set_bridging_triangle_wall_width(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "set_bridging_triangle_wall_width got passed a non-float")
            return
        self._preferences.setValue("calibrationshapesreborn/bridging_triangle_wall_width", new_value)
        self._bridging_triangle_wall_width = new_value
        self._bridging_triangle_wall_width_changed.emit()
        
    @pyqtProperty(float, notify=_bridging_triangle_wall_width_changed, fset=_set_bridging_triangle_wall_width)
    def bridging_triangle_wall_width(self) -> float:
        return self._bridging_triangle_wall_width

    def _set_bridging_triangle_roof_height(self, value: float) -> None:
        try:
            new_value = float(value)
        except ValueError:
            log("w", "set_bridging_triangle_roof_height got passed a non-float")
        self._preferences.setValue(
            "calibrationshapesreborn/bridging_triangle_roof_height", new_value)
        self._bridging_triangle_roof_height = new_value
        self._bridging_triangle_roof_height_changed.emit()

    @pyqtProperty(float, notify=_bridging_triangle_roof_height_changed, fset=_set_bridging_triangle_roof_height)
    def bridging_triangle_roof_height(self) -> float:
        return self._bridging_triangle_roof_height
    
    def add_bridging_triangle_dialog(self):
        """Loads the dialog to make a custom bridging triangle"""
        if self._bridging_triangle_dialog is None:
            self._create_bridging_triangle_dialog()
        self._bridging_triangle_dialog.show()

    def _create_bridging_triangle_dialog(self) -> None:
        """Creates the custom bridging triangle dialog if
        it doesn't already exist"""
        context_dict = {
            "manager": self,
        }
        self._bridging_triangle_dialog = CuraApplication.getInstance().\
            createQmlComponent(self._bridging_triangle_qml, context_dict)
            

    def addBedLevelCalibration(self) -> None:
        # Get the build plate Size
        machine_manager = CuraApplication.getInstance().getMachineManager()

        global_stack = machine_manager.activeMachine
        machine_width=global_stack.getProperty("machine_width", "value") 
        machine_depth=global_stack.getProperty("machine_depth", "value")
        if (machine_width/machine_depth)>1.15 or (machine_depth/machine_width)>1.15:
            factor_width=round((machine_width/100), 1)
            factor_depth=round((machine_depth/100), 1)
        else:
            factor_width=int(machine_width/100)
            factor_depth=int(machine_depth/100)
        
        # Logger.log("d", "factor_w= %.1f", factor_w)
        # Logger.log("d", "factor_d= %.1f", factor_d)
        
        model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "ParametricBedLevel.stl")
        mesh = trimesh.load(model_definition_path)
        origin = [0, 0, 0]
        direction_x = [1, 0, 0]
        direction_y = [0, 1, 0]
        # DirZ = [0, 0, 1]
        mesh.apply_transform(trimesh.transformations.scale_matrix(factor_width, origin, direction_x))
        mesh.apply_transform(trimesh.transformations.scale_matrix(factor_depth, origin, direction_y))
        # addShape
        self._addShape("BedLevelCalibration",self._toMeshData(mesh))
            
    def _registerShapeStl(self, mesh_name, mesh_filename=None, **kwargs) -> None:
        if mesh_filename is None:
            mesh_filename = mesh_name + ".stl"
        
        model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", mesh_filename)
        mesh =  trimesh.load(model_definition_path)
        
        # addShape
        self._addShape(mesh_name,self._toMeshData(mesh), **kwargs)
 
    def addCalibrationCube(self) -> None:
        self._registerShapeStl("CalibrationCube")

    def addMultiCube(self) -> None:
        self._registerShapeStl("MultiCube")

    def addJunctionDeviationTower(self) -> None:
        self._registerShapeStl("JunctionDeviationTower")
        
    def addRetractTest(self) -> None:
        self._registerShapeStl("RetractTest")

    def addLayerAdhesion(self) -> None:
        self._registerShapeStl("LayerAdhesion")    
    
    def addXYCalibration(self) -> None:
        self._registerShapeStl("xy_calibration")
        
    def addBridgeTest(self) -> None:
        self._registerShapeStl("BridgeTest")

    def addThinWall(self) -> None:
        self._registerShapeStl("ThinWall")
 
    def addThinWall2(self) -> None:
        self._registerShapeStl("ThinWallRought")

    def addBacklashTest(self) -> None:
        self._registerShapeStl("Backlash")  
  
    def addOverhangTest(self) -> None:
        self._registerShapeStl("OverhangTest", "Overhang.stl")
 
    def addFlowTest(self) -> None:
        self._registerShapeStl("FlowTest", "FlowTest.stl")
        
    def addHoleTest(self) -> None:
        self._registerShapeStl("FlowTest", "HoleTest.stl")

    def addTolerance(self) -> None:
        self._registerShapeStl("Tolerance")

    def addLithophaneTest(self) -> None:
        self._registerShapeStl("Lithophane")
        
    # Dotdash addition 2 - Support test
    def addSupportTest(self) -> None:
        self._registerShapeStl("SupportTest")

    # Dimensional Accuracy Test
    def addDimensionalTest(self) -> None:
        self._registerShapeStl("DimensionalAccuracyTest")
        
    # Dotdash addition - for Linear/Pressure advance
    def addPressureAdvTower(self) -> None:
        self._registerShapeStl("PressureAdv", "PressureAdvTower.stl")

    #-----------------------------
    #   Dual Extruder 
    #----------------------------- 
    def addCubeBiColor(self) -> None:
        self._registerShapeStl("CubeBiColorExt1", "CubeBiColorWhite.stl", ext_pos=1)
        self._registerShapeStl("CubeBiColorExt2", "CubeBiColorRed.stl", ext_pos=2)

    def addHollowCalibrationCube(self) -> None:
        self._registerShapeStl("CubeBiColorExt", "HollowCalibrationCube.stl", ext_pos=1)
        self._registerShapeStl("CubeBiColorInt", "HollowCenterCube.stl", ext_pos=2)
        
    def addExtruderOffsetCalibration(self) -> None:
        self._registerShapeStl("CalibrationMultiExtruder1", "nozzle-to-nozzle-xy-offset-calibration-pattern-a.stl", ext_pos=1)
        self._registerShapeStl("CalibrationMultiExtruder1", "nozzle-to-nozzle-xy-offset-calibration-pattern-b.stl", ext_pos=2)

    #-----------------------------
    #   Standard Geometry
    #-----------------------------
    # Origin, xaxis, yaxis, zaxis = [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    # S = trimesh.transformations.scale_matrix(20, origin)
    # xaxis = [1, 0, 0]
    # Rx = trimesh.transformations.rotation_matrix(math.radians(90), xaxis)
    def addCube(self) -> None:
        z_transform = trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5])
        self._addShape("Cube",self._toMeshData(trimesh.creation.box(extents = [self._shape_size, self._shape_size, self._shape_size], transform = z_transform )))
        
    def addCylinder(self) -> None:
        mesh = trimesh.creation.cylinder(radius = self._shape_size / 2, height = self._shape_size, sections=90)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Cylinder",self._toMeshData(mesh))

    def addTube(self) -> None:
        mesh = trimesh.creation.annulus(r_min = self._shape_size / 4, r_max = self._shape_size / 2, height = self._shape_size, sections = 90)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Tube",self._toMeshData(mesh))
        
    # Sphere are not very useful but I leave it for the moment
    def addSphere(self) -> None:
        # subdivisions (int) – How many times to subdivide the mesh. Note that the number of faces will grow as function of 4 ** subdivisions, so you probably want to keep this under ~5
        mesh = trimesh.creation.icosphere(subdivisions=4,radius = self._shape_size / 2,)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Sphere",self._toMeshData(mesh))
        
    #---------------
    #  Custom Stuff
    # --------------
    @pyqtSlot()
    def make_custom_bridging_box(self) -> None:
        """Function that actually creates a bridging box."""
        height = self._bridging_box_height
        width = self._bridging_box_width
        depth = self._bridging_box_depth
        wall_width = self._bridging_box_wall_width
        roof_height = self._bridging_box_roof_height
        
        bridging_box_mesh_data = self.generate_capped_cuboid(width, depth, wall_width, height, roof_height)
        bridging_box = self._toTriMesh(bridging_box_mesh_data)
        
        self._addShape("Bridging Box", self._toMeshData(bridging_box))
    
    def generate_capped_cuboid(self, width, depth, wall_width, height, cap_thickness):
        mesh = MeshBuilder()
        
        cap_height = height - cap_thickness  # Where the cap starts
        
        outer_vertices = [
            Vector(-width/2, -depth/2, 0), Vector(width/2, -depth/2, 0),
            Vector(width/2, depth/2, 0), Vector(-width/2, depth/2, 0),
            Vector(-width/2, -depth/2, height), Vector(width/2, -depth/2, height),
            Vector(width/2, depth/2, height), Vector(-width/2, depth/2, height)
        ]
        
        inner_vertices = [
            Vector(-width/2 + wall_width, -depth/2 + wall_width, 0),
            Vector(width/2 - wall_width, -depth/2 + wall_width, 0),
            Vector(width/2 - wall_width, depth/2 - wall_width, 0),
            Vector(-width/2 + wall_width, depth/2 - wall_width, 0),
            Vector(-width/2 + wall_width, -depth/2 + wall_width, cap_height),
            Vector(width/2 - wall_width, -depth/2 + wall_width, cap_height),
            Vector(width/2 - wall_width, depth/2 - wall_width, cap_height),
            Vector(-width/2 + wall_width, depth/2 - wall_width, cap_height)
        ]
        
        for v in outer_vertices + inner_vertices:
            mesh.addVertex(v.x, v.y, v.z)
        
        # Walls
        for i in range(4):
            mesh.addQuad(outer_vertices[i], outer_vertices[(i+1)%4], outer_vertices[(i+1)%4 + 4], outer_vertices[i+4])
            mesh.addQuad(inner_vertices[(i+1)%4], inner_vertices[i], inner_vertices[i+4], inner_vertices[(i+1)%4 + 4])
        
        # Cap top
        mesh.addQuad(outer_vertices[7], outer_vertices[6], outer_vertices[5], outer_vertices[4])
        
        # Bottom cap inside
        mesh.addQuad(inner_vertices[4], inner_vertices[5], inner_vertices[6], inner_vertices[7])
        
        # Bottom rim (separate quads for each base of the walls)
        for i in range(4):
            mesh.addQuad(inner_vertices[i], inner_vertices[(i+1)%4], outer_vertices[(i+1)%4], outer_vertices[i])
        return mesh.build()

        
    @pyqtSlot()
    def make_custom_bridging_tube(self) -> None:
        """Function that actually creates a tube with a roof."""
        outer_diameter = self._bridging_tube_outer_diameter
        inner_diameter = self._bridging_tube_inner_diameter
        height = self._bridging_tube_height
        roof_height = self._bridging_tube_roof_height
        
        bridging_tube_mesh_data = self.generate_capped_tube(outer_diameter, inner_diameter, height, roof_height)
        bridging_tube = self._toTriMesh(bridging_tube_mesh_data)
        # For whatever reason it lacks colour as a MeshData and I get exceptions trying to calculate the normals.
        self._addShape("Bridging Tube",self._toMeshData(bridging_tube))
    
    def generate_capped_tube(self, outer_diameter, inner_diameter, height, cap_thickness, segments=96):
        mesh = MeshBuilder()
        
        outer_radius = outer_diameter / 2.0
        inner_radius = inner_diameter / 2.0
        cap_height = height - cap_thickness  # Where the cap starts
        
        vertices = []
    
        # Generate vertices
        for i in range(segments):
            angle = (2.0 * math.pi * i) / segments
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Outer tube
            vertices.append(Vector(outer_radius * cos_a, outer_radius * sin_a, 0))  # Bottom outer
            vertices.append(Vector(outer_radius * cos_a, outer_radius * sin_a, cap_height))  # Top outer
            
            # Inner tube
            vertices.append(Vector(inner_radius * cos_a, inner_radius * sin_a, 0))  # Bottom inner
            vertices.append(Vector(inner_radius * cos_a, inner_radius * sin_a, cap_height))  # Top inner
            
            # Cap outer
            vertices.append(Vector(outer_radius * cos_a, outer_radius * sin_a, height))  # Cap outer
            
            # Cap base
            vertices.append(Vector(inner_radius * cos_a, inner_radius * sin_a, cap_height))  # Cap inner base
        
        center_cap = Vector(0, 0, height)  # Center of the cap
        center_cap_base = Vector(0, 0, cap_height)  # Center of the cap base
        
        # Add vertices to the mesh
        for vert in vertices:
            mesh.addVertex(vert.x, vert.y, vert.z)
        mesh.addVertex(center_cap.x, center_cap.y, center_cap.z)
        mesh.addVertex(center_cap_base.x, center_cap_base.y, center_cap_base.z)
        
        # Generate faces
        for i in range(segments):
            next_i = (i + 1) % segments
            v0, v1, v2, v3, v4, v5 = vertices[i * 6], vertices[i * 6 + 1], vertices[i * 6 + 2], vertices[i * 6 + 3], vertices[i * 6 + 4], vertices[i * 6 + 5]
            v0_next, v1_next, v2_next, v3_next, v4_next, v5_next = vertices[next_i * 6], vertices[next_i * 6 + 1], vertices[next_i * 6 + 2], vertices[next_i * 6 + 3], vertices[next_i * 6 + 4], vertices[next_i * 6 + 5]
            
            # Outer wall
            mesh.addQuad(v0, v1, v1_next, v0_next)
            
            # Inner wall
            mesh.addQuad(v2_next, v3_next, v3, v2)
            
            # Top cap side
            mesh.addQuad(v1, v4, v4_next, v1_next)
            
            # Bottom rim (optional if needed)
            mesh.addQuad(v2, v0, v0_next, v2_next)
            
            # Top cap outer (triangulated to center)
            mesh.addFace(v4, v4_next, center_cap)
            
            # Bottom of cap (between inner and outer edges)
            mesh.addQuad(v5, v3, v3_next, v5_next)
            
            # Bottom cap base (triangulated to center base)
            mesh.addFace(v5_next, v5, center_cap_base)

        return mesh.build()

    @pyqtSlot()
    def make_custom_bridging_triangle(self) -> None:
        """Function that creates a hollow triangular prism with a roof."""
        width = self._bridging_triangle_base_width
        depth = self._bridging_triangle_base_depth
        height = self._bridging_triangle_height
        wall_width = self._bridging_triangle_wall_width
        roof_height = self._bridging_triangle_roof_height

        bridging_triangle_mesh_data = self.generate_capped_triangle(width, depth, wall_width, height, roof_height)
        bridging_triangle = self._toTriMesh(bridging_triangle_mesh_data)
        bridging_triangle.apply_translation([-width/2, -depth/2, 0])
        self._addShape("Bridging Triangle",self._toMeshData(bridging_triangle))
        
    def generate_capped_triangle(self, base, height, wall_width, total_height, cap_thickness):
        """
        Create a right-angled triangular prism in CCW order:
        B = (0,0) bottom-left
        A = (base,0) bottom-right (90° corner)
        C = (base,height) top-right
        Then offset inward by wall_width, extrude to total_height,
        and add a 'cap' at (z=cap_height).
        """
        mesh = MeshBuilder()
        
        cap_height = total_height - cap_thickness  # Where the cap starts

        # -----------------------------
        # 1) Outer 2D loop (CCW)
        # -----------------------------
        B2D = Vector(0, 0, 0)
        A2D = Vector(base, 0, 0)
        C2D = Vector(base, height, 0)

        outer_2D = [B2D, A2D, C2D]  # CCW

        # -----------------------------
        # 2) Offset each edge inward
        # -----------------------------
        def rotate_ccw(v: Vector) -> Vector:
            # 2D rotate 90° CCW: (x, y) -> (-y, x)
            return Vector(-v.y, v.x, 0)

        def normalize(v: Vector) -> Vector:
            length = math.sqrt(v.x**2 + v.y**2)
            if length < 1e-9:
                return Vector(0, 0, 0)
            return Vector(v.x / length, v.y / length, 0)

        def offset_edge(p0: Vector, p1: Vector, offset: float):
            """
            Returns (anchor, direction) for the line that is
            'wall_width' inward from edge (p0->p1).
            anchor = p0 shifted by the inward normal
            direction = (p1 - p0)
            """
            edge = Vector(p1.x - p0.x, p1.y - p0.y, 0)
            # 'Left' normal for CCW
            left_normal = rotate_ccw(edge)
            left_normal = normalize(left_normal)
            # Shift p0 by +left_normal*offset
            anchor = Vector(p0.x + left_normal.x*offset,
                            p0.y + left_normal.y*offset, 0)
            return (anchor, edge)

        # For a CCW triangle, edges are:
        #   E0: B->A
        #   E1: A->C
        #   E2: C->B
        edges = [
            offset_edge(outer_2D[0], outer_2D[1], wall_width),
            offset_edge(outer_2D[1], outer_2D[2], wall_width),
            offset_edge(outer_2D[2], outer_2D[0], wall_width)
        ]

        def intersect_lines(anchor1, dir1, anchor2, dir2):
            """
            Intersect two lines in 2D:
            L1(t) = anchor1 + t*dir1
            L2(u) = anchor2 + u*dir2
            Return Vector of intersection or None if parallel.
            """
            # Solve:
            # anchor1 + t*dir1 = anchor2 + u*dir2
            # => anchor1.x + t*dir1.x = anchor2.x + u*dir2.x
            # => anchor1.y + t*dir1.y = anchor2.y + u*dir2.y
            denom = (dir1.x * dir2.y - dir1.y * dir2.x)
            if abs(denom) < 1e-9:
                # Parallel or degenerate
                return None
            dx = anchor2.x - anchor1.x
            dy = anchor2.y - anchor1.y
            t = (dx*dir2.y - dy*dir2.x) / denom
            # Intersection coords
            ix = anchor1.x + t*dir1.x
            iy = anchor1.y + t*dir1.y
            return Vector(ix, iy, 0)

        # -----------------------------
        # 3) Compute each inner vertex
        # -----------------------------
        # Vertex i_in = intersection of edges i-1, i in a cyc
        # For B_in, edges are E2 (C->B) and E0 (B->A)
        # For A_in, edges are E0 (B->A) and E1 (A->C)
        # For C_in, edges are E1 (A->C) and E2 (C->B)
        # We'll define a small helper to get the intersection.
        def inner_vertex(e1_idx, e2_idx):
            anchor1, dir1 = edges[e1_idx]
            anchor2, dir2 = edges[e2_idx]
            return intersect_lines(anchor1, dir1, anchor2, dir2)

        B_in2D = inner_vertex(2, 0)
        A_in2D = inner_vertex(0, 1)
        C_in2D = inner_vertex(1, 2)

        # -----------------------------
        # 4) Build 3D: extrude in Z
        # -----------------------------
        # Outer bottom: B, A, C at z=0
        # Outer top: B_top, A_top, C_top at z= total_height
        # Inner bottom: B_in, A_in, C_in at z=0
        # Inner top (cap base): B_in_top, A_in_top, C_in_top at z=cap_height
        # We'll add them in a consistent order to the mesh.
        B     = Vector(B2D.x,     B2D.y,     0)
        A     = Vector(A2D.x,     A2D.y,     0)
        C     = Vector(C2D.x,     C2D.y,     0)
        B_top = Vector(B2D.x,     B2D.y,     total_height)
        A_top = Vector(A2D.x,     A2D.y,     total_height)
        C_top = Vector(C2D.x,     C2D.y,     total_height)

        # Make sure the intersections returned valid points:
        # (If any is None, we have a degenerate case.)
        if not (B_in2D and A_in2D and C_in2D):
            # Fallback: no offset or raise an error
            # But for brevity, just do a fallback:
            B_in = B
            A_in = A
            C_in = C
        else:
            B_in = Vector(B_in2D.x, B_in2D.y, 0)
            A_in = Vector(A_in2D.x, A_in2D.y, 0)
            C_in = Vector(C_in2D.x, C_in2D.y, 0)

        B_in_top = Vector(B_in.x, B_in.y, cap_height)
        A_in_top = Vector(A_in.x, A_in.y, cap_height)
        C_in_top = Vector(C_in.x, C_in.y, cap_height)

        # Add them all to the mesh as vertices
        all_verts = [
            B, A, C,
            B_top, A_top, C_top,
            B_in, A_in, C_in,
            B_in_top, A_in_top, C_in_top
        ]
        for v in all_verts:
            mesh.addVertex(v.x, v.y, v.z)

        # -----------------------------
        # 5) Build the walls
        # -----------------------------
        # Outer walls (vertical quads)
        mesh.addQuad(B, A, A_top, B_top)  # edge BA
        mesh.addQuad(A, C, C_top, A_top)  # edge AC
        mesh.addQuad(C, B, B_top, C_top)  # edge CB

        # Inner walls (vertical quads, reversed winding for outward normals)
        mesh.addQuad(A_in, B_in, B_in_top, A_in_top)  # edge BA (inner)
        mesh.addQuad(C_in, A_in, A_in_top, C_in_top)  # edge AC (inner)
        mesh.addQuad(B_in, C_in, C_in_top, B_in_top)  # edge CB (inner)

        # -----------------------------
        # 6) Caps
        # -----------------------------
        # Outer cap (top) => single triangle
        mesh.addFace(B_top, A_top, C_top)
        # Inner cap (bottom of the cap) => single triangle
        mesh.addFace(B_in_top, C_in_top, A_in_top)

        # -----------------------------
        # 7) Bottom rim
        # -----------------------------
        # Connect inner bottom to outer bottom
        mesh.addQuad(B_in, A_in, A, B)  # edge BA
        mesh.addQuad(A_in, C_in, C, A)  # edge AC
        mesh.addQuad(C_in, B_in, B, C)  # edge CB

        return mesh.build()

    #----------------------------------------
    # Initial Source code from  fieldOfView
    #----------------------------------------  
    def _toTriMesh(self, mesh_data: MeshData) -> trimesh.base.Trimesh:
        if not mesh_data:
            return trimesh.base.Trimesh()

        indices = mesh_data.getIndices()
        if indices is None:
            # some file formats (eg 3mf) don't supply indices, but have unique vertices per face
            indices = numpy.arange(mesh_data.getVertexCount()).reshape(-1, 3)

        return trimesh.base.Trimesh(vertices=mesh_data.getVertices(), faces=indices)
    
    
    def _toMeshData(self, tri_node: trimesh.base.Trimesh) -> MeshData:
        # Rotate the part to laydown on the build plate
        # Modification from 5@xes
        tri_node.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [-1, 0, 0]))
        tri_faces = tri_node.faces
        tri_vertices = tri_node.vertices
        # Following Source code from  fieldOfView
        # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L45
        indices = []
        vertices = []

        index_count = 0
        face_count = 0
        for tri_face in tri_faces:
            face = []
            for tri_index in tri_face:
                vertices.append(tri_vertices[tri_index])
                face.append(index_count)
                index_count += 1
            indices.append(face)
            face_count += 1

        vertices = numpy.asarray(vertices, dtype=numpy.float32)
        indices = numpy.asarray(indices, dtype=numpy.int32)
        normals = calculateNormalsFromIndexedVertices(vertices, indices, face_count)

        mesh_data = MeshData(vertices=vertices, indices=indices, normals=normals)

        return mesh_data        
        
    # Initial Source code from  fieldOfView
    # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L70
    def _addShape(self, mesh_name, mesh_data: MeshData, extruder_position = 0) -> None:
        application = CuraApplication.getInstance()
        global_stack = application.getGlobalContainerStack()
        if not global_stack:
            return

        node = CuraSceneNode()

        node.setMeshData(mesh_data)
        node.setSelectable(True)
        if len(mesh_name)==0:
            node.setName("TestPart" + str(id(mesh_data)))
        else:
            node.setName(str(mesh_name))

        scene = self._controller.getScene()
        op = AddSceneNodeOperation(node, scene.getRoot())
        op.push()

        extruder_stack = application.getExtruderManager().getActiveExtruderStacks() 

        extruder_number=len(extruder_stack)
        # Logger.log("d", "extruder_nr= %d", extruder_nr)
        # default_extruder_position  : <class 'str'>
        if extruder_position > 0 and extruder_position<=extruder_number :
            default_extruder_position = int(extruder_position-1)
        else :
            default_extruder_position = int(application.getMachineManager().defaultExtruderPosition)
        # Logger.log("d", "default_extruder_position= %s", type(default_extruder_position))
        default_extruder_id = extruder_stack[default_extruder_position].getId()
        # Logger.log("d", "default_extruder_id= %s", default_extruder_id)
        node.callDecoration("setActiveExtruder", default_extruder_id)

        active_build_plate = application.getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))

        node.addDecorator(SliceableObjectDecorator())

        application.getController().getScene().sceneChanged.emit(node)