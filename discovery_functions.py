from main import *

stats = Stats()

# расшифровать гены, создав разбойника с ними и выведя обусловленную ими экипировку:
def discover_genes(genes_list):
    test_rogue = Rogue(genes_list, 0, genes_can_mutate=False)

genes_list = [1, 3, 1, 1, 1, 0, 1]
discover_genes(genes_list)
