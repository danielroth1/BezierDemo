import tkinter as tk
from tkinter.constants import LEFT, RIGHT
import numpy as np

def quadratic_bezier(t, p0, p1, p2):
    """
    :return: Quadratic bezier formular according to https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves
    """
    return (1 - t) * ((1 - t) * p0 + t * p1) + t * ((1 - t) * p1 + t * p2)

def cubic_bezier(t, p0, p1, p2, p3):
    """
    :return: Cubic bezier formular according to https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
    """
    return (1 - t) * quadratic_bezier(t, p0, p1, p2) + t * quadratic_bezier(t, p1, p2, p3)

def draw_bezier_curve_quadratic(p, line_color, resolution=20):
    """
    Draw a quadratic bezier curve.
    :param p: control points of the spline
    :line_color: color of the drawn line
    :resolution: number of segments (each segment is a tiny straight line)
    """
    for i in range(len(p)):
        i = i * 2
        if i + 2 < len(p):
            b_prev = p[i]
            for res_index in range(resolution):
                t = float(res_index) / resolution
                b = quadratic_bezier(t, p[i], p[i + 1], p[i + 2])
                can.create_line(b_prev[0], b_prev[1], b[0], b[1], fill=line_color)
                b_prev = b


def draw_bezier_curve_cubic(p, line_color, resolution=20):
    """
    Draw a cubic bezier curve.
    :param p: control points of the spline
    :line_color: color of the drawn line
    :resolution: number of segments (each segment is a tiny straight line)
    """
    for i in range(len(p)):
        i = i * 3
        if i + 3 < len(p):
            b_prev = p[i]
            for res_index in range(resolution + 1):
                t = float(res_index) / resolution
                b = cubic_bezier(t, p[i], p[i + 1], p[i + 2], p[i + 3])
                can.create_line(b_prev[0], b_prev[1], b[0], b[1], fill=line_color)
                b_prev = b

def dot(p0, p1):
    """
    :return: dot product of the given 2d vectors
    """
    return p0[0] * p1[0] + p0[1] * p1[1]

def norm(p):
    """
    :return: norm of the given 2d vector
    """
    return np.sqrt(p[0] * p[0] + p[1] * p[1])

def normalize(p):
    """
    :return: normalized 2d vector
    """
    return 1 / norm(p) * p

def project_point_on_line(p, p0, p1):
    """
    :return: the projected point p on the line that is defined by (p0, p1). (p0, p1) must be normalized.
    """
    d = (p1 - p0)
    return p0 + dot(d, p - p0) * d

def project_point_on_line_fac(p, p0, p1):
    """
    :return: the factor that needs to be multiplied to get the projected point p on the line that is defined by (p0, p1). (p0, p1) must be normalized.
    """
    d = (p1 - p0)
    return dot(d, p - p0)

def draw_points(points, line_color):
    """
    Draw spheres for each given point.
    :param points: list of points to draw.
    """
    radius = 5
    for p in points:
        can.create_oval(p[0] - radius, p[1] - radius, p[0] + radius, p[1] + radius, outline=line_color)

def draw_connected_points(p, line_color):
    """
    Draw a dashed lines that connectes the given points p
    :param p: - list/array of points
    """
    for i in range(len(p) - 1):
        can.create_line(p[i][0], p[i][1], p[i + 1][0], p[i + 1][1], dash=(10,10), fill=line_color)

def connect_line(points, connect_ends, factor):
    """
    Creates a cubic bezier curve that connects the given points.
    Control points are calculated in a way that the resulting curve intersects the given points.
    :param connect_ends: bool if the start and end of the curve should be connected.
    :param factor: defines the amount of "curvature". 0 makes the corners edges while larger values (> 400) makes them completely round.
    :return: list of the cubic bezier control points
    """
    if len(points) < 3:
        return ()
    
    if connect_ends:
        bezier_points = np.zeros((3 * len(points), 2))
        for i in range(len(points)):
            iPrev = (i - 1) % len(points)
            iNext = (i + 1) % len(points)
            # factor_used = min(factor, 0.5 * norm(points[i] - points[i - 1]), 0.5 * norm(points[i + 1] - points[i]))
            factor_used = min(factor, 0.5 * norm(points[i] - points[iPrev]))
            dir = normalize(points[iNext] - points[iPrev])
            bezier_points[(3 * i - 1) % len(bezier_points)] = points[i] - factor_used * dir
            bezier_points[3 * i] = points[i]

            factor_used = min(factor, 0.5 * norm(points[iNext] - points[i]))
            bezier_points[(3 * i + 1) % len(bezier_points)] = points[i] + factor_used * dir
        bezier_points = np.append(bezier_points, np.array([bezier_points[0]]), axis=0)
    else:
        bezier_points = np.zeros((3 * len(points) - 2, 2))
        bezier_points[0] = points[0]
        factor_used = min(factor, 0.5 * norm(points[1] - points[0]))
        bezier_points[1] = points[0] + factor_used * normalize(points[1] - points[0])
        factor_used = min(factor, 0.5 * norm(points[len(points) - 1] - points[len(points) - 2]))
        bezier_points[len(bezier_points) - 2] = points[len(points) - 1] - factor_used * normalize(points[len(points) - 1] - points[len(points) - 2])
        bezier_points[len(bezier_points) - 1] = points[len(points) - 1]
        for i in range(len(points) - 1):
            if i == 0:
                continue
            factor_used = min(factor, 0.5 * norm(points[i] - points[i - 1]))
            dir = normalize(points[i + 1] - points[i - 1])
            bezier_points[3 * i - 1] = points[i] - factor_used * dir
            bezier_points[3 * i] = points[i]

            factor_used = min(factor, 0.5 * norm(points[i + 1] - points[i]))
            bezier_points[3 * i + 1] = points[i] + factor_used * dir
        
    draw_bezier_curve_cubic(bezier_points, line_color)
    return bezier_points


