"""

GRID repair

Takes The outputted netcdf files and makes the grids correct so they work with cdo remap

"""

import numpy as np 
import pandas as pd
import pdb


def main():
	# Load in the lookup table of the CMIP5 grids
	# SOURCE: https://portal.enes.org/data/enes-model-data/cmip5/resolution
	grids = pd.read_csv("./CMIP5model_lookup.csv", index_col=0)
	pdb.set_trace()
	pass


if __name__ == '__main__':
	main()



