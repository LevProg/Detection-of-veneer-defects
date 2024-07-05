import os
import shutil


def ensure_unique_filename(dst_folder, base_name):
    """
    Generates a unique filename in the specified destination folder by adding/incrementing the second index.
    """
    base, ext = os.path.splitext(base_name)

    if '_' in base:
        parts = base.rsplit('_', 1)
        index1 = parts[0]
        try:
            index2 = int(parts[1])
        except ValueError:
            index1 = base
            index2 = 1
    else:
        index1 = base
        index2 = 1

    new_name = f"{index1}_{index2}{ext}"

    while os.path.exists(os.path.join(dst_folder, new_name)):
        index2 += 1
        new_name = f"{index1}_{index2}{ext}"

    return new_name


def move_and_rename_images(src_folders, dst_folder):
    """
    Moves and renames images from source folders to the target folder.
    """
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    for src_folder in src_folders:
        for image_name in os.listdir(src_folder):
            src_path = os.path.join(src_folder, image_name)
            if os.path.isfile(src_path):
                unique_name = ensure_unique_filename(dst_folder, image_name)
                dst_path = os.path.join(dst_folder, unique_name)

                shutil.copy(src_path, dst_path)
                print(f"Copied {src_path} to {dst_path}")

    #src_folders = ['D:/Шпон/photo/data_1_1_22', 'D:/Шпон/photo/data_1_2_21', 'D:/Шпон/photo/data_1_3_20', 'D:/Шпон/photo/data_1_4_19', 'D:/Шпон/photo/data_1_5_18', 'D:/Шпон/photo/data_1_6_17', 'D:/Шпон/photo/data_1_7_16', 'D:/Шпон/photo/data_1_8_10', 'D:/Шпон/photo/data_1_9_9', 'D:/Шпон/photo/data_1_10_7', 'D:/Шпон/photo/data_1_11_23', 'D:/Шпон/photo/data_2_12_15', 'D:/Шпон/photo/data_2_13_16']  # Список исходных папок
    #dst_folder = 'D:/Шпон/photo/sum_data'  # Папка для сохранения переименованных изображений

    #move_and_rename_images(src_folders, dst_folder)



def rename_files(src_folder):
    """
    Переименовывает файлы из формата 9_N в формат 2_(N+2).
    """
    for file_name in os.listdir(src_folder):
        base, ext = os.path.splitext(file_name)

        # Проверяем, соответствует ли имя файла ожидаемому формату 9_N
        if base.startswith("7_"):
            try:
                # Извлекаем N и увеличиваем его на 2
                n = int(base[2:])
                new_n = n + 3
                new_base = f"4_{new_n}"

                # Формируем новое имя файла
                new_name = new_base + ext

                # Полные пути к старому и новому файлам
                old_path = os.path.join(src_folder, file_name)
                new_path = os.path.join(src_folder, new_name)

                # Переименовываем файл
                os.rename(old_path, new_path)
                print(f"Renamed {old_path} to {new_path}")
            except ValueError:
                print(f"Skipping file {file_name}: invalid format")
        else:
            print(f"Skipping file {file_name}: does not match the pattern '9_N'")


def main():
    src_folder = "D:/Шпон/photo/sum_data"  # Замените на ваш путь к папке с файлами
    rename_files(src_folder)


if __name__ == "__main__":
    main()
