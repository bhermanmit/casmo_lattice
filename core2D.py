#!/usr/bin/env python2

# Packages
from collections import OrderedDict

# Global Dictionaries
surf_dict = OrderedDict() 
cell_dict = OrderedDict() 
mat_dict = OrderedDict()
univ_dict = OrderedDict()
lat_dict = OrderedDict()
plot_dict = OrderedDict()
axial_dict = OrderedDict()
assy_dict = OrderedDict()

# Item counters
n_materials = 0
n_surfaces = 0
n_cells = 0
n_universes = 0
n_lattices = 0
n_plots = 0

# Class Definitions
class Element(object):
    def __init__(self, name, xs, value):
        self.name = name
        self.xs = xs
        self.value = value

    def display(self):
        print '    Name: {0}'.format(self.name)
        print '    XS: {0}'.format(self.xs)
        print '    Value: {0}'.format(self.value)

    def write_xml(self):
        xml_str = ""
        xml_str += """    <element name="{name}" xs="{xs}" ao="{value}" />\n""".format(name = self.name, xs = self.xs, value = self.value)
        return xml_str

class Nuclide(object):
    def __init__(self, name, xs, value):
        self.name = name
        self.xs = xs
        self.value = value

    def display(self):
        print '    Name: {0}'.format(self.name)
        print '    XS: {0}'.format(self.xs)
        print '    Value: {0}'.format(self.value)

    def write_xml(self):
        xml_str = ""
        xml_str += """    <nuclide name="{name}" xs="{xs}" ao="{value}" />\n""".format(name = self.name, xs = self.xs, value = self.value)
        return xml_str

class Sab(object):
    def __init__(self, name, xs):
        self.name = name
        self.xs = xs

    def display(self):
        print '    Name: {0}'.format(self.name)
        print '    XS: {0}'.format(self.xs)

    def write_xml(self):
        xml_str = ""
        xml_str += """    <sab name="{name}" xs="{xs}" />\n""".format(name = self.name, xs = self.xs)
        return xml_str

class Material(object):
    def __init__(self, key, comment = None):
        global n_materials
        n_materials += 1
        self.id = n_materials
        self.elements = []
        self.nuclides = []
        self.sab = None
        self.key = key
        self.comment = comment
        self.color = None 

    def add_element(self, name, xs, value):
        self.elements.append(Element(name, xs, value))

    def add_nuclide(self, name, xs, value):
        self.nuclides.append(Nuclide(name, xs, value))

    def add_sab(self, name, xs):
        self.sab = Sab(name, xs)

    def add_color(self, color):
        self.color = color

    def finalize(self):
        if mat_dict.has_key(self.key):
            raise Exception('Material not finalized because of duplicate key - '+self.key)
        mat_dict.update({self.key:self})

    def display(self):
        print '\nMaterial ID: {0}'.format(self.id)
        print 'Elements:'
        for item in self.elements:
            item.display()
        print 'Nuclides:'
        for item in self.nuclides:
            item.display()
        print 'S(a,b):'
        self.sab.display()
        if self.comment != None:
            print 'Comment: {0}'.format(self.comment)
        if self.color != None:
            print 'Color: {0}'.format(self.color)

    def write_xml(self):
        xml_str = ""
        if self.comment != None:
            xml_str += """  <!--{0:^40}-->\n""".format(self.comment)
        xml_str += """  <material id="{id:>6}">\n""".format(id = self.id)
        xml_str += """    <density units="sum" />\n"""
        for item in self.elements:
            xml_str += item.write_xml()
        for item in self.nuclides:
            xml_str += item.write_xml()
        if self.sab != None:
            xml_str += self.sab.write_xml()
        xml_str += """  </material>\n"""
        return xml_str

class Surface(object):
    def __init__(self, type, coeffs = "", bc=None, comment=None):
        global n_surfaces
        n_surfaces += 1
        self.id = n_surfaces
        self.type = type
        self.coeffs = coeffs
        self.bc = bc
        self.comment = comment

    def display(self):
        print '\nSurface ID: {0}'.format(self.id)
        print 'TYPE: {0}'.format(self.type)
        print 'COEFFICIENTS: {0}'.format(self.coeffs)
        if self.bc != None:
            print 'Boundary Condition: {0}'.format(self.bc)
        if self.comment != None:
            print 'COMMENT: {0}'.format(self.comment)

    def write_xml(self):
        xml_str = ""
        if self.bc == None:
          xml_str += """  <surface id="{id:>6}" type="{type:<17}" coeffs="{coeffs:>25}"/>""".format(id = self.id, type = self.type, coeffs = self.coeffs)
        else:
          xml_str += """  <surface id="{id:>6}" type="{type:<17}" coeffs="{coeffs:>25}" boundary="{bc}"/>""".format(id = self.id, type = self.type, coeffs = self.coeffs, bc = self.bc)
        if self.comment != None:
            xml_str += """  <!--{0:^40}-->""".format(self.comment)
        xml_str += "\n"
        return xml_str

