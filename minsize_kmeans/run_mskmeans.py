#!/usr/bin/env python3.5
# coding: utf-8

import pulp
import random
import sys

def l2_distance(point1, point2):
    return sum([(float(i)-float(j))**2 for (i,j) in zip(point1, point2)])

class subproblem(object):
    def __init__(self, centroids, data, min_size):

        self.centroids = centroids
        self.data = data
        self.min_size = min_size
        self.n = len(data)
        self.k = len(centroids)

        self.create_model()

    def create_model(self):
        def distances(assignment):
            return l2_distance(self.data[assignment[0]], self.centroids[assignment[1]])

        clusters = list(range(self.k))
        assignments = [(i, j)for i in range(self.n) for j in range(self.k)]

        # outflow variables for data nodes
        self.y = pulp.LpVariable.dicts('data-to-cluster assignments',
                                  assignments,
                                  lowBound=0,
                                  upBound=1,
                                  cat=pulp.LpInteger)

        # outflow variables for cluster nodes
        self.b = pulp.LpVariable.dicts('cluster outflows',
                                  clusters,
                                  lowBound=0,
                                  upBound=self.n-self.min_size,
                                  cat=pulp.LpContinuous)

        # create the model
        self.model = pulp.LpProblem("Model for assignment subproblem", pulp.LpMinimize)

        # objective function
        self.model += sum([distances(assignment) * self.y[assignment] for assignment in assignments])

        # flow balance constraints for data nodes
        for i in range(self.n):
            self.model += sum(self.y[(i, j)] for j in range(self.k)) == 1

        # flow balance constraints for cluster nodes
        for j in range(k):
            self.model += sum(self.y[(i, j)] for i in range(self.n)) - self.min_size == self.b[j]

        # flow balance constraint for the sink node
        self.model += sum(self.b[j] for j in range(self.k)) == self.n - (self.k * min_size)


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
    ids = list(range(len(dataset)))
    random.shuffle(ids)
    return [dataset[id] for id in ids[:k]]

def compute_centers(clusters, dataset):
    # canonical labeling of clusters
    ids = list(set(clusters))
    c_to_id = dict()
    for j, c in enumerate(ids):
        c_to_id[c] = j
    for j, c in enumerate(clusters):
        clusters[j] = c_to_id[c]

    k = len(ids)
    dim = len(dataset[0])
    centers = [[0.0] * dim for i in range(k)]
    counts = [0] * k
    for j, c in enumerate(clusters):
        for i in range(dim):
            centers[c][i] += dataset[j][i]
        counts[c] += 1
    for j in range(k):
        for i in range(dim):
            centers[j][i] = centers[j][i]/float(counts[j])
    return clusters, centers

def minsize_kmeans(dataset, k, min_size=0):

    centers = initialize_centers(dataset, k)
    clusters = [-1] * len(dataset)

    converged = False
    while not converged:
        m = subproblem(centers, data, min_size)
        clusters_ = m.solve()
        if not clusters_:
            return None, None
        clusters_, centers = compute_centers(clusters_, dataset)

        converged = True
        i = 0
        while converged and i < len(dataset):
            if clusters[i] != clusters_[i]:
                converged = False
            i += 1
        clusters = clusters_

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
    if len(sys.argv) < 6:
        print('usage: %s [data file] [k] [minimum size] [#iterations] [result file]'%sys.argv[0])
        exit(1)

    data = read_data(sys.argv[1])
    k = int(sys.argv[2])
    min_size = int(sys.argv[3])
    iterations = int(sys.argv[4])

    best = None
    best_clusters = None
    for i in range(iterations):
        clusters, centers = minsize_kmeans(data, k, min_size)
        if clusters:
            quality = compute_quality(data, clusters)
            if not best or (quality < best):
                best = quality
                best_clusters = clusters
    
    if best:
        with open(sys.argv[5], 'a') as f:
            print('\n'.join(str(i) for i in clusters), file=f)
    else:
        print('no clustering found')


