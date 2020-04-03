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
            new_rogue = Rogue('', False, 0)

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
    def __init__(self, gens_list, from_parent, parent_generation):

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

        # если этот разбойник порождён другим разбойником, его гены должны незначительно мутировать:
        if from_parent:
            gens_list = self.mutate_gens(gens_list)
            self.my_gens = gens_list
        else:
            self.my_gens = gens_list


    # сгенерировать случайный набор генов:
    def generate_gens(self):
        pass
        # нужно знать нижние и верхние границы для каждого гена, чтобы вписаться в них...


    # унаследовать родительские гены с вероятностью мутации:
    def mutate_gens(self, parent_gens):
        pass
        # нужно знать нижние и верхние границы для каждого гена, чтобы вписаться в них...


    # "применить" гены путём надевания обусловленной ими экипировки:
    def apply_gens(self):
        pass
        # self.wear_item(0, self.my_gens[0])
        # self.wear_item(1, self.my_gens[1])
        # self.wear_item(2, self.my_gens[2])


    # оформить победу в дуэли:
    def do_win(self):
        self.my_wins += 1
        if self.my_wins % 2 == 0:
            self.spawn_new_rogue(self.my_gens, True)


    # оформить поражение в дуэли:
    def do_defeat(self):
        self.my_defeats += 1
        if self.my_defeats == 2:
            self.die()


    # родить нового разбойника:
    def spawn_new_rogue(self, parent_gens, from_parent):
        new_rogue = Rogue(self.my_gens, True, self.my_generation)
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

    # создать список, где будут храниться ссылки на всех разбойников:
    ROGUES_LIST = list()

    # создать объект популяции и наполнить его разбойниками в указанном количестве:
    new_population = Population(3)

    #ROGUES_LIST[2].die()

    # "прочитать" популяцию:
    print(new_population)

else:
    print('__name__ is not "__main__".')
