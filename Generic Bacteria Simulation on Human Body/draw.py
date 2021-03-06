from parameters import parameters
import os
import re
import numpy as np
from Point import *
from mayavi import mlab
import matplotlib.pyplot as plt
import threading
import globals as g
import copy

def picker_callback(picker):
    global vessels, lastSelected, bound, showingNode, plots
    if 'lastSelected' not in globals():
        lastSelected = None
    if 'bound' not in globals():
        bound = None
    picked = picker.actors
    for (top, bottom, node) in vessels:
        if top.actor.actor._vtk_obj in [o._vtk_obj for o in picked] or bottom.actor.actor._vtk_obj in [o._vtk_obj for o in picked]:
            if lastSelected != None:
                lastSelected.remove()
            lastSelected = mlab.text(node.start.x, node.start.y, node.name, width=0.2, z=node.start.z)
            if bound != None:
                (tBound, bBound) = bound
                tBound.remove()
                bBound.remove()
            tBound = mlab.outline(top)
            bBound = mlab.outline(bottom)
            bound = (tBound, bBound)
            if plots is None:
                f, plots = plt.subplots(2, 1)
            (ax1, ax2) = plots
            ax1.cla()
            history = copy.deepcopy(node.getCellCountHistory())
            x = np.linspace(0, len(history) * parameters.cell_count_history_interval, len(history))
            y = history
            ax1.plot(x, y, 'r')
            ax1.set_title('Bacteria Count history')            

            ax2.cla()
            history = copy.deepcopy(node.getFlowHistory())
            x = np.linspace(0, len(history) * parameters.cell_count_history_interval, len(history))
            y = history
            ax2.plot(x, y, 'b')
            ax2.set_title('Blood flow history')            

            if showingNode is None:
                plt.show()

            showingNode = node

            break
            

def draw_body(nodes):
    assert(nodes is not None)
    global body_model
    global vessels
    global figure, colorGradient, showingFigure, showingNode, plots

    if 'vessels' not in globals():
        vessels = []
    if 'colorGradient' not in globals():
        colorGradient = parameters.color_gradient.split(',')
    if 'body_model' not in globals() or body_model is None:
        body_model = {'x': [], 'y': [], 'z': [], 'triangles': []}
        current_directory = os.path.dirname(os.path.realpath(__file__))
        with open(current_directory + parameters.body_mesh_file) as data_file:
            for line in data_file:
                if re.match('^v\s+', line):
                    #parse line
                    line = re.sub('^v\s*', '', line)
                    line = re.sub('\n', '', line)
                    parts = re.split('\s', line)
                    x = float(parts[0]); y = float(parts[1]); z = float(parts[2])
                    body_model['x'].append(x)
                    body_model['y'].append(y)
                    body_model['z'].append(z)
                elif re.match('^f\s+', line):
                    line = re.sub('^f\s*', '', line)
                    line = re.sub('\n', '', line)
                    parts = re.split('\s', line)
                    triangle = [ float(re.sub('\/\/.*', '', parts[0]))-1, float(re.sub('\/\/.*', '', parts[1]))-1, float(re.sub('\/\/.*', '', parts[2]))-1 ]
                    body_model['triangles'].append(triangle)
    if 'figure' not in globals():
        figure = mlab.gcf()
    
    mlab.clf()
    figure.scene.disable_render = True
    mlab.triangular_mesh(body_model['x'], body_model['y'], body_model['z'], body_model['triangles'], color=(1,0.8,0.8), opacity=0.2)
    #Blood vessels
    for node in nodes:
        top, bottom = draw_blood_vessel(node.start, node.end, node.radius * parameters.visualization_factor)
        vessels.append((top, bottom, node))
    figure.scene.disable_render = False
    picker = figure.on_mouse_pick(picker_callback)
    picker.tolerance = 0.01
    
    plt.ion()
    showingNode = None
    plots = None
    mlab.view(0,0)
    anim()

@mlab.show
@mlab.animate(delay=int(parameters.refresh_interval * 1000))
def anim():
    global vessels, colorGradient, timeText, showingNode
    timeText = None
    while True:
        if timeText != None:
            timeText.remove()            
        timeText = mlab.text(0.01, 0.01, 'Time: ' + str(g.globals.time), width=0.3)
        for (top, bottom, host) in vessels:
            lutT = top.module_manager.scalar_lut_manager.lut.table.to_array()
            lutB = bottom.module_manager.scalar_lut_manager.lut.table.to_array()
            count = host.getBacteriaCount()
            colorNdx = int(float(count) / parameters.cell_count_color_mapping * (len(colorGradient) - 1))
            if colorNdx >= len(colorGradient):
                colorNdx = len(colorGradient) - 1
            color = colorGradient[colorNdx]
            assert len(color) == 6
            ones = np.ones(np.shape(lutT[:, 0]))
            R = int(color[0:2], 16)
            G = int(color[2:4], 16)
            B = int(color[4:6], 16)
            #R
            lutT[:,0] = ones * R
            lutB[:,0] = ones * R
            #G
            lutT[:,1] = ones * G
            lutB[:,1] = ones * G
            #B
            lutT[:,2] = ones * B
            lutB[:,2] = ones * B            
            top.module_manager.scalar_lut_manager.lut.table = lutT
            bottom.module_manager.scalar_lut_manager.lut.table = lutB
        
        if showingNode is not None:
            (ax1, ax2) = plots
            ax1.cla()
            history = copy.deepcopy(showingNode.getCellCountHistory())
            x = np.linspace(0, len(history) * parameters.cell_count_history_interval, len(history))
            y = history
            ax1.plot(x, y, 'r')
            ax1.set_title('Bacteria Count history')            

            ax2.cla()
            history = copy.deepcopy(showingNode.getFlowHistory())
            x = np.linspace(0, len(history) * parameters.cell_count_history_interval, len(history))
            y = history
            ax2.plot(x, y, 'b')
            ax2.set_title('Blood flow history')  
        mlab.draw()
        if parameters.verbose:      
            print("updating graph")
        yield

def draw_blood_vessel(p1, p2, r, colormap='Reds'):
    assert(isinstance(p1, Point))
    assert(isinstance(p2, Point))
    if(p2.y - p1.y) < 0:
        tmp = p2
        p2 = p1
        p1 = tmp
    u = np.linspace(0, 2 * np.pi, 100)
    l = p2.y - p1.y
    x = r * np.outer(np.cos(u), np.sin(u))
    y = np.empty((len(x),len(x)))
    y.fill(p1.y)
    z = r * np.outer(np.sin(u), np.sin(u))
    #p1
    mlab.mesh(p1.x + x, y, p1.z + z, colormap=colormap)
    #p2
    mlab.mesh(p2.x + x, l+y, p2.z + z, colormap=colormap)
    
    #sides
    x = r * np.linspace(-1, 1, 40)
    y = np.linspace(p1.y, p2.y, 40)

    x, y = np.meshgrid(x, y)
    z = np.sqrt(r**2-x**2)
    neg_z = -z
    diff = np.linspace(p1.x, p2.x, 40)
    diffz = np.linspace(p1.z, p2.z, 40)
    for (row, dx ) in zip(x, diff):
        row += dx
    for (row, dz ) in zip(z, diffz):
        row += dz
    for (row, dz ) in zip(neg_z, diffz):
        row += dz 
    top = mlab.mesh(x,y,neg_z, colormap=colormap)
    bottom = mlab.mesh(x,y,z, colormap=colormap)
    return (top, bottom)