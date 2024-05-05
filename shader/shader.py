from pyglet.graphics.shader import Shader, ShaderProgram

# create vertex and fragment shader sources
vertex_source_phong = open('shader/vert_shader_phong.glsl', 'r').read()
fragment_source_phong = open('shader/frag_shader_phong.glsl', 'r').read()
vertex_source_simple = open('shader/vert_shader_simple.glsl', 'r').read()
fragment_source_simple = open('shader/frag_shader_simple.glsl', 'r').read()
vertex_source_circle = open('shader/vert_shader_circle.glsl', 'r').read()
fragment_source_circle = open('shader/frag_shader_circle.glsl', 'r').read()

def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)