# для работы со временем:
from datetime import datetime
from time import time, sleep

# для некоторых операций:
from random import randrange, randint, choice, shuffle
from re import sub as replace

# для отрисовки графиков:
import matplotlib.pyplot as plt

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
    """Класс используется для удобной работы с популяцией."""

    # счётчик всех разбойников:
    how_many_rogues = 0

    # счётчик живых разбойников:
    how_many_rogues_alive = 0

    # счётчик поколений:
    generations = 0

    # рекорд количества побед у одного разбойника в популяции, а также его имя и гены:
    record_max_wins = 0
    max_winner_name = 'none'
    max_winner_genes = 'none'

    # день последних изменений в изменении численности популяции:
    day_of_last_changes = 0



    # при создании популяции сразу же наполнить её:
    def __init__(self, total, wins_to_reproduce=2, defeats_to_die=2):

        # запомнить начальное значение:
        self.initial_size = total

        # сохранить биологические параметры, которые будут справедливы для каждого разбойника в популяции:
        self.wins_to_reproduce = wins_to_reproduce
        self.defeats_to_die = defeats_to_die

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
        text += 'рекорд побед: ' + str(self.record_max_wins) + '\n'
        text += 'имя рекордсмена: ' + str(self.max_winner_name) + '\n'
        text += 'генотип рекордсмена: ' + str(self.max_winner_genes) + '\n'
        return text


    # перезагрузить популяцию, оставив в ней how_many_to_save разбойников с наиболее успешными генотипами:
    def reload(self, how_many_to_save):

        # обнулить кол-во разбойников:
        how_many_rogues_alive = 0

        # "убить" всех существующих разбойников:
        for x in ROGUES_LIST:
            x.alive = False

        # извлечь из словаря генотипов данные о лучших генотипах:
        list_genotypes_top = stats.get_ordered_list_from_dict(LIST_FOR_DICTS_GENOTYPES[current_stage], inner_index=2)

        # наполнить популяцию разбойниками с этими генотипами:
        for x in range(0, how_many_to_save):

            # преобразовать генотип из строки в список:
            genotype_in_str = list_genotypes_top[x][0]
            genotype_in_list = []
            for char in genotype_in_str:
                if char != '-':
                    genotype_in_list.append( int(char) )

            # создать нового разбойника, передав генотип и отметку о том, что гены НЕ должны мутировать:
            new_rogue = Rogue(genotype_in_list, 0, from_parent=True, genes_can_mutate=False)

            # пополнить список разбойников:
            ROGUES_LIST.append(new_rogue)




