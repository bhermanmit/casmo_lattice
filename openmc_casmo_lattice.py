# Takes a casmo file output file as an argument and creates openmc files

# Packages
import sys
import os
import re
from optparse import OptionParser
from core2D import *

# Parse command line options
parser = OptionParser()
parser.add_option('-i', '--input', dest='input',
                  help="CASMO (.out) file name.")
(options, args) = parser.parse_args()

pin_lattice ="""
{nw:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {no:>4} {ne:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {pa:>4} {fp:>4} {fp:>4} {pb:>4} {fp:>4} {fp:>4} {pc:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {pd:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {pe:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {pf:>4} {fp:>4} {fp:>4} {pg:>4} {fp:>4} {fp:>4} {ph:>4} {fp:>4} {fp:>4} {pi:>4} {fp:>4} {fp:>4} {pj:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {pk:>4} {fp:>4} {fp:>4} {pl:>4} {fp:>4} {fp:>4} {pm:>4} {fp:>4} {fp:>4} {pn:>4} {fp:>4} {fp:>4} {po:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {pp:>4} {fp:>4} {fp:>4} {pq:>4} {fp:>4} {fp:>4} {pr:>4} {fp:>4} {fp:>4} {ps:>4} {fp:>4} {fp:>4} {pt:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {pu:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {pv:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {pw:>4} {fp:>4} {fp:>4} {px:>4} {fp:>4} {fp:>4} {py:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{we:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {fp:>4} {ea:>4}
{sw:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {so:>4} {se:>4}
"""

class CASMO(object):

    def __init__(self, filename):

      # Initialize CASMO class attributes
      self.filename = filename
      self.lines = ''
      self.lattice_lines = []
      self.lattice_sym = None 
      self.pin_pitch = None
      self.assy_pitch = None
      self.material = {}
      self.pins = {}

      # Run parsing methods
      if not self.filename.endswith('.out'):
          raise Exception('Input file must be a CASMO .out file.')
      self.read_file_contents()
      self.find_lattice_lines()
      self.find_lattice_info()
      self.find_material_lines()
      self.find_pin_lines()

    def read_file_contents(self):

        # Open file and read contents
        with open(self.filename, 'r') as fh:
            self.lines = fh.read().splitlines()

    def find_lattice_lines(self):
        read_lattice = False
        for aline in self.lines:
            if re.search('Pin numbers \(input/internal\)', aline):
                read_lattice = True
                continue
            if re.search('Number of pin types \(full assembly\):', aline):
                break
            if not read_lattice:
                continue
            if aline is not '':
                self.lattice_lines.append(aline)

    def find_lattice_info(self):
        first_true = True
        for aline in self.lines:
            if re.search('PWR', aline):
                pwrline = aline
                if first_true:
                    first_true = False
                else:
                    break
        pwrline = pwrline.split('*')[0]
        pwrline = pwrline.replace(',','')
        pwrline = pwrline.split()
        self.pin_pitch = pwrline[2]
        self.pin_pitch = pwrline[3]
        self.lattice_sym = pwrline[-1]
        print(self.lattice_sym)

    def print_lattice_lines(self):
        print('CASMO lattice:')
        for aline in self.lattice_lines:
            print(aline)
            
    def find_material_lines(self):
        read_materials = False
        matline = []
        matname = ''
        for aline in self.lines:
            if re.search('Composition name, Material number', aline):
                read_materials = True
                continue
            if re.search('Dancoff factor map', aline):
                break
            if not read_materials:
                continue
            if aline is not '':
                sline = aline.split()
                if len(sline[0]) == 3:
                    if len(matline) > 0:
                        self.material.update({matname:matline})
                    matname = sline[0]
                    matline = []
                    matline.append(aline)
                else:
                    matline.append(aline)
                    
    def print_material_lines(self):
        for key in self.material:
            print('Material {0}'.format(key))
            print(self.material[key])
            print('')
            
    def find_pin_lines(self):
        read_pins = False
        read_pin = False
        pinline = []
        pinname = ''
        for aline in self.lines:
            if re.search('List of CASMO5 Input Cards \(', aline):
                read_pins = True
                continue
            if re.search('List of CASMO5 Input Cards Complete', aline):
                break
            if not read_pins:
                continue
            if aline.strip() is not '':
                sline = aline.split()
                if re.search('PIN', sline[0]):
                    if len(pinline) > 0:
                        if not re.search('ROD', ''.join(pinline)):
                            self.pins.update({pinname:pinline})
                        else:
                            self.pins.update({pinname+'_ROD':pinline})
                    read_pin = True
                    pinname = sline[0]+sline[1]
                    pinline = []
                    pinline.append(aline)

                # takes care of additional lines in pin
                elif read_pin:
                    if not re.search('^            ', aline):
                        read_pin = False
                        if not re.search('ROD', ''.join(pinline)):
                            self.pins.update({pinname:pinline})
                        else:
                            self.pins.update({pinname+'_ROD':pinline})
                        pinline = []
                        continue
                    pinline.append(aline)

    def print_pin_lines(self):
        for key in self.pins:
            print('{0}'.format(key))
            print(self.pins[key])
            print('')              

