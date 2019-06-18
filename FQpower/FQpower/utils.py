from configparser import ConfigParser
from django.conf import settings
import os
#配置文件
class Conf:
    @staticmethod
    def get_str(section, option):
        try:
            cf = ConfigParser()
            cf.read(settings.MY_SYS_CONF_PATH[0], encoding='utf-8')
            res = cf.get(section, option)
        except:
            res = ''

        return res

    @staticmethod
    def get_int(section, option):
        try:
            cf = ConfigParser()
            cf.read(settings.MY_SYS_CONF_PATH[0], encoding='utf-8')
            res = cf.getint(section, option)
        except:
            res = 0

        return res

    @staticmethod
    def get_float(section, option):
        try:
            cf = ConfigParser()
            cf.read(settings.MY_SYS_CONF_PATH[0], encoding='utf-8')
            res = cf.getfloat(section, option)
        except:
            res = 0

        return res

    @staticmethod
    def get_bool(section, option):
        try:
            cf = ConfigParser()
            cf.read(settings.MY_SYS_CONF_PATH[0], encoding='utf-8')
            res = cf.getboolean(section, option)
        except:
            res = 0

        return res

class FileManager:
    # 获取当前路径下所有子文件夹
    @staticmethod
    def sub_dir(path):
        return [file for file in os.listdir(path) if os.path.isdir('\\'.join([path,file]))]

    # 获取当前路径下的非目录子文件
    @staticmethod
    def no_subdir_files(path):
        return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    # 获取当前路径下的非目录子文件,包含子目录下文件
    @staticmethod
    def inc_subdir_files(path):
        return [[os.path.join(root, file) for file in files] for root, dirs, files in os.walk(path)]

    # 获取当前路径下的所有指定文件类型的非目录子文件
    @staticmethod
    def no_subdir_type_files(path, type):
        all_file = list()
        for file in FileManager.no_subdir_files(path):
            arr = os.path.splitext(os.path.join(file))
            if arr[1] == type : all_file.append(arr[0])

        return all_file

    # 获取当前路径下的所有指定文件类型的非目录子文件,包含子目录下文件
    @staticmethod
    def inc_subdir_type_files(path, type):
        all_file = list()
        for files in FileManager.inc_subdir_files(path):
            for file in files:
                dir_name, file_name = os.path.split(file)
                arr = os.path.splitext(os.path.join(file_name))
                if arr[1] == type: all_file.append(arr[0])
        return all_file

    @staticmethod
    def write_file(path, data_file):
        [dir_name, file_name] = os.path.split(path)
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            with open(path, 'wb+') as f:
                for chunk in data_file.chunks():
                    f.write(chunk)

            return True
        except:
            return False

    @staticmethod
    def get_extension(file):
        (shotname, extension) = os.path.splitext(file)
        return extension

    @staticmethod
    def get_shotname(file):
        (shotname, extension) = os.path.splitext(file)
        return shotname

    @staticmethod
    def get_filename(file):
        [dir_name, file_name] = os.path.split(file)
        return file_name

    @staticmethod
    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    yield chunk
                else:
                    break
    @staticmethod
    def rm_file(file):
        if os.path.exists(file):
            os.remove(file)
