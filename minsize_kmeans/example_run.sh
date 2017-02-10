#!/bin/bash

# Example 1:

# Run k-means on the data stored in the file ../data/iris.data
# number of clusters: 3
# Each cluster should contain at least 2 points
# Run the algorithm only once
# Store the results in the file clusters.out
./run_mskmeans.py ../data/iris.data 3 2 1 ./clusters.out


# Example 2:

# Run k-means on the data stored in the file ../data/iris.data
# number of clusters: 3
# Each cluster should contain at least 2 and at most 100 points
# Run the algorithm only once
# Store the results in the file clusters_mm.out
./minmax_kmeans.py ../data/iris.data 3 2 100 1 clusters_mm.out
