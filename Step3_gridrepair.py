"""

GRID repair

Takes The outputted netcdf files and makes the grids correct so they work with cdo remap

"""
#==============================================================================
__title__ = "Netcdf CMIP5 grid repair"
__author__ = "Arden Burrell"
__version__ = "1.0 (31.03.2018)"
__email__ = "arden.burrell@gmail.com"

#==============================================================================
import numpy as np 
import pandas as pd
import pdb
import sys
import os
import subprocess as subp
import argparse
import warnings as warn
#==============================================================================

def main(args):
	# ========== Load in the lookup table of the CMIP5 grids ==========
	# SOURCE: https://portal.enes.org/data/enes-model-data/cmip5/resolution
	grids     = pd.read_csv("./CMIP5model_lookup.csv", header=0)
	# ========== Set up the Key Infomation ==========
	# the downloaded senarios
	senarios  = ["historical_rcp8.5", "historical_rcp4.5", "historical_rcp2.6"]
	# the downloaded variables
	variables = ["pr", "tas"]

	# ========== Create a for loop to loop over every model ==========

	for sen in senarios:
		for var in variables:
			for model in grids["Model"]:
				repair_netcdf(sen, var, model, grids, args.force)
			# sys.exit()


#==============================================================================
def repair_netcdf(sen, var, model, grids, force):
	"""
	Repairs the grid of a given netcdf file
	"""
	# ========== Set the path and the file name ==========
	if var == "pr":
		units = "mm_month"
	elif var == "tas":
		units = "deg_C"
	else:
		raise ValueError("Unknown variable")

	path  = "./Processed_CMIP5_data/%s/%s/%s/" % (sen, var, model)
	fname = "%s_%s_%s_r1i1p1_%s_1950_2050_%s_regrid.nc" %(var, model, sen, units, sen)
	fout  = "%s_%s_%s_r1i1p1_%s_1950_2050_%s_setgrid.nc" %(var, model, sen, units, sen)
	
	# ========== Perform the checks on the path and file ==========
	if not os.path.isdir(path):
		# CHeck if the folder exists
		print ("Cannot find a dir for:", path)
		return

	if not os.path.isfile(path+fname):
		# check if the file exists with a different name
		for nx in range(0, 10):
			fname = "%s_%s_%s_r%di1p1_%s_1950_2050_%s_regrid.nc" %(
				var, model, sen, nx, units, sen)
			if os.path.isfile(path+fname):
				break
		if not os.path.isfile(path+fname):
			warn.warn(
				"WARNING: The file %s cannot be found, entering interactive debugging " 
				% fname)
			pdb.set_trace()

	if not force:
		# check if an existinf file exists
		if os.path.isfile(path+fout):
			print("A valid file already exists for: %s" % path)
			return

	# ========== Create a new grid ==========
	# Save the current grid
	subp.call("cdo griddes %s%s > %sGriddes" % (path, fname, path), shell=True)
	# open the current grid
	gfile    = open("%sGriddes" % path, "r") 
	# SPlit the lines
	ginfo    =  gfile.read().splitlines()
	# Check and see if the start is known
	if (
		any([n.startswith("xfirst") for n in ginfo])
		) or (
		any([n.startswith("xinc") for n in ginfo])
		):

		warn.warn("xfirst is listed in gridfile and will be overwritten")
		# pdb.set_trace()

	# Set the lines to be removed
	badel    = ["xvals", "yvals", "     ", "xbounds", "ybounds", "xfirst", "xinc"]
	# Create list to hold the new grid details
	new_grid = []

	for ginf in ginfo:
		test = []
		for be in badel:
			if ginf.startswith(be):
				test.append(False)
			elif ginf == "#":
				test.append(False)
			else:
				test.append(True)
		
		if all(test):
			new_grid.append(ginf)
	# Add the additional material
	new_grid.append('xfirst    = -180')
	new_grid.append('xinc      = %s' %  str(
		float(grids[grids["Model"]==model]["Longitude"]) ))
	

	# Check the y values, if they are missing use the ones in the original grid file
	if not (any([n.startswith("yfirst") for n in ginfo])):
		print ("Seting the y bounds")
		vals = []
		for glov in range(0,len(ginfo)):
			if  ginfo[glov].startswith("yvals"):
				vals.append(glov)
			elif ginfo[glov].startswith("ybounds"):
				vals.append(glov)
		if len (vals) == 2:
			sp = ""
			new_grid.append(sp.join(ginfo[vals[0]:vals[1]]))

		else:
			print("Warning"	)
			pdb.set_trace()
			raise IndexError("Bounding is incorrect")

	# Save the grid out
	save_grid(path, new_grid)

	# ========== Set the new grid file ==========
	# Save the current grid
	subp.call("cdo setgrid,%sGridFix %s%s %s%s" % (path, path, fname, path, fout), shell=True)
	print("A file built for: %s" % path)
	# pdb.set_trace()
#==============================================================================

def save_grid(path, grid):
	"""Takes a list of elements and save them too a grid"""
	with open((path+"GridFix"), 'w') as file_handler:
	    for item in grid:
	        file_handler.write("{}\n".format(item))

#==============================================================================

if __name__ == '__main__':
	description='Arguments for grid repair'
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument(
		"-f", "--force", action="store_true", 
		help="Force: create new netcdf even if a fixed one exists")
	args = parser.parse_args() 
	main(args)



