"""

GRID repair

Takes The outputted netcdf files and makes the grids correct so they work with cdo remap

"""
__title__ = "Netcdf CMIP5 grid repair"
__author__ = "Arden Burrell"
__version__ = "1.0 (31.03.2018)"
__email__ = "arden.burrell@gmail.com"


import numpy as np 
import pandas as pd
import pdb
import sys


def main():
	# ========== Load in the lookup table of the CMIP5 grids ==========
	# SOURCE: https://portal.enes.org/data/enes-model-data/cmip5/resolution
	grids     = pd.read_csv("./CMIP5model_lookup.csv", index_col=0)

	# ========== Set up the Key Infomation ==========
	# the downloaded senarios
	senarios  = ["historical_rcp8.5", "historical_rcp4.5", "historical_rcp2.6"]
	# the downloaded variables
	variables = ["pr", "tas"]

	# ========== Create a for loop to loop over every model ==========

	for sen in senarios:
		for var in variables:
			for model in grids["Model"]:
				print (model)
			sys.exit()




	pdb.set_trace()
	pass





if __name__ == '__main__':
	main()



