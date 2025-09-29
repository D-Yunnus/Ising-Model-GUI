import customtkinter as ctk
import tkinter as tk

import math as math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors

import Metro_Algo as metro


# -----------
# Root Window
# -----------
class root(ctk.CTk):

    def __init__(self):

        # __init__() from ctk.CTk() class
        super().__init__()

        # title
        self.title('Statistical Field Theory Models')
        # size
        self.geometry('650x950')
        self.resizable(False, False)

        # background color
        self.color = '#1B1B1C'
        self.configure(fg_color = self.color)

        # -------------
        # Switch Button
        # -------------
        self.switch_Frame = ctk.CTkFrame(self, fg_color = 'transparent')
        self.lbl_Model = ctk.CTkLabel(self.switch_Frame, text = 'Ising Model', text_color = 'white')

        self.switch = tk.IntVar(value = 0)
        self.btn_Switch = ctk.CTkSwitch(self.switch_Frame, variable = self.switch, command = self.switch_models)

        # place in frame
        self.btn_Switch.pack(side = 'right', padx = 5, pady = 5)
        self.lbl_Model.pack(side = 'right')

        # ---------------------
        # Phase Diagram Widgets
        # ---------------------
        self.phase_grid_dim = [200, 200]
        self.grid_scalings = [3.5, 2]
        self.Phase_Diagram = PhaseDiagram(self, self.phase_grid_dim, self.grid_scalings, self.color)

        # co-ordinate state of the (T,B)-phase digram
        self.phase_state = [self.Phase_Diagram.x, self.Phase_Diagram.y]

        # -------------------
        # Ising Model Widgets
        # -------------------
        self.sim_box_dim = [500, 500]
        self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#390A6B', "#FAF743"])
        self.Model = Model(self, self.color, self.phase_state, self.grid_scalings, self.phase_grid_dim, self.sim_box_dim, self.switch.get(), self.cmap)

        # ----------------
        # Widget Placement
        # ----------------

        self.switch_Frame.pack(side = 'top')
        self.Model.pack(side = 'top', pady = 5)
        self.Phase_Diagram.pack(side = 'top', pady = 5)

        # run
        self.mainloop()

    def switch_models(self):
        if self.switch.get():
            self.cmap = 'hsv'
            self.lbl_Model.configure(text = 'XY Model')
        else:
            self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#390A6B', "#FAF743"])
            self.lbl_Model.configure(text = 'Ising Model')

        # destroy then recreate model object with model_type changed
        self.Model.destroy()
        self.Model = Model(self, self.color, self.phase_state, self.grid_scalings, self.phase_grid_dim, self.sim_box_dim, self.switch.get(), self.cmap)

        # redo widget placement
        self.switch_Frame.pack_forget()
        self.Model.pack_forget()
        self.Phase_Diagram.pack_forget()
        self.switch_Frame.pack(side = 'top')
        self.Model.pack(side = 'top', pady = 5)
        self.Phase_Diagram.pack(side = 'top', pady = 5)

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Collection of objects that create the visual plot of the ising model
# ----------------------------------------------------------------------------------------------------
# ------------
# Model Widget
# ------------
class Model(ctk.CTkFrame):

    def __init__(self, parent, color, state, grid_scalings, phase_grid_dim, sim_box_dim, model_type, cmap):

        # __init__ from ctk.CTkframe()
        super().__init__(parent, fg_color = 'transparent')
        # color of the widget
        self.color = color
        # size of the widget
        self.sim_box_dim = sim_box_dim
        # type of thermodynamical model
        self.model_type = model_type
        # color of the lattice px squares
        self.cmap = cmap

        # ----------------
        # Phase Parameters
        # ----------------
        self.phase_state = state
        self.phase_grid_dim = phase_grid_dim
        self.grid_scalings = grid_scalings

        # --------------------
        # Interaction J Slider
        # --------------------
        J_frame = ctk.CTkFrame(self, fg_color = 'transparent')
        lbl_J = ctk.CTkLabel(J_frame, text = 'J', text_color = 'white', font = ('Arial', 18, 'bold'))

        self.J_var = tk.DoubleVar(value = 1)
        J_slider = ctk.CTkSlider(J_frame,
                                 orientation = 'vertical',
                                 height = 0.9 * self.sim_box_dim[1], width = 20,
                                 bg_color = 'transparent',
                                 button_color = '#FAF743', button_hover_color = '#DEDB26',
                                 progress_color = 'lightgray', fg_color = 'white',
                                 variable = self.J_var,
                                 from_ = 0,
                                 to = 1)
        J_slider.pack()
        lbl_J.pack(pady = 3)

        # ---------------------
        # Menu For Lattice Size
        # ---------------------
        sizes = ('64', '128', '256', '512')
        self.N_var = tk.IntVar(value = sizes[2])
        sizes_combo = ctk.CTkComboBox(self,
                                      button_color = '#FAF743', border_color = '#FAF743', fg_color = 'white', button_hover_color = '#DEDB26',
                                      text_color = '#1B1B1C', dropdown_fg_color = 'white',
                                      variable = self.N_var,
                                      values = sizes,
                                      command = lambda event : self.ising_model.refresh())


        # ---------------------
        # Ising Model Generator
        # ---------------------
        self.ising_model_frame = ctk.CTkFrame(self, fg_color = 'white')
        self.ising_model = IsingModel(self.ising_model_frame, self.phase_state, self.J_var, self.N_var, self.grid_scalings, self.color, self.phase_grid_dim, self.sim_box_dim, self.model_type, cmap)
        # ------------
        # Button Frame
        # ------------
        btn_frame = buttons(self, self.ising_model, self.grid_scalings, self.phase_grid_dim)


        J_frame.pack(side = 'right', padx = 0.02 * self.sim_box_dim[0])
        sizes_combo.pack(pady = 5)
        self.ising_model_frame.pack()
        self.ising_model.ctk_canvas.pack(padx = 5, pady = 5)
        btn_frame.pack(side = 'left', pady = 5)
        
