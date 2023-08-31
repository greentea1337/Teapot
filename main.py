from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
import numpy as np
import configparser

config = configparser.ConfigParser()
config.read('config.txt')

grid_enabled = config['Grid'].getboolean('enabled')

def load_obj(file_path):
    vertices = []
    faces = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                vertex = line.split()[1:]
                vertex = [float(coord) for coord in vertex]
                vertices.append(vertex)
            elif line.startswith('f '):
                face = line.split()[1:]
                face = [int(index.split('/')[0]) - 1 for index in face]
                faces.append(face)

    return vertices, faces

def calculate_normals(vertices, faces):
    normals = []

    for face in faces:
        v1 = np.array(vertices[face[0]])
        v2 = np.array(vertices[face[1]])
        v3 = np.array(vertices[face[2]])

        normal = np.cross(v2 - v1, v3 - v1)
        normal /= np.linalg.norm(normal)

        for _ in range(3):
            normals.append(normal)

    return normals

def draw_teapot(normals):
    normals_array = np.array(normals, dtype=np.float32)

    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 0, normals_array)

    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glColor4f(float(config['TeapotColor']['red']), float(config['TeapotColor']['green']), float(config['TeapotColor']['blue']), float(config['TeapotColor']['alpha']))

    glDrawElements(GL_TRIANGLES, len(faces) * 3, GL_UNSIGNED_INT, None)

    glDisable(GL_POLYGON_OFFSET_FILL)

    glLineWidth(1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(float(config['GridColor']['red']), float(config['GridColor']['green']), float(config['GridColor']['blue']))

    if grid_enabled:
        glDrawElements(GL_TRIANGLES, len(faces) * 3, GL_UNSIGNED_INT, None)

    glDisableClientState(GL_NORMAL_ARRAY)

def init():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)

    samples = int(config['Smoothing']['samples'])
    glutSetOption(GLUT_MULTISAMPLE, samples)

    glutInitWindowSize(int(config['Window']['width']), int(config['Window']['height']))
    glutCreateWindow(b"Teapot")
    gluPerspective(45, (int(config['Window']['width']) / int(config['Window']['height'])), 0.1, 50.0)
    glTranslate(0.0, 0.0, -5.0)
    glRotatef(0, 0, 0, 0)
    glScalef(float(config['Teapot']['scale']), float(config['Teapot']['scale']), float(config['Teapot']['scale']))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_MULTISAMPLE)

    # Добавляем направленное освещение
    light_direction = [1.0, 1.0, 1.0, 0.0]  # Направление света
    light_color = [1.0, 1.0, 1.0, 1.0]  # Цвет света

    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
    glEnable(GL_LIGHT0)

def render_scene():
    glRotatef(1, 1, 1, 1)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, None)

    draw_teapot(normals)

    glDisableClientState(GL_VERTEX_ARRAY)

    glutSwapBuffers()

def disable_grid():
    global grid_enabled
    grid_enabled = False

def main():
    init()

    global vertices, faces, vertex_buffer, index_buffer, normals
    vertices, faces = load_obj('teapot.obj')
    normals = calculate_normals(vertices, faces)

    vertex_buffer= glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)

    index_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(faces, dtype=np.uint32), GL_STATIC_DRAW)

    glutDisplayFunc(render_scene)
    glutIdleFunc(render_scene)
    glutMainLoop()

if __name__ == '__main__':
    main()