# List of list of points. Each list represents it's own curve that is separated from the others.
points_list = [np.array([[100, 100],
                    [200, 200],
                    [100, 300],
                    [400, 400],
                    [500, 350],
                    [350, 200]])]

# main window
window = tk.Tk()
window.title("Bezier Demo")
window.config(height=1000, width=1000)

# canvas
canvas_width = 1200
canvas_height = 800
can = tk.Canvas(window, bg = 'white', height=canvas_height, width=canvas_width)
can.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

line_color = "#476042"

def redraw2(show_control_points, show_connected_points, connect_ends, factor):
    """
    Redraws the canvas.
    :param show_control_points: show the cubic bezier control points.
    :param show_connect_points: draw a circle for all points that should be connected.
    :param connect_ends: connect the ends of the cubic bezier splines
    :param factor: "curvature" factor. Defines how round the corners are.
    """
    can.delete("all")
    
    for points in points_list:
        if show_connected_points:
            draw_points(points, 'blue')
        bezier_points = connect_line(points, connect_ends, factor)
        if len(bezier_points) > 0 and show_control_points:
            draw_connected_points(bezier_points, 'red')
    
def redraw():
    redraw2(show_control_points_var.get() == 1, show_connected_points_var.get() == 1, connect_ends_var.get(), factorSlider.get())

def append_new_curve():
    """
    Add a new curve that will be considered in future mouse clicks.
    """
    points_list.append(np.zeros((0,2)))

# Event handlers

# Mouse left click
def mouse_left_clicked(event):
    global points_list

    if (event.state & 0x4) != 0: # pressing ctrl while left clicking, automatically sets a new curve
        append_new_curve()

    points_list[len(points_list) - 1] = np.append(points_list[len(points_list) - 1], np.array([[event.x, event.y]]), axis=0)
    redraw()
can.bind("<Button-1>", mouse_left_clicked)

# Mouse right click
def mouse_right_clicked(event):
    global points_list
    points_list[len(points_list) - 1] = points_list[len(points_list) - 1][:-1]
    redraw()
can.bind("<Button-2>", mouse_right_clicked)

# add other controls to the window
settingsFrame = tk.Frame()
settingsFrame.pack(side=RIGHT)

def var_changed():
    redraw()

# show control points check box
show_control_points_var = tk.IntVar()
show_control_points_var.set(1)
c1 = tk.Checkbutton(settingsFrame, text='Control points', variable=show_control_points_var, onvalue=1, offvalue=0, command=var_changed)
c1.pack(fill="x")

# show connected points check box
show_connected_points_var = tk.IntVar()
show_connected_points_var.set(1)
c2 = tk.Checkbutton(settingsFrame, text='Connected points', variable=show_connected_points_var, onvalue=1, offvalue=0, command=var_changed)
c2.pack(fill="x")

# connect ends check box
connect_ends_var = tk.IntVar()
connect_ends_var.set(1)
connect_ends_checkbox = tk.Checkbutton(settingsFrame, text='Connect ends', variable=connect_ends_var, onvalue=1, offvalue=0, command=var_changed)
connect_ends_checkbox.pack(fill="x")

# curvature factor slider
def slider_changed(value):
    redraw()
factorSlider = tk.Scale(settingsFrame, from_=0, to=400, orient=tk.HORIZONTAL, command=slider_changed)
factorSlider.set(50)
factorSlider.pack()
def clear_command():
    global points_list
    points_list = ([np.zeros((0,2))])
    redraw()
clearButton = tk.Button(settingsFrame, text="Clear", command=clear_command)
clearButton.pack()

# new curve button
def new_curve_command():
    global points_list
    append_new_curve()
    redraw()
newCurveButton = tk.Button(settingsFrame, text="New curve", command=new_curve_command)
newCurveButton.pack()
can.pack()

# Initial redraw of the canvas.
redraw()

# center window
window.eval('tk::PlaceWindow . center')

window.mainloop()