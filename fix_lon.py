"""

GRID repair

Takes a netcdf file name as argument and fixes the lon grid


"""
#==============================================================================
__title__ = "Netcdf CMIP5 grid repair"
__author__ = "Arden Burrell"
__version__ = "1.0 (04.04.2018)"
__email__ = "arden.burrell@gmail.com"

#==============================================================================
# Import packages
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
	grids   = pd.read_csv("./CMIP5model_lookup.csv", header=0)

	# ========== Set up the Key Infomation ==========
	fname   = args.fname
	# fname = "/srv/ccrc/data45/z3466821/CMIP5fetch/Processed_CMIP5_data/historical_rcp8.5/pr/ACCESS1-0/Merged_pr_ACCESS1-0_historical_rcp8.5_lonfix.nc"

	# ========== Create a for loop to loop over every model ==========
	fcleanup = repair_netcdf(fname, grids)


#==============================================================================
def repair_netcdf(fname, grids):
	"""
	Repairs the grid of a given netcdf file
	"""

	# ========== Set the path and the file name ==========
	# fname = "%s_%s_%s_r1i1p1_%s_1950_2050_%s_regrid.nc" %(var, model, sen, units, sen)
	fout  = "%s_setgrid.nc" % (fname)
	
	# ========== Create a list of files to cleanup ==========
	cleanup = []

	# ========== Check if the file exists ==========
	if not os.path.isfile(fname+".nc"):
		# check if the file exists with a different name
		raise IOError("WARNING: The file %s cannot be found"% fname)

	# ========== Create a new grid ==========
	# Save the current grid
	subp.call("cdo griddes %s.nc > %sGriddes" % (fname, fname), shell=True)
	# add the griddes to the cleanup 
	cleanup.append("%sGriddes" % fname)

	# open the current grid
	gfile    = open("%sGriddes" % fname, "r") 
	# Split the lines of the grid file
	ginfo    =  gfile.read().splitlines()
	# Check and see if the start is known
	if (
		any([n.startswith("xfirst") for n in ginfo])
		) or (
		any([n.startswith("xinc") for n in ginfo])
		):
		warn.warn("xfirst is listed in gridfile and will be overwritten")
		pdb.set_trace()
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
	pdb.set_trace()
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
		'fname', type=str, 
		help='The fname of the netcdf to have its grid repaired')
	args = parser.parse_args() 
	main(args)


