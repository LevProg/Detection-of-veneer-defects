import os
import xml.etree.ElementTree as ET
import shutil

# Создаем словарь для соответствия меток и их индексов
label_map = {
    "Отсутствие клея": 0,
    "Одна полоса клея": 1,
    "Полосы клея смещены к пласти шпона": 2,
    "Полосы клея смещены на край": 3,
    "Часть уса  без клея": 4,
    "Скол по шпону": 5,
    "Разошедшаяся трещина": 6,
    "Заминание шпона": 7,
    "Трещины + участок без клея": 8,
    "Запил": 9,
    "Скол по сучку + участок без клея": 10,
    "Спиливание уса": 11,
    "Нет дефектов": 12,
    "Не видно шпона": 13
}

# Парсинг XML-файла с аннотациями
def parse_annotations(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    annotations = []
    for image in root.findall('image'):
        image_name = image.get('name')
        tag_label = image.find('tag').get('label')
        annotations.append((image_name, tag_label))

    return annotations

# Переименование и сохранение изображений
def rename_and_save_images(annotations, input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    label_counters = {label: 0 for label in label_map.values()}

    for image_name, tag_label in annotations:
        label_index = label_map[tag_label]
        label_counters[label_index] += 1
        new_image_name = f"{label_index}_{label_counters[label_index]}.png"

        src_path = os.path.join(input_folder, image_name)
        dst_path = os.path.join(output_folder, new_image_name)

        shutil.copy(src_path, dst_path)
        print(f"Copied {src_path} to {dst_path}")

# Основная функция
def main():
    xml_file = 'C:/Users/burla/Downloads/1_2_21/annotations.xml'  # Путь к вашему XML-файлу
    input_folder = 'D:/Шпон/photo/1_2_21'  # Папка с исходными изображениями
    output_folder = 'D:/Шпон/photo/data_1_2_21'  # Папка для сохранения переименованных изображений
    os.makedirs(output_folder)

    annotations = parse_annotations(xml_file)
    rename_and_save_images(annotations, input_folder, output_folder)

if __name__ == "__main__":
    main()