# -----------
# Ising Model
# -----------
class IsingModel():

    def __init__(self, parent, state, interaction, lattice_size, grid_scalings, color, phase_grid_dim, sim_box_dim, model_type, cmap):

        # parent attribute
        self.parent = parent
        # color attribute
        self.color = color
        # phase digram size attribute
        self.phase_grid_dim = phase_grid_dim
        # simulation plot size
        self.sim_box_dim = sim_box_dim
        # type of model
        self.model_type = model_type

        # parameters for ising model
        self.N_var = lattice_size
        self.J_var = interaction
        self.phase_state = state # encodes (T,B)-state
        self.grid_scalings = grid_scalings

        # matplotlib figure
        self.ax = plt.subplot(111)
        self.fig = self.ax.figure
        self.ax.axis('off')

        # plot color same as root window color
        self.fig.patch.set_color(self.color)
        self.fig.tight_layout()

        # create FigureCanvas and embed into a CTkCanvas
        self.ctk_canvas = ctk.CTkCanvas(self.parent)
        self.canvas = FigureCanvasTkAgg(self.fig, self.ctk_canvas)
        self.canvas.get_tk_widget().pack(expand = True, fill = 'both')

        # FigureCanvas layout
        self.canvas.figure.tight_layout()
        self.canvas.get_tk_widget().configure(width = self.sim_box_dim[0], height = self.sim_box_dim[1])

        # color of the lattice px squares
        self.cmap = cmap

        # restarts to an initial configuration
        self.refresh()

        # pause attribute to start or stop the simulation
        self.pause = False

    # ---------------------
    # Initial Configuration
    # ---------------------
    def refresh(self):

        # creates an initial congfiguration with given N
        self.config = metro.ini_config(self.N_var.get(), self.model_type)

        # displays plot
        self.lattice_plot = self.ax.imshow(self.config, cmap = self.cmap)
        self.canvas.draw()

    # --------------
    # Run Simulation
    # --------------
    def update(self):

        # states on the coordinate grid is written in term of (x,y) px
        # scale the states to coincide with (T,B) ranges
        T = (self.phase_state[0].get() / self.phase_grid_dim[0]) * self.grid_scalings[0]
        B = (self.phase_state[1].get()/self.phase_grid_dim[1] - 0.5) * self.grid_scalings[1]

        # ensures no divide by zero error
        if T == 0:
            T = 10 ** -5

        # performs a Metropolis Algo sweep
        self.config = metro.sweep(self.config, B, self.J_var.get(), 1 / T, self.N_var.get(), self.model_type)
        # updates data
        self.lattice_plot.set_data(self.config)
        # displays results on canvas
        self.canvas.draw()

        # checks whether to keep running (update itself)
        if self.pause == False:
            # different sweep rates for size of model
            match self.N_var.get():
                case 512:
                    self.parent.after(25, self.update)
                case _:
                    self.parent.after(20, self.update)

