# для работы со временем:
from datetime import datetime
from time import time

# для некоторых операций:
from random import randrange, randint

# импортировать другие файлы проекта:
from operations_with_files import *
from charts_functions import *

# импортировать необходимый набор словарей с экипировкой:
from equipment_custom import *
#from equipment_wow_classic import *
#from equipment_obvious_strong import *
#from equipment_obvious_weak import *


# класс Популяции
class Population():
    """Класс используется для удобной работы с популяцией"""

    # счётчик всех разбойников:
    how_many_rogues = 0

    # счётчик живых разбойников:
    how_many_rogues_alive = 0

    # счётчик поколений:
    generations = 0
    
    
    # при создании популяции сразу же наполнить её:
    def __init__(self, total):
        while total > 0:
            # создать нового разбойника, передав "пустой генотип" и отметку о том, что ему нужно сгенерировать гены:
            new_rogue = Rogue('', 0, from_parent=False)

            # пополнить список разбойников:
            ROGUES_LIST.append(new_rogue)

            total -= 1


    # вывести актуальную информацию о популяции:
    def __str__(self):
        text = 'Популяция:\n'
        text += 'поколений: ' + str(self.generations) + '\n'
        text += 'всего субъектов: ' + str(self.how_many_rogues) + '\n'
        text += 'живых субъектов: ' + str(self.how_many_rogues_alive) + '\n'

        return text


# класс Разбойника
class Rogue():
    """Класс описывает механику тестируемого персонажа."""

    # при создании экземпляра:
    def __init__(self, genes_list_inherited, parent_generation, from_parent=True):

        # строки с предыдущего проекта...

        # статистические счётчики:
        Population.how_many_rogues += 1
        Population.how_many_rogues_alive += 1

        # номер поколения:
        self.my_generation = parent_generation + 1
        if self.my_generation > Population.generations:
            Population.generations = self.my_generation

        # жив ли:
        self.alive = True

        # счётчики побед и поражений:
        self.my_wins = 0
        self.my_defeats = 0

        # инициализировать цепочку генов:
        self.my_genes = [0] * 7

        # если этот разбойник порождён другим разбойником, его гены должны незначительно мутировать:
        if from_parent:
            genes_list = self.mutate_genes(genes_list_inherited)
            self.my_genes = genes_list
        else:
            self.generate_random_genes()


    # сгенерировать случайный набор генов:
    def generate_random_genes(self):
        self.my_genes[0] = randrange(0,len(RIGHT_HANDS))     # <-- для правой руки:
        self.my_genes[1] = randrange(0, len(LEFT_HANDS))     # <-- для левой руки:
        self.my_genes[2] = randrange(0, len(GLOVES))         # <-- для рукавиц:
        self.my_genes[3] = randrange(0, len(HEADS))          # <-- для головы:
        self.my_genes[4] = randrange(0, len(CHESTS))         # <-- для нагрудника:
        self.my_genes[5] = randrange(0, len(PANTS))          # <-- для штанов:
        self.my_genes[6] = randrange(0, len(BOOTS))          # <-- для обуви:

        print(self.my_genes)
    
    # произвести мутацию в указанном гене:
    def mutate_gene(self, gene_id):
        current_value = self.my_genes[gene_id]
        new_value = -1
        while new_value != current_value:
            pass
        

    # унаследовать родительские гены с вероятностью мутации:
    def mutate_genes(self, parent_genes):

        # произойдёт ли мутация вообще:
        event_mutation = randint(1, 3)

        # # если мутация НЕ должна произойти::
        if event_mutation < 3:
            self.my_genes = parent_genes
        
        # если мутация должна произойти:
        else:
            # определить "силу" мутации, которая обуславливает количество мутировавших генов:
            mutation_volume = randint(0, 30)
            mutation_iters = 1
            if 16 <= mutation_volume <= 25:
                mutation_iters = 2
            elif 26 <= mutation_volume <= 30:
                mutation_iters = 3
            
            # список уже мутировавших генов, чтобы исключить "перезапись" мутации в уже мутировавшем гене:
            genes_mutated = []

            current_iter = 0
            while current_iter < mutation_iters:
                gene_with_forced_mutation = randint(0, GENES_CHAIN_LENGTH)
                
                # если этот ген не внесён в список уже мутировавших генов:
                if gene_with_forced_mutation not in genes_mutated:
                    self.mutate_gene(gene_with_forced_mutation)
                    genes_mutated.append(gene_with_forced_mutation)
                    current_iter += 1
                else: # иначе перейти на следующую итерацию без сдвига счётчика
                    continue
    

    # "применить" гены путём надевания обусловленной ими экипировки:
    def apply_genes(self):
        pass
        # self.wear_item(0, self.my_genes[0])
        # self.wear_item(1, self.my_genes[1])
        # self.wear_item(2, self.my_genes[2])


    # оформить победу в дуэли:
    def do_win(self):
        self.my_wins += 1
        if self.my_wins % 2 == 0:
            self.spawn_new_rogue(self.my_genes, True)


    # оформить поражение в дуэли:
    def do_defeat(self):
        self.my_defeats += 1
        if self.my_defeats == 2:
            self.die()


    # родить нового разбойника:
    def spawn_new_rogue(self, parent_genes, from_parent):
        new_rogue = Rogue(self.my_genes, self.my_generation, from_parent=True)
        ROGUES_LIST.append(new_rogue)


    # погибнуть:
    def die(self):
        self.alive = False
        Population.how_many_rogues_alive -= 1


    # методы с предыдущего проекта...



# провести череду соревнований:
def perform_challenges_serie():
    pass
    # цикл - пока не достигнут верх популяции
    counter = 0
    while counter < Population.how_many_rogues_alive:
        pass


# провести соревнование между двумя разбойниками:
def perform_challenge(rogue_1, rogue_2):
    sum_of_damage_1 = rogue_1.do_battle()
    sum_of_damage_2 = rogue_2.do_battle()

    # раскидать очки между победителем и проигравшим:
    if sum_of_damage_1 > sum_of_damage_2:
        rogue_1.do_win()
        rogue_2.do_defeat()
    elif sum_of_damage_1 < sum_of_damage_2:
        rogue_1.do_defeat()
        rogue_2.do_win()
    else:
        print('О чудо! Произошла ничья!')


# ЗАПУСК:
if __name__ == '__main__':

    # КОНСТАНТЫ:
    GENES_CHAIN_LENGTH = 0  # <-- длина цепочки генов (должна совпадать с количеством словарей экипировки)

    # создать список, где будут храниться ссылки на всех разбойников:
    ROGUES_LIST = list()

    # создать объект популяции и наполнить его разбойниками в указанном количестве:
    new_population = Population(3)

    #ROGUES_LIST[2].die()

    # "прочитать" популяцию:
    print(new_population)

else:
    print('__name__ is not "__main__".')
