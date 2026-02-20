from glob import glob
import os


def main():
    data_dir = '/home/adeshkin/Desktop/tolk_tom_1/part_4_174-237'
    folders = sorted(glob(f'{data_dir}/*'))
    for folder in folders:
        if os.path.isdir(folder):
            name = folder.split('/')[-1]
            idx = name.split('_')[-1]
            new_name = f'{int(idx):03d}'
            new_folder = os.path.join(data_dir, new_name)
            os.rename(folder, new_folder)   

if __name__ == '__main__':
    main()