# ------------
# Button Frame
# ------------
class buttons(ctk.CTkFrame):

    def __init__(self, parent, model, grid_scalings, grid_dim):

        # button frame
        super().__init__(parent, fg_color = 'transparent')

        # ------------
        # Start Button
        # ------------
        startBtn = ctk.CTkButton(self,
                                 text = '▶',
                                 fg_color = '#390A6B', hover_color = '#17022E',
                                 border_width = 2, border_color = 'white',
                                 width = 35, height = 35,
                                 command = lambda : start(model))
        
        # ------------
        # Pause Button
        # ------------
        pauseBtn = ctk.CTkButton(self,
                                 text = '⏸',
                                 fg_color = '#390A6B', hover_color = '#17022E',
                                 border_width = 2, border_color = 'white',
                                 width = 35, height = 35,
                                 command = lambda : pause(model))

        # ------------
        # Crit Button
        # ------------
        critBtn = ctk.CTkButton(self,
                                 text = 'Critical T',
                                 fg_color = '#390A6B', hover_color = '#17022E',
                                 border_width = 2, border_color = 'white',
                                 width = 35, height = 35,
                                 font = ('Arial', 12, 'bold'),
                                 command = lambda : critical_temp(model, grid_scalings, grid_dim))
        
        # --------------------
        # Button Functionality
        # --------------------

        # start simulation
        def start(model):
            model.pause = False
            model.update()

        # pause simulation
        def pause(model):
            model.pause = True

        def critical_temp(model, grid_scalings, grid_dim):
            crit_temp = 2 / math.log(1+math.sqrt(2))
            crit_temp_px = (crit_temp / grid_scalings[0]) * grid_dim[0]
            model.phase_state[0].set(crit_temp_px)
            model.phase_state[1].set(grid_dim[1]/2)

        # ----------------
        # Button Placement
        # ----------------
        self.columnconfigure((0,1,2,3,4,5,6, 7), weight = 1, uniform = 'a')
        self.rowconfigure(0, weight = 1, uniform = 'a')
        startBtn.grid(row = 0, column = 0, sticky = 'w', padx = 10)
        pauseBtn.grid(row = 0, column = 1, sticky = 'w')
        critBtn.grid(row = 0, column = 7, sticky = 'e')

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Collection of objects that create the interactive grid phase diagram
# ----------------------------------------------------------------------------------------------------
# ----------------
# Phase Diagram
# ----------------
class PhaseDiagram(ctk.CTkFrame):

    def __init__(self, parent, phase_grid_dim, grid_scalings, color):

        # __init__ from ctk.CTkframe()
        super().__init__(parent, fg_color = 'transparent')

        # color of the widget attribute
        self.color = color
        # size of the widget
        self.phase_grid_dim = phase_grid_dim
        # scaling ratio of the grid from px to unit (T,B)
        self.grid_scalings = grid_scalings

        # sets up co-ordinates as tkinter variables
        self.x = tk.DoubleVar()
        self.y = tk.DoubleVar()
        self.coordGrid = CoordinateGrid(self, self.x, self.y, self.phase_grid_dim, self.grid_scalings)
        self.grid_scalings = self.coordGrid.grid_scalings
 
        # initially start at critical point
        self.x.set(self.coordGrid.crit_temp_px) 
        self.y.set(self.phase_grid_dim[1] / 2)

        # ------------------
        # Coordiante Sliders
        # ------------------
        self.x_slider = ctk.CTkSlider(self,
                                      button_color = '#FAF743', button_hover_color = '#DEDB26',
                                      progress_color = 'lightgray', fg_color = 'white',
                                      variable = self.x,
                                      from_ = 0,
                                      to = self.phase_grid_dim[0],
                                      width = self.phase_grid_dim[0],
                                      command = lambda event: self.coordGrid.moves_pointer())
        self.y_slider = ctk.CTkSlider(self,
                                      button_color = '#FAF743', button_hover_color = '#DEDB26',
                                      progress_color = 'lightgray', fg_color = 'white',
                                      orientation = 'vertical',
                                      variable = self.y,
                                      from_ = 0,
                                      to = phase_grid_dim[1],
                                      height = self.phase_grid_dim[1],
                                      command = lambda event: self.coordGrid.moves_pointer())

        # --------------
        # Labelling Axis
        # --------------
        self.lbl_B_axis = ctk.CTkLabel(self, text = 'B', text_color = 'white', font = ('Arial', 12, 'bold'), fg_color = 'transparent', justify = 'center')
        self.lbl_B_axis.place(x = phase_grid_dim[0] * 1.26, y = phase_grid_dim[1] * 0.01)
        self.lbl_T_axis = ctk.CTkLabel(self, text = 'T', text_color = 'white', font = ('Arial', 12, 'bold'), fg_color = 'transparent')
        self.lbl_T_axis.place(x = phase_grid_dim[0] * 0, y = phase_grid_dim[1] * 1.23)

        # -----------------
        # Widget Placements
        # -----------------
        self.columnconfigure((0,1), weight = 1)
        self.rowconfigure((0,1), weight = 1)
        self.coordGrid.grid( row = 0, column  = 0, padx = 5, pady = 5)
        self.x_slider.grid(row = 1, column = 0, sticky = 'ew', pady = 15)
        self.y_slider.grid(row = 0, column = 1, sticky = 'ns', padx = 15)