class Universe(object):
    def __init__(self, value=None):
        global n_universes
        if value != None:
            self.id = value 
        else:
            n_universes += 1
            self.id = n_universes
        self.cells = []

    def add_cell(self, key):
        self.cells.append(key)

    def display(self):
        print '\nUniverse ID: {0}'.format(self.id)
        print 'Cells: {0}'.format(self.cells)

class Cell(object):
    n_cells = 0
    def __init__(self, surfaces, universe=None, fill=None, material=None, comment=None):
        global n_cells
        n_cells += 1
        self.id = n_cells
        self.fill = fill
        self.material = material
        self.surfaces = surfaces
        self.universe = universe
        self.comment = comment
        self.checked = False

        # check cell setup
        self.checked = self.check_cell()
        if not self.checked:
            raise Exception('Cell needs fill or material!')

    def check_cell(self):
        if self.fill == None and self.material == None:
            return False
        if self.fill != None and self.material != None:
            return False
        return True

    def display(self):
        print '\nCell ID {0}'.format(self.id)
        if self.fill != None:
            print 'Fill: {0}'.format(self.fill)
        if self.material != None:
            print 'Material: {0}'.format(self.material)
        print 'Surfaces: {0}'.format(self.surfaces)
        print 'Universe: {0}'.format(self.universe)
        if self.comment != None:
            print 'Comment: {0}'.format(self.comment)

    def write_xml(self):
        xml_str = ""
        if self.fill == None:
          xml_str += """  <cell id="{id:>6}" universe="{univ:<6}" material="{mat:>6}" surfaces="{surfs:>12}"/>""".format(id = self.id, univ = self.universe, mat = self.material, surfs = self.surfaces)
        else:
          xml_str += """  <cell id="{id:>6}" universe="{univ:<6}" fill="{fill:>10}" surfaces="{surfs:>12}"/>""".format(id = self.id, univ = self.universe, fill = self.fill, surfs = self.surfaces)
        if self.comment != None:
            xml_str += """  <!--{0:^40}-->""".format(self.comment)
        xml_str += "\n"
        return xml_str
        

class Lattice(object):
    def __init__(self, dimension, lower_left, width, universes, comment=None):
        global n_lattices, n_universes
        n_lattices += 1
        n_universes += 1
        self.id = n_universes
        self.type = "rectangular"
        self.dimension = dimension
        self.lower_left = lower_left
        self.width = width
        self.universes = universes 
        self.comment = comment

        # Get lattice dimension
        self.nx = dimension.split()[0]
        self.ny = dimension.split()[1]

    def display(self):
        print '\nLattice ID: {0}'.format(self.id)
        print 'Type: {0}'.format(self.type)
        print 'Dimension: {0}'.format(self.dimension)
        print 'Lower Left: {0}'.format(self.lower_left)
        print 'Width: {0}'.format(self.width)
        print 'Universes: {0}'.format(self.universes)
        if self.comment != None:
          print 'Comment: {0}'.format(self.comment)

    def write_xml(self):
        xml_str = "\n"
        if self.comment != None:
            xml_str += """  <!--{0:^40}-->\n""".format(self.comment)
        xml_str += """  <lattice id="{id:>6}" type="{type}" dimension="{dim}">\n""".format(id = self.id, type = self.type, dim = self.dimension)
        xml_str += """    <lower_left>{lleft}</lower_left>\n""".format(lleft = self.lower_left)
        xml_str += """    <width>{width}</width>\n""".format(width = self.width)
        xml_str += """    <universes>{univs}    </universes>\n""".format(univs = self.universes)
        xml_str += """  </lattice>\n"""
        return xml_str

class Assembly(object):
    def __init__(self, enr = '0.0', bp = '0', u = None, wid = '0'):
        self.enr = enr
        if bp == None:
            bp = '0'
        self.bp = bp
        self.u = u
        self.wid = wid
        self.density = '0.0' 
        self.fueltemp = '0.0'

    def add_universe(self, u):
        self.u = u

    def add_waterid(self, wid):
        self.wid = wid

    def add_density(self, density):
        self.density = density

    def add_fueltemp(self, fueltemp):
        self.fueltemp = fueltemp

