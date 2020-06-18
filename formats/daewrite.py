from xml.etree.ElementTree import *


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self, info: dict):
        collada = Element('COLLADA', version='1.4.1', xmlns='http://www.collada.org/2005/11/COLLADASchema')
        library_materials = SubElement(collada, 'library_materials')
        library_effects = SubElement(collada, 'library_effects')
        library_images = SubElement(collada, 'library_images')
        library_geometries = SubElement(collada, 'library_geometries')
        library_controllers = SubElement(collada, 'library_controllers')
        library_animations = SubElement(collada, 'library_animations')
        library_cameras = SubElement(collada, 'library_cameras')
        library_visual_scenes = SubElement(collada, 'library_visual_scenes')

        for material_info in info['materials']:
            material = SubElement(library_materials, 'material', id=material_info['name'])
            effect = SubElement(library_effects, 'effect', id=material_info['name'])
            profile = SubElement(effect, 'profile_COMMON')
            technique = SubElement(profile, 'technique', sid='phong')
            phong = SubElement(technique, 'phong')

            emission = SubElement(phong, 'emission')
            ambient = SubElement(phong, 'ambient')
            diffuse = SubElement(phong, 'diffuse')
            specular = SubElement(phong, 'specular')

            if material_info['effect']['emission'] is tuple:
                SubElement(emission, 'color').text = ' '.join(material_info['effect']['emission'])
            else:
                newparam = SubElement(profile, 'newparam', sid=material_info['effect']['emission'] + '-emission')
                surface = SubElement(newparam, 'surface', type='2D')
                SubElement(surface, 'init_from').text = material_info['effect']['emission']
                SubElement(emission, 'texture', texture=material_info['effect']['emission'])

            if material_info['effect']['ambient'] is tuple:
                SubElement(ambient, 'color').text = ' '.join(material_info['effect']['ambient'])
            else:
                newparam = SubElement(profile, 'newparam', sid=material_info['effect']['ambient'] + '-ambient')
                surface = SubElement(newparam, 'surface', type='2D')
                SubElement(surface, 'init_from').text = material_info['effect']['ambient']
                SubElement(emission, 'texture', texture=material_info['effect']['ambient'])

            if material_info['effect']['diffuse'] is tuple:
                SubElement(diffuse, 'color').text = ' '.join(material_info['effect']['diffuse'])
            else:
                newparam = SubElement(profile, 'newparam', sid=material_info['effect']['diffuse'] + '-diffuse')
                surface = SubElement(newparam, 'surface', type='2D')
                SubElement(surface, 'init_from').text = material_info['effect']['diffuse']
                SubElement(emission, 'texture', texture=material_info['effect']['diffuse'])

            if material_info['effect']['specular'] is tuple:
                SubElement(specular, 'color').text = ' '.join(material_info['effect']['specular'])
            else:
                newparam = SubElement(profile, 'newparam', sid=material_info['effect']['specular'] + '-specular')
                surface = SubElement(newparam, 'surface', type='2D')
                SubElement(surface, 'init_from').text = material_info['effect']['specular']
                SubElement(emission, 'texture', texture=material_info['effect']['specular'])
            # shininess = SubElement(phong, 'shininess')
            # SubElement(shininess, 'float').text = '50'
            # reflective = SubElement(phong, 'reflective')
            # SubElement(reflective, 'color').text = 'r g b a'
            # reflectivity = SubElement(phong, 'reflectivity')
            # SubElement(reflectivity, 'float').text = '0-1'
            # transparent = SubElement(phong, 'transparent')
            # SubElement(transparent, 'color').text = 'r g b a'
            # transparency = SubElement(phong, 'transparency')
            # SubElement(transparency, 'float').text = '0-1'
            SubElement(material, 'instance_effect', url=material_info['name'])

        for geometry_info in info['geometries']:  # TODO: geometries
            pass

        for node_info in info['nodes']:  # TODO: nodes
            pass
        print(tostring(collada, xml_declaration=True))

# Effect Example
# <profile_COMMON>
#     <newparam sid="myDiffuseColor">
#         <float3> 0.2 0.56 0.35 </float3>
#     </newparam>
#     <technique sid="phong1">
#         <phong>
#             <emission><color>1.0 0.0 0.0 1.0</color></emission>
#             <ambient><color>1.0 0.0 0.0 1.0</color></ambient>
#             <diffuse><param ref="myDiffuseColor"/></param></diffuse>
#             <specular><color>1.0 0.0 0.0 1.0</color></specular>
#             <shininess><float>50.0</float></shininess>
#             <reflective><color>1.0 1.0 1.0 1.0</color></reflective>
#             <reflectivity><float>0.5</float></reflectivity>
#             <transparent><color>0.0 0.0 1.0 1.0</color></transparent>
#             <transparency><float>1.0</float></transparency>
#         </phong>
#     </technique>
# </profile_COMMON>
