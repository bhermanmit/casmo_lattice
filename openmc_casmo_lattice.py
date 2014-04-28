# Takes a casmo file output file as an argument and creates openmc files

# Packages
import sys
import os
import re
from optparse import OptionParser

# OpenCSG packages
sys.path.append(os.path.join('opencsg', 'opencsg'))
from material import *
from surface import *
from universe import *
from geometry import *
from mesh import *

# Parse command line options
parser = OptionParser()
parser.add_option('-i', '--input', dest='input',
                  help="CASMO (.out) file name.")
(options, args) = parser.parse_args()

# Initialize global variables 
univ = 0
pin_dict = {}
mat_dict = {}

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

class Pin(object):

    def __init__(self, name, cas_pin):
        self.name = name
        self.radii = []
        self.mats = []
        self.active = False

        # set up unique universe
        global univ
        univ += 1
        self.univ = univ

        # process pin
        self.process_casmo(cas_pin)

        print(self.name)
        print(self.radii)
        print(self.mats)

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

    # Test pin
    apin = Pin('PIN4_ROD', casmo.pins['PIN4_ROD'])

if __name__ == '__main__':
    main()
