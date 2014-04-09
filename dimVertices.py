# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils
from bpy.props import *

bl_info = {'name': 'DimensionVertices',
            'description': 'Scale vertices to certain dimension',
            'author': 'Andreas Schuster',
            'category': 'Object'}


class DimVertices(bpy.types.Operator):
    '''Scale selected vertices to certain dimenions'''  # tooltip
    bl_idname = "object.dim_vertices"  # unique identifier for buttons and menu items to reference.
    bl_label = "Dim Vertices"  # display name in the interface
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator

    pDim = FloatProperty(name="Dimension", default=1.0)
    pAxis = EnumProperty(name='Axis', items=[('x', 'x', 'x'), ('y', 'y', 'y'), ('z', 'z', 'z')])
    pConstrainX = BoolProperty(name='ConstrainX', default=True)
    pConstrainY = BoolProperty(name='ConstrainY', default=True)
    pConstrainZ = BoolProperty(name='ConstrainZ', default=True)

    def execute(self, context):
        '''
        '''
        # switch mode
        currentMode = bpy.context.mode
        if currentMode == 'EDIT_MESH':
            currentMode = 'EDIT'
        bpy.ops.object.mode_set(mode='OBJECT')

        # get vertices and bbox
        vertices = []
        for obj in context.selected_objects:
            vertices.extend([i for i in obj.data.vertices if i.select])

        if len(vertices) < 2:
            return {'CANCELLED'}

        bboxMin, bboxMax = self._getMinMax(vertices)

        dimensions = self._getDimensions(bboxMin, bboxMax)
        currentDim = getattr(dimensions, self.pAxis)
        if currentDim < 0.001:
            return {'CANCELLED'}

        # calc scale vector
        scaleFactor = self.pDim / currentDim
        scaleVector = mathutils.Vector((1.0, 1.0, 1.0))
        if self.pConstrainX or self.pAxis == 'x':
            scaleVector.x = scaleFactor
        if self.pConstrainY or self.pAxis == 'y':
            scaleVector.y = scaleFactor
        if self.pConstrainZ or self.pAxis == 'z':
            scaleVector.z = scaleFactor

        # scale it
        center = (bboxMin + bboxMax) / 2.0
        for v in vertices:
            v.co = mathutils.Vector(((v.co.x - center.x) * scaleVector.x + center.x,
                                    (v.co.y - center.y) * scaleVector.y + center.y,
                                    (v.co.z - center.z) * scaleVector.z + center.z))

        # switch mode back
        bpy.ops.object.mode_set(mode=currentMode)
        return {'FINISHED'}  # this lets blender know the operator finished successfully

    def invoke(self, context, event):
        '''
        '''
        return context.window_manager.invoke_props_dialog(self)

    def _getMinMax(self, vertices):
        '''
        '''
        dimMin = mathutils.Vector(vertices[0].co)
        dimMax = mathutils.Vector(vertices[0].co)

        for v in vertices:
            dimMin.x = min(dimMin.x, v.co.x)
            dimMin.y = min(dimMin.y, v.co.y)
            dimMin.z = min(dimMin.z, v.co.z)
            dimMax.x = max(dimMax.x, v.co.x)
            dimMax.y = max(dimMax.y, v.co.y)
            dimMax.z = max(dimMax.z, v.co.z)
        return (dimMin, dimMax)

    def _getDimensions(self, i_min, i_max):
        return mathutils.Vector((abs(i_min.x-i_max.x), abs(i_min.y-i_max.y), abs(i_min.z-i_max.z)))


def register():
    bpy.utils.register_module(__name__)
    # Invoke the dialog when loading
    #bpy.ops.object.dim_vertices('INVOKE_DEFAULT')


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