# класс Разбойника
class Rogue():
    """Класс описывает механику тестируемого персонажа, а также управляет его генами."""

    # при создании экземпляра:
    def __init__(self, genes_list_inherited, parent_generation, from_parent=True, genes_can_mutate=True):

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

        # статистические счётчики:
        Population.how_many_rogues += 1
        Population.how_many_rogues_alive += 1

        # номер поколения:
        self.my_generation = parent_generation + 1
        if self.my_generation > Population.generations:
            Population.generations = self.my_generation

        # "имя" разбойника:
        self.name = '"' + str(Population.how_many_rogues) + '-й, из поколения ' + str(parent_generation + 1) + '"'

        # жив ли:
        self.alive = True

        # счётчики побед и поражений:
        self.my_wins = 0
        self.my_defeats = 0

        # инициализировать цепочку генов:
        self.my_genes = [0] * 7

        if genes_can_mutate:
            # если этот разбойник порождён другим разбойником, его гены должны незначительно мутировать:
            if from_parent:
                self.mutate_genes(genes_list_inherited)
            else:
                self.generate_random_genes()
        else:
            self.my_genes = genes_list_inherited

        # отобразить эти гены в статистике:
        stats.genes_add_presence(self.my_genes, self.my_generation)

        # надеть экипировку согласно полученным генам:
        self.apply_genes()


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


    # метод для расчёта собственного рейтинга:
    def calculate_rate(self):
        dbg = DBG_rogue_calculate_rate

        # вычислить вероятность попадания:
        p_hit = self.stat_hit / 100

        # вычислить вероятность скользящего и НЕскользящего удара:
        p_glancing = self.stat_glancing_percent / 100
        not_p_glancing = 1 - self.stat_glancing_percent / 100

        # вычислить вероятность критического и НЕкритического удара:
        p_crit = self.stat_crit / 100
        not_p_crit = 1 - self.stat_crit / 100

        # вычислить ожидание модификатора:
        expectation_modificator = p_hit * (p_glancing * 0.7 + not_p_glancing * (p_crit * 2 + not_p_crit))

        # вычислить ожидание урона с таким модификатором:
        expectation_damage = expectation_modificator * self.stat_attackpower
        expectation_damage = round(expectation_damage, 3)

        if dbg:
            print('\tожидание модификатора =', expectation_modificator)
            print('\tожидание урона =', expectation_damage)

        return expectation_damage


    # сгенерировать случайный набор генов:
    def generate_random_genes(self):
        dbg = DBG_rogue_generate_random_genes

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
    def mutate_genes(self, parent_genes):
        dbg = DBG_rogue_mutate_genes

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
            # определить "силу" мутации = количество генов, которые должны мутировать:
            mutation_volume = randint(0, 30)
            mutation_iters = 1
            if 22 <= mutation_volume <= 28:
                mutation_iters = 2
            elif 29 <= mutation_volume <= 30:
                mutation_iters = 3

            if dbg:  # для отладки:
                print('\nf "mutate_genes" begins:' + '\n\tмутаций запланировано: ' + str(mutation_iters))

            # список генов, доступных для мутации:
            genes_available = [0, 1, 2, 3, 4, 5, 6]

            # список мутировавших генов:
            genes_mutated = []

            current_iter = 0
            while current_iter < mutation_iters:
                if dbg:  # для отладки:
                    print('\tw1')

                # выбрать случайный ген из доступных:
                gene_with_forced_mutation = choice(genes_available)

                # если этот ген ещё не мутировал:
                if gene_with_forced_mutation not in genes_mutated:
                    self.mutate_gene(gene_with_forced_mutation)
                    genes_mutated.append(gene_with_forced_mutation)
                    current_iter += 1
                    if dbg:  # для отладки:
                        print('\tcurrent_iter =', current_iter)
                else:
                    if dbg:  # для отладки:
                        print('\telse, because ' + str(gene_with_forced_mutation) + ' already in genes_mutated')

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
    def mutate_gene(self, gene_id):
        dbg = DBG_rogue_mutate_gene

        current_value = self.my_genes[gene_id]
        new_value = current_value

        if dbg:  # для отладки:
            print('\nf "mutate_gene":' + '\n\tgene_id: ' + str(gene_id) + '\n\told gene value: ' + str(current_value))

        tries = 0
        while new_value == current_value:
            if dbg and tries > 0:  # для отладки:
                print('\tw2, because ' + str(new_value) + ' = ' + str(current_value) )
            new_value = randrange(0, len(LINKS_TO_EQUIP_DICTS[gene_id]))
            self.my_genes[gene_id] = new_value
            tries += 1

        if dbg:  # для отладки:
            print('\tnew gene value: ' + str(new_value) + '\n\ttries: ' + str(tries))


    # "применить" гены путём надевания обусловленной ими экипировки:
    def apply_genes(self):
        dbg = DBG_rogue_apply_genes

        pointer = 0
        for item_id in self.my_genes:
            self.wear_item(pointer, item_id, LINKS_TO_EQUIP_DICTS[pointer])
            pointer += 1

        if dbg:  # для отладки:
            print('\nf "apply_genes":' + '\n\tapplied.')
            print(self)


    # оформить победу в дуэли:
    def do_win(self):
        dbg = DBG_rogue_do_win

        self.my_wins += 1
        stats.genes_add_win(self.my_genes)

        # после каждой второй победы:
        if self.my_wins % population.wins_to_reproduce == 0:
            # родить разбойника-потомка:
            if dbg:
                print(self.name + ' рожает потомка...')
            new_rogue = Rogue(self.my_genes, self.my_generation, from_parent=True)
            ROGUES_LIST.append(new_rogue)

            population.day_of_last_changes = current_day

        # обновить рекорд количества побед у одного разбойника в популяции:
        if self.my_wins > Population.record_max_wins:
            Population.record_max_wins = self.my_wins
            Population.max_winner_name = self.name
            Population.max_winner_genes = self.my_genes


    # оформить поражение в дуэли:
    def do_defeat(self):
        dbg = DBG_rogue_do_defeat

        self.my_defeats += 1

        # после двух поражений выпилиться:
        if self.my_defeats == population.defeats_to_die:
            self.alive = False
            Population.how_many_rogues_alive -= 1

            population.day_of_last_changes = current_day

            if dbg:
                print(self.name + ' выпиливается...')


    def wear_item(self, slot, item_id, items_list):
        dbg = DBG_rogue_wear_item

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

        # выписать в строку гены:
        cnt = 0
        genes_str = ''
        for x in self.my_genes:
            if cnt != len(self.my_genes) - 1:
                genes_str += str(x) + ', '
            else:
                genes_str += str(x)
        cnt += 1

        # удобочитаемый текст:
        description = 'Разбойник по имени ' + self.name +'\n'
        description += 'гены: ' + genes_str + '\n'
        description += using_equipment_names + '\n'
        description += 'рейтинг: ' + str(self.calculate_rate()) + ' очк.\n'
        description += 'сила атаки: ' + str(self.stat_attackpower) + ' ед.\n'
        description += 'ловкость: ' + str(self.stat_agility) + ' ед.\n'
        description += 'сила: ' + str(self.stat_power) + ' ед.\n'
        description += 'меткость: ' + str(self.stat_hit) + '%\n'
        description += 'крит. шанс: ' + str(self.stat_crit) + '%\n'
        description += 'мастерство: ' + str(self.stat_mastery) + ' ед.\n'
        description += 'шанс скольз. уд.: ' + str(self.stat_glancing_percent) + '%\n'
        return description