class CASMOMaterial(object):
    def __init__(self, name, cas_mat):
        self.name = name
        self.nuclide_names = []
        self.nuclide_fracs = []

        # convert from casmo
        self.process_casmo(cas_mat)

        # create python object
        self.create_object()

    def process_casmo(self, cas_mat):

        nuclide_start = True

        # create one big string
        mat_str = ''.join(cas_mat)
        mat_list = mat_str.split()

        # loop around str and start at index 4
        for i in range(len(mat_list)):
            if i < 3:
                continue

            # check for = sign
            if mat_list[i] == '=':
                continue

            # read in nuclide
            if nuclide_start:
                nuclide_name = mat_list[i].replace('=', '')
                self.nuclide_names.append(nuclide_name)
                nuclide_start = False
            else:
                nuclide_frac = float(mat_list[i])/1.0e24
                self.nuclide_fracs.append(nuclide_frac)
                nuclide_start = True

    def create_object(self):
        mat_obj = Material(self.name, self.name)
        for name, frac in zip(self.nuclide_names, self.nuclide_fracs):
            mat_obj.add_nuclide(name, '71c', frac)
        mat_dict.update({self.name:mat_obj})

class CASMOPin(object):

    def __init__(self, name, cas_pin):
        self.name = name
        self.radii = []
        self.mats = []
        self.active = False

        # process pin
        self.process_casmo(cas_pin)

        # create python object
        self.create_object()

    def process_casmo(self, cas_pin):

        radii_lines = True
        mat_lines = False

        # create one long string
        pin_str = ''.join(cas_pin)
        pin_list = pin_str.split()

        # loop around str and start at index 2
        for i in range(len(pin_list)):
            if i < 2:
                continue

            # check for separator between radii and mats
            a = pin_list[i]
            if pin_list[i] == '/':
                radii_lines = False
                mat_lines = True
                continue

            # Check for final separators
            if pin_list[i] == '//' or pin_list[i] == '*':
                break

            # add radii to list
            if radii_lines:
                self.radii.append(pin_list[i])

            # add material to list
            if mat_lines:
                matname = pin_list[i].replace("'","")
                self.mats.append(matname)

    def create_object(self):

        i_surf = 0
        i_cell = 0

        # loop over radii and mats
        for radii, mat in zip(self.radii, self.mats):

            # add the surface
            i_surf += 1
            add_surface(self.name+'{0}'.format(i_surf), 'z-cylinder', '0.0 0.0 {0}'.format(radii))

            # get the material id (BOX and CAN equivalent)
            if mat == 'BOX':
                mat = 'CAN'
            if mat == 'AIC':
                mat = 'CAN' 
            matid = mat_dict[mat].id

            # add the cell
            i_cell += 1
            if i_surf == 1:
                add_cell(self.name+'{0}'.format(i_cell), '-{0}'.format(i_surf), universe=self.name, material=matid)
            else:
                add_cell(self.name+'{0}'.format(i_cell), ' {0} -{1}'.format(i_surf-1, i_surf), universe=self.name, material=matid)

def main():

    # Check for input file
    if options.input is None:
        raise Exception('Must specify input file.')

    # Parse CASMO file
    casmo = CASMO(options.input)

    # Process Materials from CASMO lines into Python objects
    for matkey in casmo.material:
        CASMOMaterial(matkey, casmo.material[matkey])

    # Process Pins from CASMO lines into Python objects
    for pinkey in casmo.pins:
        CASMOPin(pinkey, casmo.pins[pinkey])

    # Write out all files
    write_files()

def write_files():

############ Geometry File ##############

    # Heading info
    geo_str = ""
    geo_str += \
"""<?xml version="1.0" encoding="UTF-8"?>\n<geometry>\n\n"""

    # Write out surfaces
    for item in surf_dict.keys():
        geo_str += surf_dict[item].write_xml()

    # Write out cells
    geo_str += "\n"
    for item in cell_dict.keys():
        geo_str += cell_dict[item].write_xml()

    # Write out lattices
    geo_str += "\n"
    for item in lat_dict.keys():
        geo_str += lat_dict[item].write_xml()

    # Write out footer info
    geo_str += \
"""\n</geometry>"""
    with open('geometry.xml','w') as fh:
        fh.write(geo_str)

############ Materials File ##############

    # Heading info
    mat_str = ""
    mat_str += \
"""<?xml version="1.0" encoding="UTF-8"?>\n<materials>\n\n"""

    # Write out materials
    for item in mat_dict.keys():
        mat_str += mat_dict[item].write_xml()
        mat_str += "\n"

    # Write out footer info
    mat_str += \
"""</materials>"""
    with open('materials.xml','w') as fh:
        fh.write(mat_str)
    

if __name__ == '__main__':
    main()
