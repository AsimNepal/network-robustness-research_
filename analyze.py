"""Reproducible network resilience experiments. Python standard library only."""
from __future__ import annotations
import argparse, csv, itertools, math, random
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def add_edge(g, a, b):
    if a != b:
        g[a].add(b); g[b].add(a)

def erdos_renyi(n, p, rng):
    g = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p: add_edge(g, i, j)
    return g

def barabasi_albert(n, m, rng):
    if not 1 <= m < n: raise ValueError('require 1 <= m < n')
    g = [set() for _ in range(n)]
    for i in range(m + 1):
        for j in range(i): add_edge(g, i, j)
    for v in range(m + 1, n):
        pool = [u for u in range(v) for _ in range(len(g[u]))]
        targets = set()
        while len(targets) < m:
            targets.add(rng.choice(pool))
        for u in targets: add_edge(g, v, u)
    return g

def watts_strogatz(n, k, beta, rng):
    if k % 2 or not 0 < k < n: raise ValueError('k must be even and between 0 and n')
    g = [set() for _ in range(n)]
    original = [(u, (u + d) % n) for u in range(n) for d in range(1, k // 2 + 1)]
    for u, v in original: add_edge(g, u, v)
    for u, v in original:
        if rng.random() < beta:
            g[u].remove(v); g[v].remove(u)
            choices = [w for w in range(n) if w != u and w not in g[u]]
            if choices: add_edge(g, u, rng.choice(choices))
            else: add_edge(g, u, v)
    return g

def components(g, active):
    unseen = set(active); sizes = []
    while unseen:
        start = unseen.pop(); queue = [start]; count = 1
        for u in queue:
            for v in g[u] & unseen:
                unseen.remove(v); queue.append(v); count += 1
        sizes.append(count)
    return sizes

def largest_component_fraction(g, removed):
    active = set(range(len(g))) - set(removed)
    return max(components(g, active), default=0) / len(g)

def attack_order(g, strategy, rng):
    n = len(g)
    if strategy == 'random':
        order = list(range(n)); rng.shuffle(order); return order
    if strategy == 'degree':
        return sorted(range(n), key=lambda u: (-len(g[u]), u))
    if strategy == 'adaptive_degree':
        remaining = set(range(n)); order = []
        while remaining:
            u = min(remaining, key=lambda v: (-len(g[v] & remaining), v))
            order.append(u); remaining.remove(u)
        return order
    raise ValueError(strategy)

def resilience_curve(g, strategy, rng, fractions):
    order = attack_order(g, strategy, rng)
    return [largest_component_fraction(g, order[:int(round(f * len(g)))]) for f in fractions]

def area_under_curve(values, fractions):
    return sum((fractions[i] - fractions[i - 1]) * (values[i] + values[i - 1]) / 2
               for i in range(1, len(values)))

def run(n=80, replicates=12, seed=20261121):
    fractions = [i / 20 for i in range(21)]
    families = ['random_graph', 'small_world', 'preferential_attachment']
    strategies = ['random', 'degree', 'adaptive_degree']
    rows, summaries = [], []
    for family in families:
        for rep in range(replicates):
            rng = random.Random(seed + 100000 * families.index(family) + rep)
            if family == 'random_graph': g = erdos_renyi(n, 4 / (n - 1), rng)
            elif family == 'small_world': g = watts_strogatz(n, 4, .15, rng)
            else: g = barabasi_albert(n, 2, rng)
            edges = sum(map(len, g)) // 2
            for strategy in strategies:
                attack_rng = random.Random(seed + 1000000 * families.index(family) + 1000 * rep + strategies.index(strategy))
                values = resilience_curve(g, strategy, attack_rng, fractions)
                auc = area_under_curve(values, fractions)
                summaries.append(dict(family=family, replicate=rep, strategy=strategy, n=n, edges=edges, auc=round(auc, 6), at_25pct=round(values[5], 6), at_50pct=round(values[10], 6)))
                for f, val in zip(fractions, values):
                    rows.append(dict(family=family, replicate=rep, strategy=strategy, fraction_removed=f, largest_component_fraction=round(val, 6)))
    return rows, summaries

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def write_svg(path, rows, n_reps):
    families = ['random_graph', 'small_world', 'preferential_attachment']
    strategies = ['random', 'degree', 'adaptive_degree']
    colors = {'random':'#2377bd','degree':'#db7935','adaptive_degree':'#bd355d'}
    W,H=1050,390
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="white"/>', '<style>text{font-family:Arial,sans-serif;fill:#233348} .small{font-size:11px} .title{font-size:15px;font-weight:bold}</style>']
    for fi,family in enumerate(families):
        x0=40+fi*345; y0=48; pw=265; ph=255
        parts.append(f'<text x="{x0}" y="22" class="title">{family.replace("_"," ").title()}</text>')
        for t in [0,.25,.5,.75,1]:
            y=y0+ph*(1-t); parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+pw}" y2="{y:.1f}" stroke="#e5eaf0"/>')
            parts.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" class="small">{t:g}</text>')
        parts.append(f'<path d="M{x0} {y0} V{y0+ph} H{x0+pw}" fill="none" stroke="#566477"/>')
        for strategy in strategies:
            coords=[]
            for j in range(21):
                f=j/20
                vals=[r['largest_component_fraction'] for r in rows if r['family']==family and r['strategy']==strategy and abs(r['fraction_removed']-f)<1e-9]
                avg=sum(vals)/len(vals)
                coords.append(f'{x0+pw*f:.1f},{y0+ph*(1-avg):.1f}')
            parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{colors[strategy]}" stroke-width="2.5"/>')
        parts.append(f'<text x="{x0+pw/2}" y="{y0+ph+28}" text-anchor="middle" class="small">Fraction of nodes removed</text>')
        for t in [0,.5,1]:parts.append(f'<text x="{x0+pw*t}" y="{y0+ph+15}" text-anchor="middle" class="small">{t:g}</text>')
    for i,s in enumerate(strategies):
        x=225+i*225
        parts.append(f'<line x1="{x}" y1="365" x2="{x+30}" y2="365" stroke="{colors[s]}" stroke-width="3"/>')
        parts.append(f'<text x="{x+36}" y="369" class="small">{s.replace("_"," ")}</text>')
    parts.append('</svg>');path.write_text('\n'.join(parts),encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--n',type=int,default=80);p.add_argument('--replicates',type=int,default=12);p.add_argument('--seed',type=int,default=20261121)
    args=p.parse_args()
    if args.n < 8 or args.replicates < 1: p.error('n must be >=8 and replicates >=1')
    rows, summaries=run(args.n,args.replicates,args.seed)
    write_csv(ROOT/'resilience_curves.csv',rows);write_csv(ROOT/'experiment_summary.csv',summaries)
    write_svg(ROOT/'resilience_chart.svg',rows,args.replicates)
    print('Generated',len(summaries),'graph-strategy runs,',len(rows),'curve points')
    for fam in sorted(set(r['family'] for r in summaries)):
        for strat in ['random','degree','adaptive_degree']:
            vals=[r['auc'] for r in summaries if r['family']==fam and r['strategy']==strat]
            print(f'{fam:26} {strat:17} mean AUC={sum(vals)/len(vals):.4f}')

if __name__=='__main__':main()
