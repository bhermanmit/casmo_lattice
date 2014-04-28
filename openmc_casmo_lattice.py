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

class CASMO(object):

    def __init__(self, filename):

      # Initialize CASMO class attributes
      self.filename = filename
      self.lines = ''
      self.lattice_lines = []
      self.material = {}
      self.pins = {}

      # Run parsing methods
      if not self.filename.endswith('.out'):
          raise Exception('Input file must be a CASMO .out file.')
      self.read_file_contents()
      self.find_lattice_lines()
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
                self.mats.append(pin_list[i])

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