# класс Столкновений
class Challenger():
    """Класс обеспечивает проведение столкновений между случайными разбойниками."""

    # провести серию соревнований:
    def perform_serie(self):
        dbg = DBG_challenger_perform_serie

        # создать список живых разбойников:
        rogues_alive = []
        for x in ROGUES_LIST:
            if x.alive:
                rogues_alive.append(x)

        # перемешать список:
        shuffle(rogues_alive)

        # получить количество пар живых разбойников в популяции:
        pairs_total = int(len(rogues_alive) // 2)

        if dbg:
            print('pairs_total =', pairs_total)

        # запускать бои между соседними по списку разбойниками:
        counter = 0
        pointer = 0
        while counter < pairs_total:
            a_1 = rogues_alive[pointer]
            a_2 = rogues_alive[pointer + 1]
            #print('новая пара:', a_1.name, 'и', a_2.name)
            self.perform_one(a_1, a_2)
            counter += 1
            pointer += 2


    # провести соревнование между двумя разбойниками:
    def perform_one(self, rogue_1, rogue_2):
        dbg = DBG_challenger_perform_one

        if dbg:
            print('\nновое соревнование между:', rogue_1.name, 'и', rogue_2.name)

        # рассчитать рейтинг каждого разбойника (в более совершенной симуляции тут может быть полноценное сражение):
        rating_1 = rogue_1.calculate_rate()
        rating_2 = rogue_2.calculate_rate()

        if dbg:
            print('\tих рейтинг:', rating_1, 'и', rating_2, 'соответственно.')

        # раскидать очки между победителем и проигравшим:
        if rating_1 > rating_2:
            rogue_1.do_win()
            rogue_2.do_defeat()
        elif rating_1 < rating_2:
            rogue_1.do_defeat()
            rogue_2.do_win()
        else:
            if dbg:
                print('\tО чудо! Произошла ничья!')



# класс Статистики:
class Stats():
    """Класс обеспечивает сбор и визуализацию статистики."""

    # при инициализации нужно подготовить некоторые данные, которые затем неоднократно понадобятся:
    def __init__(self):

        # подсчитать количество возможных генотипов:
        self.genotypes_total = 1
        for current_dict_for_equip in LINKS_TO_EQUIP_DICTS:
            self.genotypes_total *= len(current_dict_for_equip)
        # print('генотипов всего:', genotypes_total)

        # создать список возможных генотипов:
        self.list_of_possible_genotypes = list()

        # для каждого оружия в правой руке:
        for g1 in RIGHT_HANDS:
            # для каждого оружия в левой руке:
            for g2 in LEFT_HANDS:
                # для каждых перчаток:
                for g3 in GLOVES:
                    # для каждого шлема:
                    for g4 in HEADS:
                        # для каждого нагрудника:
                        for g5 in CHESTS:
                            # для каждых штанов:
                            for g6 in PANTS:
                                # для каждой обуви:
                                for g7 in BOOTS:
                                    current_genotype = str(g1-1)+'-'+str(g2-1)+'-'+str(g3-1)+'-'+str(g4-1)+'-'+str(g5-1)+'-'+str(g6-1)+'-'+str(g7-1)
                                    self.list_of_possible_genotypes.append(current_genotype)
        #print(self.list_of_possible_genotypes)


        # нужно вычислить размеры прямоугольной области, максимально приближенной по размерам к квадрату, где Ширина * Длина = Сумма генотипов:
        # для этого нужно выписать в список все делители числа-суммы генотипов:
        list_divisors = list()
        current_number = int(self.genotypes_total // 2)
        while current_number >= 2:
            if self.genotypes_total % current_number == 0:
                list_divisors.append(current_number)
            current_number -= 1
        print('list_divisors:', list_divisors)

        # взять индекс примерно из середины полученного списка делителей:
        somewhere_in_the_middle = len(list_divisors) // 2

        # получить длины сторон будущего прямоугольника:
        side_1 = list_divisors[somewhere_in_the_middle]
        side_2 = self.genotypes_total / side_1

        # определить, какая сторона длиннее, чтобы в будущем прямоугольник "положить" на бок:
        self.side_x = int(side_1 if side_1 >= side_2 else side_2)
        self.side_y = int(self.genotypes_total / self.side_x)
        print('side_x =', self.side_x, 'side_y =', self.side_y)


        # объявить набор цветов для карты распространённости генотипов:
        self.list_of_distribution_colors = [''] * 11
        self.list_of_distribution_colors[0] = 'c0392b'
        self.list_of_distribution_colors[1] = '62eace'
        self.list_of_distribution_colors[2] = '4be7c8'
        self.list_of_distribution_colors[3] = '35e3c1'
        self.list_of_distribution_colors[4] = '1fe0ba'
        self.list_of_distribution_colors[5] = '1ccaa7'
        self.list_of_distribution_colors[6] = '18b495'
        self.list_of_distribution_colors[7] = '159d82'
        self.list_of_distribution_colors[8] = '12876f'
        self.list_of_distribution_colors[9] = '0f705d'


        # объявить набор цветов для карты побед генотипов:
        self.list_of_wins_colors = [''] * 10
        self.list_of_wins_colors[0] = 'c0392b'
        self.list_of_wins_colors[1] = 'f39c12'
        self.list_of_wins_colors[2] = 'acecba'
        self.list_of_wins_colors[3] = '98e7a9'
        self.list_of_wins_colors[4] = '83e298'
        self.list_of_wins_colors[5] = '6edd86'
        self.list_of_wins_colors[6] = '5ad875'
        self.list_of_wins_colors[7] = '45d364'
        self.list_of_wins_colors[8] = '30cf53'
        self.list_of_wins_colors[9] = '2cba4a'

        # инициализировать переменные для хранения набора отрисованных слайдов:
        self.htmls_distribution = ''
        self.htmls_wins = ''

        # счётчик отрисованных дней:
        self.days_drawn = 0


    # метод - добавить новый ген и номер породившего его поколения в словарь,
    # и/или добавить 1 в счётчик присутствия гена в популяции:
    def genes_add_presence(self, genes, generation):
        genes_str = '-'.join(map(str, genes))
        LIST_FOR_DICTS_GENOTYPES[current_stage].setdefault(genes_str, (generation, 0, 0))
        a, b, c = LIST_FOR_DICTS_GENOTYPES[current_stage][genes_str]
        LIST_FOR_DICTS_GENOTYPES[current_stage][genes_str] = (a, b + 1, c)


    # метод - добавить 1 в счётчик побед гена:
    def genes_add_win(self, genes):
        genes_str = '-'.join(map(str, genes))
        a, b, c = LIST_FOR_DICTS_GENOTYPES[current_stage][genes_str]
        LIST_FOR_DICTS_GENOTYPES[current_stage][genes_str] = (a, b, c + 1)


    # метод - добавить данные по дню:
    def add_new_day(self, day_number):
        global DICT_DAYS
        DICT_DAYS.setdefault(day_number, (Population.how_many_rogues, Population.how_many_rogues_alive))


    # метод - превратить словарь в список кортежей, упорядочить список по указанному элементу, вернуть:
    def get_ordered_list_from_dict(self, dict_a, outer_index=1, inner_index=0):
        list_ = list(dict_a.items())
        list_.sort(key=lambda i: -i[outer_index][inner_index])
        return list_


    # метод - отрисовать в HTML прямоугольную область, где показать "карту генотипов" с точки зрения их распространённости:
    def draw_genes_distribution(self, day_num, create_autonomous_version=False):

        self.days_drawn += 1

        # отрисовать область, состоящую из <span>-квадратиков, где id будет равен коду генотипа:
        HTML_slide = ''
        current_index = -1
        for y in range(0, self.side_y):
            current_row = ''
            for x in range(0, self.side_x):

                # получить код очередного возможного генотипа:
                current_index += 1
                genotype_id = self.list_of_possible_genotypes[current_index]

                # добавить цвет квадратику зависимо от количества появлений гена в популяции:
                if genotype_id in LIST_FOR_DICTS_GENOTYPES[current_stage]:
                    genotype_appears = LIST_FOR_DICTS_GENOTYPES[current_stage][genotype_id][1]
                    if 0 <= genotype_appears < 10:
                        color = '#' + self.list_of_distribution_colors[ genotype_appears ]
                    else:
                        color = '#003300'
                else:
                    color = '#e2e8e9'

                # но если этот ген появился в самый первый день (изначально сгенерирован), перекрасить в синий:
                if genotype_id in LIST_FOR_DICTS_GENOTYPES[current_stage]:
                    if LIST_FOR_DICTS_GENOTYPES[current_stage][genotype_id][0] == 1:
                        color = '#4834d4'

                # добавить очередной квадратик-генотип в текущую строку:
                current_row += '<span class="gen" id="' + genotype_id + '" style="background-color: ' + color + '"></span>'

            # когда вся строка сформирована, добавить её в код всей области:
            HTML_slide += current_row + '<br>\n'

        # закончить оформление области:
        HTML_slide = '\n\n<div class="g_cont_d d_' + str(self.days_drawn) + '"><p>день ' + str(day_num) + '</p><div class="gen_f">\n' + HTML_slide + '</div></div>\n'

        # сохранить область в файл, который потом будет считываться через файл index.html:
        #save_data_to_file(filename, HTML_slide)

        # сохранить область в переменную:
        self.htmls_distribution += HTML_slide


    # метод - отрисовать в HTML прямоугольную область, где показать "карту генотипов" с точки зрения их побед:
    def draw_genes_wins(self, day_num, create_autonomous_version=False):

        # отрисовать область, состоящую из <span>-квадратиков, где id будет равен коду генотипа:
        HTML_slide = ''
        current_index = -1
        for y in range(0, self.side_y):
            current_row = ''
            for x in range(0, self.side_x):
                # получить код очередного возможного генотипа:
                current_index += 1
                genotype_id = self.list_of_possible_genotypes[current_index]

                # добавить цвет квадратику зависимо от количества побед гена:
                if genotype_id in LIST_FOR_DICTS_GENOTYPES[current_stage]:
                    genotype_wins = LIST_FOR_DICTS_GENOTYPES[current_stage][genotype_id][2]
                    if 0 <= genotype_wins < 10:
                        color = '#' + self.list_of_wins_colors[genotype_wins]
                    else:
                        # если больше 10 побед - синий цвет:
                        color = '#33ccff'
                else:
                    color = '#e2e8e9'

                # добавить очередной квадратик-генотип в текущую строку:
                current_row += '<span class="gen" id="' + genotype_id + '" style="background-color: ' + color + '"></span>'

            # когда вся строка сформирована, добавить её в код всей области:
            HTML_slide += current_row + '<br>\n'

        # закончить оформление области:
        HTML_slide = '\n\n<div class="g_cont_w w_' + str(self.days_drawn) + '"><p>день ' + str(day_num) + '</p><div class="gen_f">\n' + HTML_slide + '</div></div>\n'

        # сохранить область в файл, который потом будет считываться через файл index.html:
        #save_data_to_file(filename, HTML_slide)

        # сохранить область в переменную:
        self.htmls_wins += HTML_slide


    # метод - отрисовать график при помощи matplotlib.pyplot:
    def draw_and_put_line_chart_to_file(self, DICT_DAYS, element_to_extract, chart_title, x_label, y_label, filename):
        list_x = []
        list_y = []
        day = 1

        # добавить указанный элемент кортежа словаря (соответствующего текущему дню) в список, который ляжет на график:
        for x in DICT_DAYS:
            #print('x =', x)
            list_x.append(day)
            list_y.append( DICT_DAYS[x][element_to_extract] )
            day += 1

        # превратить данные в график, нарисовать сетку:
        fig, axes = plt.subplots()
        axes.plot(list_x, list_y)
        axes.grid(color='#eee')

        # окрасить тики графика в более светлый цвет:
        axes.tick_params(colors='#aaa')

        # добавить подпись к графику:
        axes.set_title(chart_title)

        # добавить подписи к осям:
        axes.set_xlabel(x_label)
        axes.set_ylabel(y_label)

        # сохранить изображение в файл:
        fig.savefig(filename)


    # метод - взять HTML-шаблон и создать интерактивный шаблон на его основе:
    def create_index_html(self):

        # считать основу с шаблона:
        our_html = read_file('report_template.html')

        # время запуска:
        current_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')

        # заменить в нужных точках метки на данные:
        # - время запуска:
        our_html = replace('R_LAUNCH_TIME', current_time, our_html)

        # - количество прошедших стадий:
        our_html = replace('R_STAGES_TOTAL', str(MAX_STAGES), our_html)

        # - количество прошедших дней:
        our_html = replace('R_DAYS_TOTAL', str(MAX_DAYS_AT_STAGE * MAX_STAGES), our_html)

        # - количество отрисованных на слайдах дней:
        our_html = replace('R_DAYS_DRAWN', str(self.days_drawn), our_html)

        # - день, когда произошли последние изменения в численности популяции:
        our_html = replace('R_DAY_LAST_CHANGES', str(population.day_of_last_changes), our_html)

        # - начальный и конечный размеры популяции:
        our_html = replace('R_PPL_INITIAL_SIZE', str(population.initial_size), our_html)
        our_html = replace('R_PPL_FINAL_SIZE', str(Population.how_many_rogues_alive), our_html)

        # - сколько всего разбойников появилось на свет:
        our_html = replace('R_ROGUES_TOTAL', str(Population.how_many_rogues), our_html)

        # сколько поколений образовалось:
        our_html = replace('R_GNR_TOTAL', str(population.generations), our_html)

        # - подсчитать количество уникальных генотипов, для этого надо сформировать словарь для сбора генотипов всех стадий:
        dict_for_unique_genotypes = {}
        for current_dict in range( 0, len(LIST_FOR_DICTS_GENOTYPES) ):
            for current_genotype in LIST_FOR_DICTS_GENOTYPES[current_dict]:
                dict_for_unique_genotypes.setdefault(current_genotype, 0)

        # - длина этого словаря и есть количество уникальных генотипов за все стадии:
        our_html = replace('R_UNIQUE_GENOTYPES', str(len(dict_for_unique_genotypes)), our_html)

        # - информация о самом победоносном гене на последней стадии:
        list_genotypes_top = stats.get_ordered_list_from_dict(LIST_FOR_DICTS_GENOTYPES[current_stage], inner_index=2)
        winner_name = list_genotypes_top[0][0]
        winner_born = list_genotypes_top[0][1][0]
        winner_wins = list_genotypes_top[0][1][2]
        our_html = replace('R_GENOTYPE_WINNER_NAME', winner_name, our_html)
        our_html = replace('R_GENOTYPE_WINNER_BORN', str(winner_born), our_html)
        our_html = replace('R_GENOTYPE_WINNER_WINS', str(winner_wins), our_html)

        # - слайды:
        our_html = replace('R_SLIDES_DISTRIBUTION', self.htmls_distribution, our_html)
        our_html = replace('R_SLIDES_WINS', self.htmls_wins, our_html)

        # сохранить в интерактивный файл-отчёт:
        saving_status = save_data_to_file('report ' + current_time + '.html', our_html)
        print(saving_status)



# КОНСТАНТЫ:
GENES_CHAIN_LENGTH = 0  # <-- длина цепочки генов (должна совпадать с количеством словарей экипировки)
ROGUES_AT_BEGIN = 20  # <-- начальное население популяции (для каждой стадии)
MAX_STAGES = 10  # <-- сколько стадий перезагрузки популяции должно пройти
MAX_DAYS_AT_STAGE = 200 # <-- сколько дней будет содержать одна стадия перезагрузки популяции
SLIDING_FREQUENCY = 20 # <-- как часто нужно создавать HTML-слайды с полями генотипов (1 = раз в день, 10 = раз в 10 дней)

# список ссылок на словари экипировки:
LINKS_TO_EQUIP_DICTS = [RIGHT_HANDS, LEFT_HANDS, GLOVES, HEADS, CHESTS, PANTS, BOOTS]

# список для хранения списка словарей со статистикой по генам (отдельный словарь для каждой стадии):
LIST_FOR_DICTS_GENOTYPES = [{}] * MAX_STAGES

# словарь для хранения статистики по дням:
DICT_DAYS = {}

# список, где будут храниться ссылки на всех когда-либо появившихся разбойников:
ROGUES_LIST = list()

# переменная для хранения значения текущей стадии (должна находиться в глобальной области видимости)
current_stage = 0

# КОНСТАНТЫ для точечного управления "отладкой" (выводом отчётов о работе функций/методов):
DBG_rogue_mutate_genes = False
DBG_rogue_generate_random_genes = False
DBG_rogue_apply_genes = False
DBG_rogue_calculate_rate = False
DBG_rogue_mutate_gene = False
DBG_rogue_do_win = False
DBG_rogue_do_defeat = False
DBG_rogue_wear_item = False
DBG_challenger_perform_serie = False
DBG_challenger_perform_one = False
DBG_days_report = False  # <-- общий отчёт о каждом дне



# ЗАПУСК:
if __name__ == '__main__':

    # засечь время:
    time_begin = time()

    # запустить цикл на указанное количество стадий перезагрузки популяции:
    max_days_for_current_stage = 0
    current_day = 1
    while current_stage < MAX_STAGES:

        # на старте ПЕРВОЙ стадии:
        if current_stage == 0:

            # создать объект статистики:
            stats = Stats()

            # создать объект популяции и наполнить его разбойниками в указанном количестве, а также указать их биологические параметры:
            population = Population(ROGUES_AT_BEGIN, wins_to_reproduce=2, defeats_to_die=2)

            # создать объект для управления состязаниями:
            challenger = Challenger()

            # "прочитать" популяцию:
            print(population)


        # высчитать новый максимум с учётом наступления новой стадии:
        max_days_for_current_stage += MAX_DAYS_AT_STAGE

        # запустить/продолжить цикл на доступное количество дней (1 день = 1 столкновение у каждого (почти*) разбойника)
        # * - когда в популяции в какой-то день нечётное количество разбойников, кто-то из них остаётся без пары и не дерётся в этот день
        while current_day <= max_days_for_current_stage:
            print('st ' + str(current_stage) + ', day ' + str(current_day))
            if DBG_days_report:
                print('\n\nДЕНЬ/DAY', current_day)

            # в начале каждого SLIDING_FREQUENCY дня (а также в первый и последний) отрисовывать слайды по распространённости генотипов:
            if current_day % SLIDING_FREQUENCY == 0 or current_day == 1 or current_day == MAX_DAYS_AT_STAGE * MAX_STAGES:
                stats.draw_genes_distribution(current_day, create_autonomous_version=False)

            # выполнить серию соревнований:
            challenger.perform_serie()

            if DBG_days_report:
                print('\nДень', current_day, 'завершён.')
                print(population)

            # статистика для этого дня:
            stats.add_new_day(current_day)

            # в конце каждого SLIDING_FREQUENCY дня (а также в первый и последний) отрисовывать слайды по победам генотипов:
            if current_day % SLIDING_FREQUENCY == 0 or current_day == 1 or current_day == MAX_DAYS_AT_STAGE * MAX_STAGES:
                stats.draw_genes_wins(current_day, create_autonomous_version=False)

            current_day += 1

        # когда стадия подходит к концу, перезагрузить популяцию, оставив в ней указанное кол-во лучших генотипов:
        population.reload(ROGUES_AT_BEGIN)

        current_stage += 1


    # теперь понизить назад счётчик текущей стадии, чтобы удобно работать со списком LIST_FOR_DICTS_GENOTYPES:
    current_stage -= 1

    # вывести статистику дней:
    print('\nДНИ:')
    print(DICT_DAYS)

    # нарисовать линейный график о динамике одновременно живущих разбойников:
    stats.draw_and_put_line_chart_to_file(DICT_DAYS, 1, 'живое население', 'дни', 'разбойников', 'charts/chart_population_demography.png')

    # нарисовать линейный график о динамике общей численности когда-либо живших разбойников:
    stats.draw_and_put_line_chart_to_file(DICT_DAYS, 0, 'родившихся всего', 'дни', 'разбойников', 'charts/chart_population_total.png')

    # создать общий HTML для изучения сессии:
    stats.create_index_html()

    # вычислить затраченное время:
    time_session = time() - time_begin
    duration_info = 'работа программы длилась: ' + str(round(time_session, 2)) + ' сек.'
    print('\n' + duration_info)

else:
    print('__name__ is not "__main__".')
