import time
from configparser import *
import os, sys, datetime, re
import configparser

import requests


class Helper:
    info_file = os.getcwd() + '\\info.ini'  # 配置文件路径
    words_file = os.getcwd() + '\\个人词库.txt'  # 词库保存路径
    config = ConfigParser()  # 配置文件对象
    time_to_study = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 记录开始学习时间

    def __init__(self):
        """
        配置初始化模块
        """
        if not (os.path.exists(self.info_file) and os.path.exists(self.words_file)):
            f = open(self.info_file, 'w')  # 创建配置文件
            open(self.words_file, 'a+')  # 创建个人词库文件
            self.config.read('info.ini')
            """
            init模块保存初始化信息(也是全局变量,方便使用)：
                程序启动次数times，用户名username，词库总量，创建时间created_time
            可以被全部的信息模块使用
            """
            print('>>>说明<<<\n' +
                  '○本软件旨在帮助测试和巩固单词，建立个人词库，并不提供单词学习功能\n' +
                  '○您的每一次学习记录都会被保存在info.ini文件中\n'+
                  '○本说明只在首次运行软件时出现')
            time.sleep(9)
            self.config.add_section('init')  # 在配置文件中添加初始化模块
            self.config.set('init', '软件版本', 'v1.1')
            self.config.set('init', 'times', '0')  # 启动次数，初始化为0
            system_para = os.system('cls')         # 清屏处理
            name = input('--->欢迎使用单词助手,我是Allen\n--->我该怎么称呼你呢:')
            print(f"你好啊,{name},很高兴认识你,祝你背单词愉快")
            time.sleep(3)
            system_para = os.system('cls')
            self.config.set('init', 'username', name)  # 保存用户名，初始化为空
            self.config.set('init', '词库量', '0')  # 保存单词总量
            self.config.set('init', '创建时间', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 创建时间
            times = self.config.getint('init', 'times')
            self.config.add_section(f'record-{times}')  # 添加信息保存模块，模块id由init模块确定
            self.config.set(f'record-{times}', '开始学习时间', self.time_to_study)
            self.config.write(f)
        else:
            f = open(self.info_file, 'r+')
            self.config.read('info.ini')
            """
            在非首次启动时，都会首先将init模块中的times自增1，便于下次信息模块创建时使用
            因为init模块为其他函数提供times的值，也为了避免信息模块id的不重复使用
            """
            times = self.config.getint('init', 'times')
            times += 1  # times可以看成信息模块id
            self.config.set('init', 'times', str(times))  # 根据times的值，添加新的信息模块,以免section重复
            self.config.add_section(f'record-{times}')
            self.config.set(f'record-{times}', '开始学习时间', self.time_to_study)
            self.config.write(f)

    def words_add(self):
        """
        单词添加模块,同时将新增单词写入本次信息模块和词库
        :return:
        """
        remove = []    # 存放待删除的重复的单词
        keys = []      # 词库中的全部单词列表
        day_data = {}  # 保存今日单词和其中文词义
        day_words = input('--->请输入本次测试单词(请分开输入单词):')
        day_words = day_words.strip()  # 除去字符串两边的空白字符
        day_words = re.split('[,， ]', day_words)  # 根据中英文逗号和空格来分隔用户的输入内容
        g = open(self.words_file, 'r+')
        data = g.readlines()                       # 读取个人词库内容
        trim_data = str(data).replace(r'\n', '')   # 除去换行符
        dict_data = eval(trim_data)                # 使用eval函数将字符串转为列表
        length = len(dict_data)
        for i in range(length):
            keys += eval(dict_data[i]).keys()
        """
        获取用户的单词录入
        """
        for i in day_words:
            if i in keys:            # 判断输入单词是否已经存在词库中
                print(f'--->单词{i}已经存在于词库中,不计入本次新增单词')
                remove.append(i)
            else:
                meaning = input(f'--->请输入{i}的中文词义:')
                meaning = re.split('[,， ]', meaning)  # 分隔中文词义，正则对于单个意思的单词也可转化为列表
                day_data[i] = meaning
        for i in day_words:
            if i in remove:
                day_words.remove(i)
        """
        向配置文件中添加数据
        """
        g.write(str(day_data)+'\n')  # 向词库中保存文件
        self.config.read('info.ini')
        total = self.config.getint('init', '词库量')
        total += len(day_words)
        times = self.config.getint('init', 'times')
        self.config.set(f'record-{times}', '新增单词', str(day_data))
        self.config.set('init', '词库量', str(total))
        self.config.write(open(self.info_file, 'r+'))
        print('--->保存成功,即将回到主界面...')
        time.sleep(2)
        system_para = os.system('cls')

    def words_test(self):
        """
        单词测试模块
        :return:
        """
        """
        变量定义
        """
        lr = 0  # 正确率达到0.4以上的单词个数
        weak_words = []  # 需加强记忆的单词列表
        """
        下面读取配置文件，写入数据
        """
        try:               # 异常处理，eval函数的参数不能为空，否则抛出SyntaxError，还有测试单词为空的异常
            self.config.read('info.ini')
            times = self.config.getint('init', 'times')
            words_list = eval(self.config.get(f'record-{times}', '新增单词'))  # 使用eval函数，将字符串转字典
            if times >= 1:
                last_words = eval(self.config.get(f'record-{times - 1}', '新增单词'))
                r_rate = self.config.getfloat(f'record-{times - 1}', '本次测试正确率')
                words_weak = self.config.get(f'record-{times - 1}', '本次待加强单词')
                print('--->上一次的学习情况如下:')
                print('--->学习的单词:', end=' ')
                for i in list(last_words.keys()):
                    print(i, end='|')
                print(f'--->测试正确率: {r_rate}')
                print('--->待加强单词:', end=' ')
                if not words_weak:
                    print('无')
                else:
                    for j in words_weak:
                        print(j, end='|')
                print("\n")
        except SyntaxError:
            print('--->暂时没有测试单词哦，请先添加本次测试单词')
            time.sleep(2)
            self.words_add()
        except KeyError:
            print('--->暂时没有测试单词哦，请先添加本次测试单词')
            time.sleep(2)
            self.words_add()
        except configparser.NoOptionError:
            print('--->暂时没有测试单词哦，请先添加本次测试单词')
            time.sleep(2)
            self.words_add()
        else:  # 没有发生异常就运行else中的代码
            keys = list(words_list.keys())  # 将字典的键，即单词转为列表
            for i in keys:                  # 这里按照顺序测试输入的单词，可以更换测试方式
                count = 0  # 统计用户输入中文词义的正确个数
                right_length = len(words_list.get(i))
                mean = input(f'--->{i}的中文词义有:')
                mean = re.split('[,， ]', mean)
                for j in words_list.get(i):  # 这里的双层循环是验证用户输入的词义的正确个数
                    for k in mean:
                        if k == j:
                            count += 1
                if 0.4 < (count / right_length) <= 0.6:
                    print("--->记得还不错")
                    lr += 0.5
                    time.sleep(2)
                elif 0.6 < (count / right_length) <= 0.8:
                    print('--->棒棒哒')
                    lr += 0.7
                    time.sleep(2)
                elif 0.8 < (count / right_length) <= 1:
                    print("--->完美!")
                    lr += 1
                    time.sleep(2)
                elif (count / right_length) <= 0.4:
                    print("--->还需要加强记忆哦")
                    weak_words.append(i)
                    time.sleep(2)
            print("--->测试完成，即将回到主界面...")
            time.sleep(2)
            self.config.set(f'record-{times}', '本次测试正确率', str(round(lr / len(keys), 2)))
            self.config.set(f'record-{times}', '本次待加强单词', str(weak_words))
            self.config.write(open(self.info_file, 'r+'))

    def local_query(self):
        """
        本地单词查询
        :return:
        """
        keys = []  # 保存全部的单词
        values = []  # 保存全部单词的中文词义
        self.config.read('info.ini')
        words_total = self.config.getint('init', '词库量')
        if words_total == 0:
            print("--->当前词库为空，请先添加单词")
            time.sleep(2)
        g = open(self.words_file, 'r+')
        data = g.readlines()                       # 读取个人词库内容
        trim_data = str(data).replace(r'\n', '')   # 除去换行符
        dict_data = eval(trim_data)                # 使用eval函数将字符串转为列表
        length = len(dict_data)
        for i in range(length):
            keys += eval(dict_data[i]).keys()
            values += eval(dict_data[i]).values()
        new_dict = dict(zip(keys, values))           # 列表转化字典，这是词库中全部单词和中文释义组成的字典
        query = input('--->你想查询(中英文均可):')
        y = re.search('[a-z]', query)
        if y:
            flag = False             # flag用于标记是否在词库中寻找到对应的单词
            for i in keys:
                if i == query:
                    flag = True
                    print(f'--->查询成功, {query}在词库中的意思为:', end=' ')
                    for j in new_dict.get(i):
                        print(j, end='、')
            time.sleep(3)
            if not flag:
                print(f"--->词库中暂时还没有收录单词{query}哦")
                time.sleep(2)
        elif not y:
            result = [k for (k, v) in new_dict.items() if query in v]
            if result:
                print(f'--->查询到具有"{query}"意思的单词有:', end=' ')
                for i in result:
                    print(i, end='、')
                time.sleep(3)
            elif not result:
                print(f'--->在词库中未查询到相关单词')
                time.sleep(2)

    def online_query(self):
        """
        在线查询模块，由爬虫实现
        :return:
        """
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.50'
        }
        word = input('--->你想在线查询(中英文均可):')
        if word != '':
            data = {
                'i': word,
                'doctype': 'json'
            }
            res = requests.post(url, data=data, headers=headers)
            if res.status_code == 200:
                rdata = res.json()
                if rdata['errorCode'] == 0:
                    print(f"--->查询结果:{rdata['translateResult'][0][0]['tgt']}")
                    time.sleep(3)
            else:
                print('--->查询失败，请检查单词或网络')
                time.sleep(2)

    def query_lexicon(self):
        """
        查看当前词库内容,只导出单词
        :return:
        """
        keys = []           # 保存导出的单词
        count = 0           # 统计单词个数，用于换行处理
        self.config.read('info.ini')
        g = open(self.words_file, 'r+')
        data = g.readlines()  # 读取个人词库内容
        trim_data = str(data).replace(r'\n', '')  # 除去换行符
        dict_data = eval(trim_data)  # 使用eval函数将字符串转为列表
        length = len(dict_data)
        for i in range(length):
            keys += eval(dict_data[i]).keys()
        print('--->您当前词库单词如下:')
        for j in keys:
            print(j, end='|')
            count += 1
            if count % 10 == 0:
                print("\n")
        time.sleep(2)

    def main_face(self):
        self.config.read('info.ini')
        username = self.config.get('init', 'username')
        total = self.config.get('init', '词库量')
        print(f'用户: {username}\n个人词库总量: {total}\n时间: {self.time_to_study}')
        print('>>>>>1、输入测试单词<<<<<\n' +
              '>>>>>2、学习测试单词<<<<<\n' +
              '>>>>>3、本地单词查询<<<<<\n' +
              '>>>>>4、在线查询单词<<<<<\n' +
              '>>>>>5、查看本地词库<<<<<\n' +
              '>>>>>6、退出<<<<<')
        ans = input('--->your options:')
        if ans == '1':
            system_para = os.system('cls')
            self.words_add()
        elif ans == '2':
            system_para = os.system('cls')
            self.words_test()
        elif ans == '3':
            system_para = os.system('cls')
            self.local_query()
        elif ans == '4':
            system_para = os.system('cls')
            self.online_query()
        elif ans == '5':
            system_para = os.system('cls')
            self.query_lexicon()
        elif ans == '6':
            sys.exit(0)


if __name__ == '__main__':
    obj = Helper()
    while True:
        obj.main_face()
