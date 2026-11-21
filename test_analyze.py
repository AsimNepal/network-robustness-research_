import unittest
import random
from analyze import add_edge, components, largest_component_fraction, attack_order, resilience_curve, area_under_curve, erdos_renyi, watts_strogatz, barabasi_albert

class NetworkTests(unittest.TestCase):
    def test_path(self):
        g=[set() for _ in range(4)]
        for i in range(3):add_edge(g,i,i+1)
        self.assertEqual(largest_component_fraction(g,[]),1)
        self.assertEqual(largest_component_fraction(g,[1]),.5)
        self.assertEqual(attack_order(g,'degree',random.Random(1)),[1,2,0,3])
    def test_auc(self):self.assertAlmostEqual(area_under_curve([1,.5,0],[0,.5,1]),.5)
    def test_graphs(self):
        for g in [erdos_renyi(30,.2,random.Random(1)),watts_strogatz(30,4,.2,random.Random(1)),barabasi_albert(30,2,random.Random(1))]:
            self.assertEqual(len(g),30)
            self.assertTrue(all(u in g[v] for v in range(30) for u in g[v]))
            for strategy in ['random','degree','adaptive_degree']:
                curve=resilience_curve(g,strategy,random.Random(1),[0,.5,1])
                self.assertEqual(curve[-1],0)
                self.assertTrue(all(curve[i]>=curve[i+1] for i in range(len(curve)-1)))

if __name__=='__main__':unittest.main()
