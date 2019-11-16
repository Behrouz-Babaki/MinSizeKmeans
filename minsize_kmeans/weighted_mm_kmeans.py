#!/usr/bin/env python3.5
# coding: utf-8

import pulp
import random
import argparse

def l2_distance(point1, point2):
    return sum([(float(i)-float(j))**2 for (i,j) in zip(point1, point2)])

class subproblem(object):
    def __init__(self, centroids, data, weights, min_weight, max_weight):

        self.centroids = centroids
        self.data = data
        self.weights = weights
        self.min_weight = min_weight
        self.max_weight= max_weight
        self.n = len(data)
        self.k = len(centroids)

        self.create_model()

    def create_model(self):
        def distances(assignment):
            return l2_distance(self.data[assignment[0]], self.centroids[assignment[1]])

        assignments = [(i, j) for i in range(self.n) for j in range(self.k)]

        # assignment variables
        self.y = pulp.LpVariable.dicts('data-to-cluster assignments',
                                  assignments,
                                  lowBound=0,
                                  upBound=1,
                                  cat=pulp.LpInteger)

        # create the model
        self.model = pulp.LpProblem("Model for assignment subproblem", pulp.LpMinimize)

        # objective function
        self.model += pulp.lpSum([distances(assignment) * self.weights[assignment[0]] * self.y[assignment] for assignment in assignments]), 'Objective Function - sum weighted squared distances to assigned centroid'
        # this is also weighted, otherwise the weighted centroid computation don't make sense.

        # constraints on the total weights of clusters
        for j in range(self.k):
            self.model += pulp.lpSum([self.weights[i] * self.y[(i, j)] for i in range(self.n)]) >= self.min_weight, "minimum weight for cluster {}".format(j)
            self.model += pulp.lpSum([self.weights[i] * self.y[(i, j)] for i in range(self.n)]) <= self.max_weight, "maximum weight for cluster {}".format(j)

        # make sure each point is assigned at least once, and only once
        for i in range(self.n):
            self.model += pulp.lpSum([self.y[(i, j)] for j in range(self.k)]) == 1, "must assign point {}".format(i)

    def solve(self):
        self.status = self.model.solve()

        clusters = None
        if self.status == 1:
            clusters= [-1 for i in range(self.n)]
            for i in range(self.n):
                for j in range(self.k):
                    if self.y[(i, j)].value() > 0:
                        clusters[i] = j
        return clusters

def initialize_centers(dataset, k):
    """
    sample k random datapoints as starting centers
    """
    ids = list(range(len(dataset)))
    random.shuffle(ids)
    return [dataset[id] for id in ids[:k]]

def compute_centers(clusters, dataset,weights=None):
    """
    weighted average of datapoints to determine centroids
    """
    if weights is None:
        weights = [1]*len(dataset)
    # canonical labeling of clusters
    ids = list(set(clusters))
    c_to_id = dict()
    for j, c in enumerate(ids):
        c_to_id[c] = j
    for j, c in enumerate(clusters):
        clusters[j] = c_to_id[c]

    k = len(ids)
    dim = len(dataset[0])
    cluster_centers = [[0.0] * dim for i in range(k)]
    cluster_weights = [0] * k
    for j, c in enumerate(clusters):
        for i in range(dim):
            cluster_centers[c][i] += dataset[j][i] * weights[j]
        cluster_weights[c] += weights[j]
    for j in range(k):
        for i in range(dim):
            cluster_centers[j][i] = cluster_centers[j][i]/float(cluster_weights[j])
    return clusters, cluster_centers

def minsize_kmeans_weighted(dataset, k, weights=None, min_weight=0, max_weight=None,max_iters=999,uiter=None):
    """
    @dataset - numpy matrix (or list of lists) - of point coordinates
    @k - number of clusters
    @weights - list of point weights, length equal to len(@dataset)
    @min_weight - minimum total weight per cluster
    @max_weight - maximum total weight per cluster
    @max_iters - if no convergence after this number of iterations, stop anyway
    @uiter - iterator like tqdm to print a progress bar.
    """
    n = len(dataset)
    if weights is None:
        weights = [-1]*n
    if max_weight == None:
        max_weight = sum(weights)
    uiter = uiter or list

    centers = initialize_centers(dataset, k)
    clusters = [-1] * n

    for ind in uiter(range(max_iters)):
        m = subproblem(centers, dataset, weights, min_weight, max_weight)
        clusters_ = m.solve()
        if not clusters_:
            return None, None
        clusters_, centers = compute_centers(clusters_, dataset)

        converged = all([clusters[i]==clusters_[i] for i in xrange(n)])
        clusters = clusters_
        if converged:
            break

    return clusters, centers

def read_data(datafile):
    data = []
    with open(datafile, 'r') as f:
        for line in f:
            line = line.strip()
            if line != '':
                d = [float(i) for i in line.split()]
                data.append(d)
    return data

def read_weights(weightfile):
    weights = []
    with open(weightfile, 'r') as f:
        for line in f:
            weights += [float(i) for i in line.strip().split()]
    return weights

def cluster_quality(cluster):
    if len(cluster) == 0:
        return 0.0

    quality = 0.0
    for i in range(len(cluster)):
        for j in range(i, len(cluster)):
            quality += l2_distance(cluster[i], cluster[j])
    return quality / len(cluster)

def compute_quality(data, cluster_indices):
    clusters = dict()
    for i, c in enumerate(cluster_indices):
        if c in clusters:
            clusters[c].append(data[i])
        else:
            clusters[c] = [data[i]]
    return sum(cluster_quality(c) for c in clusters.values())

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', help='file containing the coordinates of instances')
    parser.add_argument('k', help='number of clusters', type=int)
    parser.add_argument('weightfile', help='file containing the weights of instances')
    parser.add_argument('min_weight', help='minimum total weight for each cluster', type=float)
    parser.add_argument('max_weight', help='maximum total weight for each cluster', type=float)
    parser.add_argument('-n', '--NUM_ITER', type=int,
                        help='run the algorithm for NUM_ITER times and return the best clustering',
                        default=1)
    parser.add_argument('-o', '--OUTFILE', help='store the result in OUTFILE',
                        default='')
    args = parser.parse_args()

    data = read_data(args.datafile)
    weights = read_weights(args.weightfile)

    best = None
    best_clusters = None
    for i in range(args.NUM_ITER):
        clusters, centers = minsize_kmeans_weighted(data, args.k, weights,
                                           args.min_weight, args.max_weight)
        if clusters:
            quality = compute_quality(data, clusters)
            if not best or (quality < best):
                best = quality
                best_clusters = clusters

    if best:
        if args.OUTFILE:
            with open(args.OUTFILE, 'w') as f:
                f.write('\n'.join(str(i) for i in best_clusters))
        else:
            print('cluster assignments:')
            for i in range(len(best_clusters)):
                print('%d: %d'%(i, best_clusters[i]))
        print('sum of squared distances: %.4f'%(best))
    else:
        print('no clustering found')


