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

    
# Imports from the python standard library to build the plugin functionality
import os
import math
import numpy
import trimesh


from UM.Extension import Extension
from UM.Application import Application
from cura.CuraApplication import CuraApplication

from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Resources import Resources
from UM.Settings.SettingInstance import SettingInstance
from cura.Scene.CuraSceneNode import CuraSceneNode
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Scene.SceneNodeSettings import SceneNodeSettings
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.SetTransformOperation import SetTransformOperation

from UM.Logger import Logger
from UM.Message import Message

from UM.i18n import i18nCatalog

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

# Suggested solution from fieldOfView . in this discussion solved in Cura 4.9
# https://github.com/5axes/Calibration-Shapes/issues/1
# Cura are able to find the scripts from inside the plugin folder if the scripts are into a folder named resources
Resources.addSearchPath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources')
)  # Plugin translation file import

catalog = i18nCatalog("calibrationshapesreborn")

if catalog.hasTranslationLoaded():
    Logger.log("i", "Calibration Shapes Reborn Plugin translation loaded!")

#This class is the extension and doubles as QObject to manage the qml    
class CalibrationShapesReborn(QObject, Extension):
    
    
    def __init__(self, parent = None) -> None:
        super().__init__()
        
        # set the preferences to store the default value
        self._preferences = CuraApplication.getInstance().getPreferences()
        self._preferences.addPreference("calibrationshapesreborn/shapesize", 20)

        self._shape_size = float(self._preferences.getValue("calibrationshapesreborn/shapesize"))  

        self._settings_popup = None
        
        # self._settings_qml = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "settings.qml")
        self._settings_qml = os.path.abspath(os.path.join(os.path.dirname(__file__), "qml", "settings.qml"))
        
        self._controller = CuraApplication.getInstance().getController()
        
        self.setMenuName(catalog.i18nc("@item:inmenu", "Calibration Shapes"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a cube"), self.addCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a cylinder"), self.addCylinder)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a sphere"), self.addSphere)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a tube"), self.addTube)
        self.addMenuItem("", lambda: None)
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
        self.addMenuItem("  ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Cube bi-color"), self.addCubeBiColor)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add a Bi-Color Calibration Cube"), self.addHollowCalibrationCube)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add an Extruder Offset Calibration Part"), self.addExtruderOffsetCalibration)        
        self.addMenuItem("   ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set default size"), self.showSettingsPopup)

  
    # Define the default value for the standard element
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
          
    def addBedLevelCalibration(self) -> None:
        # Get the build plate Size
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine
        m_w=global_stack.getProperty("machine_width", "value") 
        m_d=global_stack.getProperty("machine_depth", "value")
        if (m_w/m_d)>1.15 or (m_d/m_w)>1.15:
            factor_w=round((m_w/100), 1)
            factor_d=round((m_d/100), 1) 
        else:
            factor_w=int(m_w/100)
            factor_d=int(m_d/100)          
        
        # Logger.log("d", "factor_w= %.1f", factor_w)
        # Logger.log("d", "factor_d= %.1f", factor_d)
        
        model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "ParametricBedLevel.stl")
        mesh = trimesh.load(model_definition_path)
        origin = [0, 0, 0]
        DirX = [1, 0, 0]
        DirY = [0, 1, 0]
        # DirZ = [0, 0, 1]
        mesh.apply_transform(trimesh.transformations.scale_matrix(factor_w, origin, DirX))
        mesh.apply_transform(trimesh.transformations.scale_matrix(factor_d, origin, DirY))
        # addShape
        self._addShape("BedLevelCalibration",self._toMeshData(mesh))       
            
    def _registerShapeStl(self, mesh_name, mesh_filename=None, **kwargs) -> None:
        if mesh_filename is None:
            mesh_filename = mesh_name + ".stl"
        
        model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", mesh_filename)
        mesh =  trimesh.load(model_definition_path)
        
        # addShape
        self._addShape(mesh_name,self._toMeshData(mesh), **kwargs)
 
    # Source code from MeshTools Plugin 
    # Copyright (c) 2020 Aldo Hoeben / fieldOfView
    def _getAllSelectedNodes(self) -> list[SceneNode]:
        selection = Selection.getAllSelectedObjects()[:]
        if selection:
            deep_selection = []  # type: list[SceneNode]
            for selected_node in selection:
                if selected_node.hasChildren():
                    deep_selection = deep_selection + selected_node.getAllChildren()
                if selected_node.getMeshData() != None:
                    deep_selection.append(selected_node)
            if deep_selection:
                return deep_selection

        Message(catalog.i18nc("@info:status", "Please select one or more models first"))

        return []
                       
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
        Tz = trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5])
        self._addShape("Cube",self._toMeshData(trimesh.creation.box(extents = [self._shape_size, self._shape_size, self._shape_size], transform = Tz )))
        
    def addCylinder(self) -> None:
        mesh = trimesh.creation.cylinder(radius = self._shape_size / 2, height = self._shape_size, sections=90)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Cylinder",self._toMeshData(mesh))

    def addTube(self) -> None:
        mesh = trimesh.creation.annulus(r_min = self._shape_size / 4, r_max = self._shape_size / 2, height = self._shape_size, sections = 90)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Tube",self._toMeshData(mesh))
        
    # Sphere are not very usefull but I leave it for the moment    
    def addSphere(self) -> None:
        # subdivisions (int) – How many times to subdivide the mesh. Note that the number of faces will grow as function of 4 ** subdivisions, so you probably want to keep this under ~5
        mesh = trimesh.creation.icosphere(subdivisions=4,radius = self._shape_size / 2,)
        mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, self._shape_size*0.5]))
        self._addShape("Sphere",self._toMeshData(mesh))

    #----------------------------------------
    # Initial Source code from  fieldOfView
    #----------------------------------------  
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
    def _addShape(self, mesh_name, mesh_data: MeshData, ext_pos = 0 , hole = False , thin = False , mode = "" ) -> None:
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
        
        extruder_nr=len(extruder_stack)
        # Logger.log("d", "extruder_nr= %d", extruder_nr)
        # default_extruder_position  : <class 'str'>
        if ext_pos>0 and ext_pos<=extruder_nr :
            default_extruder_position = int(ext_pos-1)
        else :
            default_extruder_position = int(application.getMachineManager().defaultExtruderPosition)
        # Logger.log("d", "default_extruder_position= %s", type(default_extruder_position))
        default_extruder_id = extruder_stack[default_extruder_position].getId()
        # Logger.log("d", "default_extruder_id= %s", default_extruder_id)
        node.callDecoration("setActiveExtruder", default_extruder_id)
 
        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()
        # Remove All Holes
        if hole :
            definition = stack.getSettingDefinition("meshfix_union_all_remove_holes")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", True)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance) 
        # Print Thin Walls    
        if thin :
            definition = stack.getSettingDefinition("fill_outline_gaps")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", True)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
 
        if len(mode) :
            definition = stack.getSettingDefinition("magic_mesh_surface_mode")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", mode)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
            
            
        active_build_plate = application.getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))

        node.addDecorator(SliceableObjectDecorator())

        application.getController().getScene().sceneChanged.emit(node)