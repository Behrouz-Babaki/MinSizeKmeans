# MinSizeKmeans
A python implementation of KMeans clustering with minimum cluster size constraint (Bradley et al., 2000)[[1]](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2000-65.pdf)

Note that the paper suggests using a dedicated *minimum-cost network flow* algorithm for solving the subproblem, but in my implementation I use standard MIP solvers. My motivation for doing so was [this](https://groups.google.com/d/msg/gurobi/cnVL5nN2brU/REeTs6RCCAAJ) comment from Tobias Achterberg:
> If you have a pure network, then the constraint matrix is totally unimodular, so 
any vertex solution will be integral. And since the simplex algorithm always 
returns a vertex solution (if one exists), your solution will be integral. 
>
>Note that in our experience, a network simplex algorithm is not faster than the 
dual simplex, which is the reason why Gurobi does not provide a network simplex. 

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
