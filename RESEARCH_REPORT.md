# When Do Networks Break? A Computational Study of Network Resilience

**Research report | Independent computational project | November 2026**

## Abstract

This study compares how three synthetic network families respond to node failures. We generate 12 graphs each from an Erdős–Rényi random graph, a Watts–Strogatz small-world graph, and a Barabási–Albert preferential-attachment graph, each with 80 nodes. We then remove nodes using random, static high-degree, and adaptive high-degree strategies. Resilience is quantified by the largest connected component as a fraction of the original network size, and summarized using the area under the removal curve. The results illustrate how targeted removal can produce very different outcomes across network structures. The experiment is a reproducible illustration of established network-science concepts, not a new mathematical discovery.

## Question and hypothesis

**Question:** How does network topology influence robustness to random failure versus targeted attack?

**Hypothesis:** Preferential-attachment graphs will be especially vulnerable to removal of highly connected nodes, relative to random node removal. This is a hypothesis tested in a finite synthetic setting, not a universal statement about all networks.

## Mathematical framework

Let G=(V,E) be an undirected simple graph with n=|V| nodes. For a removal order π and removal fraction f∈[0,1], remove the first round(fn) nodes of π. Let L(G,π,f) denote the size of the largest connected component of the remaining graph. Define

R(G,π,f) = L(G,π,f) / n.

The denominator remains the **original** n, so R(0) may be below 1 for a disconnected starting graph. The overall resilience score is

A(G,π) = ∫₀¹ R(G,π,f) df,

approximated by the trapezoidal rule over 21 evenly spaced values of f. A higher A means more original nodes remain in the largest connected component across the removal process. A is a descriptive summary, not a significance test.

### Removal strategies

1. Random: shuffle nodes with a seeded random number generator and remove in that order.
2. Static degree: sort nodes by their initial degrees, highest first, with node ID as a tie-breaker.
3. Adaptive degree: at every removal step, choose the node with highest degree among nodes still present, with node ID as a tie-breaker.

### Graph families

- Erdős–Rényi: 80 nodes, independent edges with probability 4/79.
- Watts–Strogatz: 80 nodes, four initial ring neighbors, rewiring probability 0.15.
- Barabási–Albert: 80 nodes, two preferentially selected existing neighbors for each added node.

All graph generators are implemented using only the Python standard library. The families have similar approximate mean degree, but are not exactly matched for edge count, clustering, path length, or connectivity.

## Experimental design

- Fixed random seed: 20261121.
- 12 independent generated graphs per family.
- 3 attack strategies per graph.
- Removal fractions 0, 0.05, ..., 1.00.
- Total: 3 × 12 × 3 = **108 graph-strategy runs**, 2,268 curve observations.
- Code: `analyze.py`; tests: `test_analyze.py`.

## Results

Mean resilience AUC by graph family and attack strategy (rounded to four decimals):

| Graph family | Random removal | Static high-degree | Adaptive high-degree |
|---|---:|---:|---:|
| Erdős–Rényi | 0.4299 | 0.2982 | 0.2447 |
| Watts–Strogatz | 0.3929 | 0.3645 | 0.2647 |
| Barabási–Albert | 0.4118 | 0.1456 | 0.1363 |

The preferential-attachment graphs retain much less connectivity under high-degree removal than under random removal in these simulations. The small-world family has relatively similar AUC under random and static-degree removal, but shows greater damage under adaptive-degree removal. See `resilience_chart.svg` for the mean curves and `experiment_summary.csv` for every replicate.

These are descriptive means from a small synthetic experiment. The code does not calculate uncertainty intervals or statistical significance. No inference about real road, communication, or power networks follows directly from this table.

## Limitations

1. Only three synthetic families and one main parameter choice per family are tested.
2. The number of nodes is modest (n=80), with 12 replicates per family.
3. Edge counts and structural features are not strictly matched across families.
4. Node removal is a simplified abstraction of infrastructure failure; there are no weights, capacities, traffic demands, or cascading failures.
5. AUC weights all removal fractions equally and can hide important threshold effects.
6. Static and adaptive high-degree attacks use deterministic node-ID tie-breaks, which may affect small graphs.

## Next steps suitable for a faculty-mentored extension

- Match graph families by exact edge count and connectedness before comparing robustness.
- Increase replicate counts and report bootstrap confidence intervals.
- Compare degree attack with betweenness-centrality attack.
- Add weighted links, traffic assignment, or cascading failure models to connect network resilience to Braess's Paradox.
- Analyze the critical removal fraction at which the largest component drops below a chosen threshold.
- Read and cite foundational network robustness literature before claiming novelty.

## Suggested starting literature

- Albert, R., Jeong, H., & Barabási, A.-L. (2000). Error and attack tolerance of complex networks. *Nature*, 406, 378–382.
- Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. *Nature*, 393, 440–442.
- Erdős, P., & Rényi, A. (1959). On random graphs I. *Publicationes Mathematicae*, 6, 290–297.

These are reading suggestions, not a claim that this study independently validates every result in those papers.
