# MinSizeKmeans
A python implementation of KMeans clustering with minimum cluster size constraint (Bradley et al., 2000)[[1]](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2000-65.pdf)

## Usage 
```
usage: ./run_mskmeans.py [data file] [k] [minimum size] [#iterations] [result file]
```
To see a run of algorithm on example data, run the script `minsize_kmeans/example_run.sh`

## Dependencies
This program uses [Pulp](https://pythonhosted.org/PuLP/) to solve the *assignment subproblem*. 
You should also have a MIP solver (Gurobi, Cplex, Cbc, etc.) installed and have it configured to work with Pulp. 


## References
1. Bradley, P. S., K. P. Bennett, and Ayhan Demiriz. "Constrained k-means clustering." Microsoft Research, Redmond (2000): 1-8.