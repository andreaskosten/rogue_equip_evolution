# для работы со временем:
from datetime import datetime
from time import time, sleep

# для некоторых операций:
from random import randrange, randint, choice

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
    how_many_rogues = 1

    # счётчик живых разбойников:
    how_many_rogues_alive = 0

    # счётчик поколений:
    generations = 0


    # при создании популяции сразу же наполнить её:
    def __init__(self, total):
        while total > 0:

            # создать нового разбойника, передав "пустой генотип" и отметку о том, что ему нужно сгенерировать гены:
            new_rogue = Rogue('', 0, from_parent=False, rogues_counter=str(self.how_many_rogues))

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
    def __init__(self, genes_list_inherited, parent_generation, from_parent=True, rogues_counter='error'):

        # инициализация списка слотов экипировки, который должен содержать id надетых предметов:
        # 0 - правая рука, 1 - левая рука, 2 - перчатки, 3 - голова, 4 - грудь, 5 - штаны, 6 - обувь
        self.equipment_slots = [0] * 7

        # инициализация списка слотов экипировки, который должен содержать названия надетых предметов:
        self.equipment_names = ['ничего'] * 7

        # БАЗОВЫЕ значения характеристик (они - точка отсчёта при смене экипировки):
        self.basic_stat_agility = 50
        self.basic_stat_power = 40
        self.basic_stat_hit = 80
        self.basic_stat_crit = 20
        self.basic_stat_mastery = 0

        # рассчитать текущие характеристики без вещей:
        self.set_stats_without_equip()

        # "имя" разбойника:
        self.name = rogues_counter + '-й, из поколения ' + str(parent_generation+1)

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
            self.mutate_genes(genes_list_inherited, dbg=True)
        else:
            self.generate_random_genes(dbg=True)

        # надеть экипировку согласно полученным генам:
        self.apply_genes(dbg=True)


    # метод для расчёта текущих характеристик без вещей:
    def set_stats_without_equip(self):
        self.stat_agility = self.basic_stat_agility
        self.stat_power = self.basic_stat_power
        self.stat_attackpower = self.stat_agility + self.stat_power
        self.stat_hit = self.basic_stat_hit
        self.direct_crit_bonus = 0
        self.calculate_critical_percent()
        self.stat_mastery = self.basic_stat_mastery
        self.calculate_glancing_percent()


    # метод для расчёта шанса критического удара:
    def calculate_critical_percent(self):
        self.stat_crit = self.basic_stat_crit + self.direct_crit_bonus + self.stat_agility // 20


    # метод для расчёта шанса скользящего удара:
    def calculate_glancing_percent(self):
        self.stat_glancing_percent = 40 - self.stat_mastery * 4


    # сгенерировать случайный набор генов:
    def generate_random_genes(self, dbg=False):
        self.my_genes[0] = randrange(1, len(RIGHT_HANDS))    # <-- для правой руки:
        self.my_genes[1] = randrange(1, len(LEFT_HANDS))     # <-- для левой руки:
        self.my_genes[2] = randrange(1, len(GLOVES))         # <-- для рукавиц:
        self.my_genes[3] = randrange(1, len(HEADS))          # <-- для головы:
        self.my_genes[4] = randrange(1, len(CHESTS))         # <-- для нагрудника:
        self.my_genes[5] = randrange(1, len(PANTS))          # <-- для штанов:
        self.my_genes[6] = randrange(1, len(BOOTS))          # <-- для обуви:

        if dbg:  # для отладки:
            print('\nf "generate_random_genes":' + '\n\tgenes generated:\n\t', end='')
            print(self.my_genes)


    # унаследовать родительские гены с вероятностью мутации:
    def mutate_genes(self, parent_genes, dbg=False):

        # взять за основу родительские гены:
        self.my_genes = parent_genes.copy()

        # произойдёт ли мутация вообще:
        event_mutation = randint(1, 10)

        # если мутация НЕ должна произойти, больше тут делать нечего:
        if event_mutation == 10:
            if dbg:  # для отладки:
                print('\nf "mutate_genes" begins and ends:' + '\n\tмутация НЕ состоялась\n\told genes: ', end='')
                print(parent_genes)
                print('\tnew genes: ', end='')
                print(self.my_genes)
            return 0

        # если мутация должна произойти:
        else:
            # определить "силу" мутации = количество мутировавших генов:
            mutation_volume = randint(0, 30)
            mutation_iters = 1
            if 16 <= mutation_volume <= 28:
                mutation_iters = 2
            elif 29 <= mutation_volume <= 30:
                mutation_iters = 3

            mutation_iters = 5

            if dbg:  # для отладки:
                print('\nf "mutate_genes" begins:' + '\n\tmutation_iters (мутаций запланировано): ' + str(mutation_iters))

            # список генов, доступных для мутации:
            genes_available = [0, 1, 2, 3, 4, 5, 6]

            # список мутировавших генов:
            genes_mutated = []

            current_iter = 0
            while current_iter < mutation_iters:
                if dbg:  # для отладки:
                    print('\tw1')
                gene_with_forced_mutation = choice(genes_available)
                if gene_with_forced_mutation not in genes_mutated:
                    self.mutate_gene(gene_with_forced_mutation, dbg=True)
                    genes_mutated.append(gene_with_forced_mutation)
                    current_iter += 1
                    if dbg:  # для отладки:
                        print('\tcurrent_iter =', current_iter)
                else:
                    if dbg:  # для отладки:
                        print('\telse, because ' + str(gene_with_forced_mutation) + ' not in genes_mutated')

        if dbg:  # для отладки:
            genes_mutated_str = ''
            if len(genes_mutated) > 1:
                for x in genes_mutated:
                    genes_mutated_str += str(x) + ', '
            else:
                genes_mutated_str = str(genes_mutated[0])
            print('\nf "mutate_genes" ends:' + '\n\told genes: ', end='')
            print(parent_genes)
            print('\tgenes_mutated: ' + genes_mutated_str)
            print('\tnew genes: ', end='')
            print(self.my_genes)


    # произвести мутацию в указанном гене, изменив его значение на любое другое:
    def mutate_gene(self, gene_id, dbg=False):
        current_value = self.my_genes[gene_id]
        new_value = current_value

        if dbg:  # для отладки:
            print('\nf "mutate_gene":' + '\n\tgene_id: ' + str(gene_id) + '\n\told gene value: ' + str(current_value))

        tries = 0
        while new_value == current_value:
            if dbg:  # для отладки:
                print('\tw2, because ' + str(new_value) + ' = ' + str(current_value) )
            new_value = randrange(0, len(LINKS_TO_EQUIP_DICTS[gene_id]))
            self.my_genes[gene_id] = new_value
            tries += 1

        if dbg:  # для отладки:
            print('\tnew gene value: ' + str(new_value) + '\n\ttries: ' + str(tries))

        #if dbg:  # для отладки:
        #    print('\nf "mutate_gene":' + '\n\tgene_id: ' + str(gene_id) + '\n\told gene value: ' + str(
        #        current_value) + '\n\tnew gene value: ' + str(new_value) + '\n\ttries: ' + str(tries))


    # "применить" гены путём надевания обусловленной ими экипировки:
    def apply_genes(self, dbg=False):
        pointer = 0
        for item_id in self.my_genes:
            self.wear_item(pointer, item_id, LINKS_TO_EQUIP_DICTS[pointer], dbg=True)
            pointer += 1

        if dbg:  # для отладки:
            print('\nf "apply_genes":' + '\n\tapplied.')
            print(self)


    # оформить победу в дуэли:
    def do_win(self):
        self.my_wins += 1
        if self.my_wins % 2 == 0:
            # родить разбойника-потомка:
            print('разбойник ' + self.name + ' рожает потомка...')
            new_rogue = Rogue(self.my_genes, self.my_generation, from_parent=True, rogues_counter=str(Population.how_many_rogues))
            ROGUES_LIST.append(new_rogue)


    # оформить поражение в дуэли:
    def do_defeat(self):
        self.my_defeats += 1
        if self.my_defeats == 2:
            self.die()


    # погибнуть:
    def die(self):
        self.alive = False
        Population.how_many_rogues_alive -= 1


    def wear_item(self, slot, item_id, items_list, dbg=False):

        item_id += 1

        if dbg:  # для отладки:
            #print('f "wear_item":\n\titems_list:')
            #print(items_list)
            print('\tвыбрана вещь:', items_list[item_id])

        # в слоте не должно быть экипировки, иначе пришлось бы снять её и отнять характеристики, которые она дала:
        if self.equipment_slots[slot] == 0:
            self.equipment_slots[slot] = item_id
            self.equipment_names[slot] = items_list[item_id][0]
            self.stat_agility += items_list[item_id][2]
            self.stat_power += items_list[item_id][3]
            # не забываем, что к силе атаки нужно добавить бонусы также от силы и ловкости:
            self.stat_attackpower += items_list[item_id][1] + items_list[item_id][2] + items_list[item_id][3]
            self.stat_hit += items_list[item_id][4]
            self.direct_crit_bonus += items_list[item_id][5]
            self.stat_mastery += items_list[item_id][6]

            # если была добавлена ловкость ИЛИ прямой бонус к крит. шансу, пересчитать общий крит. шанс:
            if items_list[item_id][2] != 0 or items_list[item_id][5] != 0:
                self.calculate_critical_percent()

            # если было добавлено мастерство, пересчитать вероятность скользящего удара:
            if items_list[item_id][6] != 0:
                self.calculate_glancing_percent()

            # особый случай для набора экипировки "custom":
            if EQUIPMENT_COLLECTION == 'custom':
                # если в левую руку взят "Леворучный Страж Лесов" (id 1 для слота "левая рука"),
                # а в правую взят "Праворучный Страж Лесов" (id 1 для слота "правая рука"),
                # добавить дополнительно 2 к крит. шансу:
                if slot == 1:
                    if self.equipment_slots[1] == 1 and self.equipment_slots[0] == 1:
                        self.direct_crit_bonus += 2
                        self.calculate_critical_percent()
                        print('Дары Лесов вместе...')


    # переопределяем "магический метод" для демонстрации текущего состояния персонажа:
    def __str__(self):

        # выписать в строку названия надетых предметов:
        using_equipment_names = ''
        for i in range(0, len(self.equipment_names) - 1):
            using_equipment_names += self.equipment_names[i] + '", "'
        using_equipment_names = '"' + using_equipment_names + self.equipment_names[-1] + '"'

        # удобочитаемый текст:
        description = 'Разбойник по имени "' + self.name +'"\n'
        description += using_equipment_names + '\n'
        description += 'сила атаки: ' + str(self.stat_attackpower) + ' ед.\n'
        description += 'ловкость: ' + str(self.stat_agility) + ' ед.\n'
        description += 'сила: ' + str(self.stat_power) + ' ед.\n'
        description += 'меткость: ' + str(self.stat_hit) + '%\n'
        description += 'крит. шанс: ' + str(self.stat_crit) + '%\n'
        description += 'мастерство: ' + str(self.stat_mastery) + ' ед.\n'
        description += 'шанс скольз. уд.: ' + str(self.stat_glancing_percent) + '%\n'
        return description


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

    # кроме этого, создать список ссылок на эти словари:
    LINKS_TO_EQUIP_DICTS = [RIGHT_HANDS, LEFT_HANDS, GLOVES, HEADS, CHESTS, PANTS, BOOTS]

    #print(LINKS_TO_EQUIP_DICTS[0])
    #print(LINKS_TO_EQUIP_DICTS[0][1])
    #print(LINKS_TO_EQUIP_DICTS[0][1][0])

    # создать список, где будут храниться ссылки на всех разбойников:
    ROGUES_LIST = list()

    # создать объект популяции и наполнить его разбойниками в указанном количестве:
    new_population = Population(2)

    #ROGUES_LIST[2].die()

    ROGUES_LIST[0].do_win()
    ROGUES_LIST[0].do_win()

    # "прочитать" популяцию:
    #print(new_population)

else:
    print('__name__ is not "__main__".')