class Plot(object):
    def __init__(self, origin, width, basis, type='slice', color='mat', pixels="1000 1000", background='255 255 255', filename=None, comment=None):
        global n_plots
        n_plots += 1
        self.id = n_plots
        self.origin = origin
        self.width = width
        self.basis = basis
        self.type = type
        self.color = color
        self.pixels = pixels
        self.background = background
        self.filename = filename
        if self.filename == None:
            self.filename = 'plot_{0}'.format(self.id)
        self.comment = comment

    def display(self):
        print '\nPlot ID: {0}'.format(self.id)
        print 'Origin: {0}'.format(self.origin)
        print 'Width: {0}'.format(self.width)
        print 'Basis: {0}'.format(self.basis)
        print 'Type: {0}'.format(self.type)
        print 'Color: {0}'.format(self.color)
        print 'Pixels: {0}'.format(self.pixels)
        print 'Background: {0}'.format(self.background)
        print 'Filename: {0}'.format(self.filename)
        if self.comment != None:
            print 'Comment: {0}'.format(self.comment)

    def write_xml(self):
        xml_str = "\n"
        if self.comment != None:
            xml_str += """  <!--{0:^40}-->\n""".format(self.comment)
        xml_str += """  <plot id="{id}" type="{type}" color="{col}">\n""".format(id = self.id, type = self.type, col = self.color)
        xml_str += """      <filename>{fname}</filename>\n""".format(fname = self.filename)
        xml_str += """      <origin> {origin} </origin>\n""".format(origin = self.origin)
        xml_str += """      <width> {width} </width>\n""".format(width = self.width)
        xml_str += """      <basis> {basis} </basis>\n""".format(basis = self.basis)
        xml_str += """      <pixels>{pixels}</pixels>\n""".format(pixels = self.pixels)
        xml_str += """      <background>{background}</background>\n""".format(background = self.background)
        for item in mat_dict.keys():
            if mat_dict[item].color != None:
                xml_str += """      <col_spec id="{id}" rgb="{rgb}"/>\n""".format(id = mat_dict[item].id, rgb = mat_dict[item].color)
        xml_str += """  </plot>\n"""
        return xml_str

class AxialRegion(object):
    def __init__(self, bottom, top, dp, grid, water_idx, cool_rho):
        self.bottom = bottom
        self.top = top
        self.dp = dp
        self.grid = grid
        self.water_idx = water_idx
        self.cool_rho = cool_rho

    def display(self):
        print 'Bottom: {0} {1}'.format(self.bottom, surf_dict[self.bottom].coeffs)
        print '  Dashpot: {0}'.format(self.dp)
        print '  Grid: {0}'.format(self.grid)
        print ' Water Index: {0}'.format(self.water_idx)
        print ' Water Density: {0}'.format(self.cool_rho)
        print 'Top: {0} {1}'.format(self.top, surf_dict[self.top].coeffs)

# Global Routines
def add_surface(key, type, coeffs, bc=None, comment=None):
    if surf_dict.has_key(key):
        raise Exception('Duplicate surface key - '+key)
    surf_dict.update({key:Surface(type, coeffs, bc, comment)})

def add_cell(key, surfaces, universe=None, fill=None, material=None, comment=None):
    if cell_dict.has_key(key):
        raise Exception('Duplicate cell key - '+key)

    # Get universe ID
    if universe == None:
        if not univ_dict.has_key('global'):
            univ_dict.update({'global':Universe(0)})
        univ_dict['global'].add_cell(key)
        universe = univ_dict['global'].id
    elif univ_dict.has_key(universe):
        univ_dict[universe].add_cell(key)
        universe = univ_dict[universe].id
    else:
        univ_dict.update({universe:Universe()})
        univ_dict[universe].add_cell(key)
        universe = univ_dict[universe].id

    # Add the cell
    cell_dict.update({key:Cell(surfaces, universe, fill, material, comment)})

def add_lattice(key, dimension, lower_left, width, universes, comment=None):
    if lat_dict.has_key(key):
         raise Exception('Duplicate lattice key - '+key)
    lat_dict.update({key:Lattice(dimension, lower_left, width, universes, comment)})

def add_plot(key, origin, width, basis, type='slice', color='mat', pixels="1000 1000", background='255 255 255', filename=None, comment=None):
    if plot_dict.has_key(key):
         raise Exception('Duplicate plot key - '+key)
    plot_dict.update({key:Plot(origin, width, basis, type, color, pixels, background, filename, comment)})
def add_axial(key, bottom, top, dp, grid, water_idx, cool_rho):
    if axial_dict.has_key(key):
        raise Exception('Duplicate axial key - '+key)
    axial_dict.update({key:AxialRegion(bottom, top, dp, grid, water_idx, cool_rho)})
