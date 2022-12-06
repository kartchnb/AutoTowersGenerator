import math
import numpy
import trimesh

from cura.CuraApplication import CuraApplication
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator

from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation

# This code was shamelessly stolen and refactored from the CalibrationShapes plugin
# by 5@xes (https://github.com/5axes/Calibration-Shapes)
# I don't pretend to have any idea how it works

# The following comments are part of the original code:
# Initial Source code from  fieldOfView
# https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L70
def ImportMesh(meshFilePath, ext_pos = 0, name='') -> tuple:
    # Read in the mesh
    mesh = trimesh.load(meshFilePath)
    mesh_data = _toMeshData(mesh)

    application = CuraApplication.getInstance()
    global_stack = application.getGlobalContainerStack()
    if not global_stack:
        return

    node = CuraSceneNode()

    node.setMeshData(mesh_data)
    node.setSelectable(True)
    node.setName(name)

    scene = CuraApplication.getInstance().getController().getScene()
    op = AddSceneNodeOperation(node, scene.getRoot())
    op.push()

    extruder_stack = application.getExtruderManager().getActiveExtruderStacks()

    extruder_nr=len(extruder_stack)
    if ext_pos>0 and ext_pos<=extruder_nr :
        default_extruder_position = int(ext_pos-1)
    else :
        default_extruder_position = int(application.getMachineManager().defaultExtruderPosition)
    default_extruder_id = extruder_stack[default_extruder_position].getId()
    node.callDecoration("setActiveExtruder", default_extruder_id)

    active_build_plate = application.getMultiBuildPlateModel().activeBuildPlate
    node.addDecorator(BuildPlateDecorator(active_build_plate))

    node.addDecorator(SliceableObjectDecorator())

    application.getController().getScene().sceneChanged.emit(node)

    # Modification from 5axes' code to return the AddNodeOperation to allow this operation to be undone later
    return op



def _toMeshData(tri_node: trimesh.base.Trimesh) -> MeshData:
    # Rotate the part to laydown on the build plate
    # Modification from 5@xes
    tri_node.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [-1, 0, 0]))
    tri_faces = tri_node.faces
    tri_vertices = tri_node.vertices

    # Following Source code from fieldOfView
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
