# записать результаты в указанный файл:
def save_data_to_file(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        print(data, file=f)


# добавить строки в указанный файл:
def append_data_to_file(filename, data):
    with open(filename, 'a+', encoding='utf8') as f:
        print(data, file=f)


# прочитать указанный файл:
def read_file(filename):
    file_text = ''
    with open(filename, 'r', encoding='utf8') as f:
        file_text += f.read()
    return file_text
