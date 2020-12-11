import unittest

from genetic_algorithm.evolutionary_decision_tree import EvolutionaryDecisionTree
from simulator.HashDecisionTree import HashDecisionTree
from simulator.decision_tree import DecisionTree


class DecisionTreeTest(unittest.TestCase):

    def create_tree(self):
        cls = HashDecisionTree
        #cls = EvolutionaryDecisionTree
        return cls(['brainy', 'wings'], ['human', 'bird', 'mammal'], cls.branch_node('brainy',
                                   cls.leaf_node('human'),
                                   cls.branch_node('wings', cls.leaf_node('bird'), cls.leaf_node('mammal'))))

    def test_decide(self):
        tree = self.create_tree()
        self.assertEqual('human', tree.decide({ 'brainy': True, 'wings': False}))
        self.assertEqual('bird', tree.decide({ 'brainy': False, 'wings': True}))
        self.assertEqual('mammal', tree.decide({ 'brainy': False, 'wings': False}))

    def test_size(self):
        tree = self.create_tree()
        self.assertEqual(5, tree.size())

    def test_traverse(self):
        tree = self.create_tree()
        node_counter = DecisionTree.Counter()
        leaf_counter = DecisionTree.Counter()
        tree.breadth_first_traverse(node_counter, leaf_counter)
        self.assertEqual(2, node_counter.count)
        self.assertEqual(3, leaf_counter.count)

if __name__ == '__main__':
    unittest.main()