# ---------------
# Coordinate Grid
# ---------------
class CoordinateGrid(ctk.CTkFrame):

    def __init__(self, parent, x, y, grid_dim, grid_scalings):

        super().__init__(parent, fg_color = 'lightgray', corner_radius = 2, width = grid_dim[0], height = grid_dim[1])

        # size of grid attribute
        self.grid_dim = grid_dim

        # create canvas for grid
        self.canvas = ctk.CTkCanvas(self, background = 'white',
                                    height = grid_dim[0],
                                    width = grid_dim[1])
        self.canvas.pack(fill = 'both', padx = 3, pady = 3)


        # draws grid
        self.num_div = [21,21]
        x_divisions = np.linspace(0, self.grid_dim[0], self.num_div[0])
        y_divisions = np.linspace(0, self.grid_dim[1], self.num_div[1])
        for div in x_divisions:
            self.canvas.create_line((div, 0), (div, self.grid_dim[1]), fill = 'lightgray', width = 1)
        for div in y_divisions:
            self.canvas.create_line((0, div), (self.grid_dim[0], div), fill = 'lightgray', width = 1)

        # grid scaling of (x,y) px co-ordinates to (T,B) phase diagram co-ordinates
        # 1 px in the x-direction is 3.5 units of temperature
        # 1 px in the y-direction is 2 units of magnetic field strength
        self.grid_scalings = grid_scalings

        # ----------
        # Phase Line
        # ----------
        # calculate critical temp
        crit_temp = 2 / math.log(1+math.sqrt(2))
        # calculate critcal temp in px units x
        self.crit_temp_px = (crit_temp / self.grid_scalings[0]) * self.grid_dim[0]
        self.canvas.create_line((0, self.grid_dim[1] / 2),
                                (self.crit_temp_px, self.grid_dim[1] / 2),
                                fill = 'red')

        # -------
        # Pointer
        # -------
        # pointer size
        self.dot_size = 0.05 * self.grid_dim[0]

        # define co-ordinates
        self.x = x
        self.y = y

        # starting location of pointer
        self.point = self.canvas.create_oval((self.crit_temp_px - self.dot_size/2, self.grid_dim[1]/2 - self.dot_size/2,
                                              self.crit_temp_px + self.dot_size/2, self.grid_dim[1]/2 + self.dot_size/2),
                                              fill = 'black')
        # moving pointer with mouse
        self.canvas.bind('<ButtonPress-1>', lambda event : self.canvas.bind('<Motion>', self.pointer_moves_sliders))
        self.canvas.bind('<ButtonRelease-1>', lambda event : self.canvas.unbind('<Motion>'))

    def pointer_moves_sliders(self, event):
        
        # max is used to ensure no negative pixels (no negative Temp)
        self.x.set(max(event.x, 0))
        self.y.set(self.grid_dim[1] - event.y)

        # move pointer
        self.moves_pointer()

    def moves_pointer(self):
        
        # deletes previous pointer as you move it
        self.canvas.delete(self.point)
        # creates new pointer at current slider/mouse location
        self.point = self.canvas.create_oval((self.x.get() - self.dot_size/2, self.grid_dim[1] - self.y.get() - self.dot_size/2,
                                              self.x.get() + self.dot_size/2, self.grid_dim[1] - self.y.get() + self.dot_size/2),
                                              fill = 'black')

        self.after(100, self.moves_pointer)

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------



# run program
root()