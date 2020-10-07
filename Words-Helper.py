import random

from PySide2.QtWidgets import QApplication, QMessageBox, QInputDialog, QLineEdit, QVBoxLayout, QLabel
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from configparser import ConfigParser
import datetime, os, requests, re
from lxml import etree


class Words_Helper:
    """
    成员变量模块
    """
    # 父目录，用于保存相关文件，在用户的D盘创建
    parent_dir = "D://Words-Helper"
    # 配置文件保存路径
    info_file = "D://Words-helper/info.ini"
    # 个人词库文件保存路径
    lexicon_file = "D://Words-helper/个人词库.txt"
    # ui文件保存路径
    ui_file = "D://Words-helper/reBuild.ui"
    # 配置文件对象
    config = ConfigParser()
    # 首次打开时间
    init_open = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 记录词库量
    lexicon = 0
    # 记录学习天数
    interval = 0
    # 记录次数
    times = 0
    # 当天日期
    day_time = ''
    # 保存读取的词库单词
    lexicon_words = {}
    # 保存当天单词
    words_today = {}
    # 记录今日测试正确率
    lr = 0
    # 记录总体正确率
    lr_total = 0
    # 记录薄弱单词
    weak_words = []
    # ui文件下载地址
    ui_url = "https://www.iloveyou3000.cn/Words-Helper/reBuild.ui"
    # 今日热点网址
    url = "http://top.baidu.com/buzz/shijian.html"
    header = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }

    def dir_create(self):
        """
        创建根目录和软件所需文件
        :return:
        """
        # 首先判断是否存在父目录
        if not os.path.exists(self.parent_dir):
            os.mkdir(self.parent_dir)
            g_info = open(self.info_file, 'wb')
            g_lexicon = open(self.lexicon_file, 'wb')
            g_ui = open(self.ui_file, 'wb')
            res = requests.get(url=self.ui_url, headers=self.header).content
            g_ui.write(res)
            g_ui.close()
            g_info.close()
            g_lexicon.close()

    def configuration(self):
        """
        配置文件的初始化
        :return:
        """
        self.config.read(self.info_file)     # 此时配置文件为空
        # 新增初始化模块，并对参数初始化设置
        if not "init" in self.config.sections():
            self.config.add_section("init")
            self.config.set("init", '用户名', '')
            self.config.set("init", '词库量', '0')
            self.config.set("init", 'times', '0')
            self.config.set("init", '总体学习正确率', '0')
            self.config.set("init", 'version', 'v1.1')
            self.config.set("init", '首次启动时间', self.init_open)
            self.config.write(open(self.info_file, 'w'))
        # 下面是对times进行自增操作，以记录用户的启动次数,同时新增记录模块
        times = self.config.getint("init", 'times')
        section_name = datetime.datetime.now().strftime("%Y-%m-%d")
        # 赋值给全局变量，这样所有的方法共享该times,因为用户每打开一次软件，对应一个times
        self.times = times
        # 将当天日期赋值给day_time变量，以供其他函数和变量使用
        self.day_time = section_name
        if not section_name in self.config.sections():
            self.config.add_section(f"{section_name}")
            self.config.set(f'{self.day_time}', '今日学习单词', '{}')
            self.config.set(f'{self.day_time}', '学习单词量', '0')
            self.config.set(f'{self.day_time}', '学习正确率', '[]')
            self.config.set(f'{self.day_time}', '本次薄弱单词', '[]')
            self.config.write(open(self.info_file, 'a+'))
        times += 1
        self.config.set("init", 'times', str(times))
        self.config.write(open(self.info_file, 'w'))

    def used_days(self):
        """
        计算用户的使用天数
        :return:
        """
        # 读取首次创建时间，以计算间隔天数
        self.config.read(self.info_file)
        origin_time = self.config.get('init', '首次启动时间').split(" ")[0].split("-")
        now = datetime.datetime.now().strftime("%Y-%m-%d").split("-")
        d1 = datetime.datetime(int(origin_time[0]), int(origin_time[1]), int(origin_time[2]))
        d2 = datetime.datetime(int(now[0]), int(now[1]), int(now[2]))
        interval = (d2 - d1).days
        self.interval = interval
        self.config.set('init', '学习天数', str(interval + 1))
        self.config.write(open(self.info_file, 'w'))

    def ui_design(self):
        """
        ui文件导入模块
        :return:
        """
        # 加载ui文件
        file = QFile(self.ui_file)
        file.open(QFile.ReadOnly)
        file.close()
        self.window = QUiLoader().load(file)
        # 设置窗口名称
        self.window.setWindowTitle("单词助手")

        # 设置用户信息
        lexicon = self.config.getint('init', '词库量')
        self.window.lexicon.setText(str(lexicon))
        self.window.study_days.setText(str(self.interval + 1))

        # 赋值全局变量，便于其他函数调用
        self.lexicon = lexicon

        self.config.read(self.info_file)
        # 下面是判断用户是否是第一次使用软件
        if self.times == 0:
            username = QInputDialog.getText(self.window, 'Welcome', "你好，我是你的单词助手Allen\n为自己起一个昵称吧^_^")
            self.config.set('init', '用户名', str(username[0]))
            self.config.write(open(self.info_file, 'w'))
            self.window.username.setText(str(username[0]))
        username = self.config.get('init', '用户名')
        self.window.username.setText(username)
        QMessageBox.about(self.window, 'Hello', f'{username},我们已经认识{self.interval + 1}天啦\n我会一直陪你背单词哒')

    def hotTopic(self):
        """
        今日热点模块
        :return:
        """
        page_data = requests.get(url=self.url, headers=self.header)
        page_data = page_data.content.decode('gbk')
        html = etree.HTML(page_data)
        info_list = html.xpath('//div[2]//tr/td[@class="keyword"]/a[1]/text()')
        url_list = html.xpath('//div[2]//tr/td[@class="keyword"]/a[1]/@href')
        vbox = QVBoxLayout()
        count = 0
        for i in info_list[0:4]:
            label = QLabel()
            label.setText(f'<a href=\"{url_list[count]}\">{i}</a>')
            label.setOpenExternalLinks(True)
            label.setStyleSheet("margin-left:auto;margin-right:auto;font:15px;")
            vbox.addWidget(label)
            count += 1
        self.window.hotTopic.setLayout(vbox)
        self.window.btn_show.setVisible(False)


    def controller(self):
        """
        信号和槽函数绑定模块，这里借用MVC模型中的思想，将该模块称为控制器【controller】模块
        :return:
        """
        self.window.input_box.setPlaceholderText("请在这里输入测试单词\n建议以'apple:苹果'形式进行录入\n如果有多个词义，用逗号隔开即可")
        # 用户名按钮点击事件
        self.window.label1.clicked.connect(self.username_change)
        # 热点显示label绑定
        self.window.btn_show.clicked.connect(self.hotTopic)
        # 输入按钮的槽函数绑定
        self.window.input_btn.clicked.connect(self.words_input)
        # 测试按钮绑定
        self.window.test_btn.clicked.connect(self.words_test)
        self.window.query_box.setPlaceholderText("请输入查询单词或中文词义")
        # 本地查询绑定
        self.window.local_query.clicked.connect(self.local_query)
        # 在线查询绑定
        self.window.online_query.clicked.connect(self.online_query)
        # 词库查询绑定
        self.window.lexicon_query.clicked.connect(self.lexicon_query)

    def username_change(self):
        """
        用户名更改模块
        :return:
        """
        self.config.read(self.info_file)
        new_name = QInputDialog.getText(self.window, '更改用户名', '请输入新的用户名', QLineEdit.Normal)
        while len(new_name[0]) > 6:
            QMessageBox.warning(self.window, 'Error', '用户名过长，请重新输入')
            new_name = QInputDialog.getText(self.window, 'Username Update', '请输入新的用户名', QLineEdit.Normal)
        # 从while循环出来之后，new_name长度一定小于等于6，再判断是否为空即可
        if new_name[0] != '':
            self.config.set('init', '用户名', str(new_name[0]))
            self.config.write(open(self.info_file, 'w'))
            self.window.username.setText(str(new_name[0]))
            QMessageBox.information(self.window, '提示', '更改成功!')

    def words_input(self):
        """
        单词输入模块
        :return:
        """
        input_content = self.window.input_box.toPlainText()
        # 对输入内容按行分割,一行就是一个单词和词义
        input_content = re.split("[\n]", input_content.strip())
        # 进行分割
        for ele in input_content:
            ele = re.split("[:：]", ele)
            # 由于词义往往不止一个，所以将其分割成列表
            ele[1] = re.split("[,，]", ele[1])
            # 键值对形式保存单词和词义【今日】
            self.words_today[ele[0]] = ele[1]
        # 单词重复判断机制,导出词库单词
        g = open(self.lexicon_file)
        for k in g.readlines():
            keys = list(eval(k.strip("\n")).keys())
            values = list(eval(k.strip("\n")).values())
            union = zip(keys, values)
            self.lexicon_words.update(dict(union))
        g.close()
        for r in list(self.words_today.keys()):
            if r in self.lexicon_words.keys():
                del self.words_today[r]
                QMessageBox.warning(self.window, 'Error', f"在词库中找到了单词{r}，不能重复保存呢")
        self.config.read(self.info_file)
        # 读取配置文件中的字典内容以添加新增内容
        read_words = eval(self.config.get(f"{self.day_time}", '今日学习单词'))  # 字符串转字典
        # 添加今日内容,并写入配置文件
        read_words.update(self.words_today)
        self.config.set(f'{self.day_time}', '今日学习单词', str(read_words))
        self.config.set(f"{self.day_time}", '学习单词量', str(len(read_words.keys())))
        # 统计词库量
        self.lexicon += len(self.words_today.keys())
        self.config.set('init', '词库量', str(self.lexicon))
        self.config.write(open(self.info_file, 'w'))
        # 更新词库内容
        g = open(self.lexicon_file, 'a+')
        g.write(str(read_words) + '\n')
        g.close()
        self.words_today.clear()     # 清空字典，以重新统计
        # 更新界面信息
        self.window.input_box.clear()
        self.window.lexicon.setText(str(self.lexicon))
        QMessageBox.about(self.window, 'Save Tips', '保存成功!')


    def words_test(self):
        """
        单词测试模块
        :return:
        """
        # 不能同时选中两个选项
        if self.window.today_check.isChecked() and self.window.lexicon_check.isChecked():
            QMessageBox.critical(self.window, 'Error', '不能同时选中这两个选项')
        # 也不能两个选项都不选
        if not self.window.today_check.isChecked() and not self.window.lexicon_check.isChecked():
            QMessageBox.critical(self.window, 'Error', '未选择测试类型')
        # 本次单词测试，引入RN算法
        if self.window.today_check.isChecked() and not self.window.lexicon_check.isChecked():
            try:
                # 记录正确个数
                words_count = 0
                # 确定今日单词,从配置文件中读取
                self.config.read(self.info_file)
                self.words_read = eval(self.config.get(f'{self.day_time}', '今日学习单词'))
                words_len = len(self.words_read)
                # 存放已出现的随机数
                flag = []
                # 先获取一个[0，列表长度]之间的随机数
                rand = random.randint(0, words_len - 1)
                # 将data内的元素随机输出
                while (True):
                    # 统计词义正确的个数
                    count = 0
                    # 判断是否已经出现，如果出现则重新获取
                    if rand in flag:
                        rand = random.randint(0, words_len - 1)
                    else:
                        # 保存随机选取的单词
                        word_choose = list(self.words_read.keys())[rand]
                        # 它在字典中的意思
                        word_mean = self.words_read.get(word_choose)
                        mean_user = QInputDialog.getText(self.window, 'Question',
                                                         f"单词{word_choose}有哪些意思呢？", QLineEdit.Normal, '')
                        # 用户输入的词义
                        mean_user = re.split("[,， ]", mean_user[0])
                        for i in mean_user:
                            # 该单词的正确词义
                            for mean in word_mean:
                                if i == mean:
                                    count += 1
                        if (count / len(word_mean)) < 0.5:
                            QMessageBox.about(self.window, 'Tips', '错了一半呢(ｷ｀ﾟДﾟ´)!!')
                            self.weak_words.append(word_choose)
                        elif 0.5 <= (count / len(word_mean)) < 0.8:
                            QMessageBox.about(self.window, 'Tips', '大部分对啦ε=(´ο｀*)))')
                        elif 0.8 <= (count / len(word_mean)) <= 1:
                            QMessageBox.about(self.window, 'Tips', '基本全对୧(๑•̀◡•́๑)૭')
                            # 该正确率区间内的单词可视为掌握
                            words_count += 1
                        flag.append(rand)
                        rand = random.randint(0, words_len - 1)
                        if len(flag) == words_len:
                            break
                self.lr += words_count
                self.config.read(self.info_file)
                # 添加薄弱单词部分
                if not self.weak_words:
                    self.config.set(f"{self.day_time}", '本次薄弱单词', '[]')
                else:
                    weak_words = eval(self.config.get(f"{self.day_time}", '本次薄弱单词'))
                    weak_words.append(self.weak_words)
                    self.config.set(f"{self.day_time}", '本次薄弱单词', str(weak_words))
                # 统计正确单词个数并写入配置文件
                learn_rate = self.lr / len(self.words_read)
                # 获取学习正确率的列表，添加本次测试正确率
                learn_list = eval(self.config.get(f"{self.day_time}", '学习正确率'))
                learn_list.append(learn_rate)
                self.config.set(f"{self.day_time}", '学习正确率', str(learn_list))
                self.config.write(open(self.info_file, 'w'))
                QMessageBox.about(self.window, 'Tips', f'测试完成,本次测试正确率为:{(self.lr / len(self.words_read)) * 100}%')
            except ValueError:
                QMessageBox.critical(self.window, 'Error', '请先输入单词再进行测试哦')
        # 词库单词测试，将结果写入init模块中，仅包括目前的综合正确率
        if self.window.lexicon_check.isChecked() and not self.window.today_check.isChecked():
            try:
                # 记录正确个数
                words_count = 0
                # 读取词库单词
                g = open(self.lexicon_file)
                for k in g.readlines():
                    keys = list(eval(k.strip("\n")).keys())
                    values = list(eval(k.strip("\n")).values())
                    union = zip(keys, values)
                    self.lexicon_words.update(dict(union))
                g.close()
                # 确定词库字典的键长度，也就是self.lexicon_words
                words_len = len(self.lexicon_words)
                # 存放已出现的随机数
                flag = []
                # 先获取一个[0，列表长度]之间的随机数
                rand = random.randint(0, words_len - 1)
                # 将data内的元素随机输出
                while (True):
                    # 统计词义正确的个数
                    count = 0
                    # 判断是否已经出现，如果出现则重新获取
                    if rand in flag:
                        rand = random.randint(0, words_len - 1)
                    else:
                        # 保存随机选取的单词
                        word_choose = list(self.lexicon_words.keys())[rand]
                        # 它在字典中的意思
                        word_mean = self.lexicon_words.get(word_choose)
                        mean_user = QInputDialog.getText(self.window, 'Question',
                                                         f'单词"{word_choose}"有哪些意思呢？', QLineEdit.Normal, '')
                        # 用户输入的词义
                        mean_user = re.split("[,， ]", mean_user[0])
                        for i in mean_user:
                            # 该单词的正确词义
                            for mean in word_mean:
                                if i == mean:
                                    count += 1
                        if (count / len(word_mean)) < 0.5:
                            QMessageBox.about(self.window, 'Tips', '错了一半呢(ｷ｀ﾟДﾟ´)!!')
                            self.weak_words.append(word_choose)
                        elif 0.5 <= (count / len(word_mean)) < 0.8:
                            QMessageBox.about(self.window, 'Tips', '大部分对啦ε=(´ο｀*)))')
                        elif 0.8 <= (count / len(word_mean)) <= 1:
                            QMessageBox.about(self.window, 'Tips', '基本全对୧(๑•̀◡•́๑)૭')
                            # 该正确率区间内的单词可视为掌握
                            words_count += 1
                        flag.append(rand)
                        rand = random.randint(0, words_len - 1)
                        if len(flag) == words_len:
                            break
                self.lr_total += words_count
                self.config.read(self.info_file)
                # 统计正确单词个数并写入配置文件
                learn_rate = self.lr_total / len(self.lexicon_words)
                self.config.set("init", '总体学习正确率', str(learn_rate))
                self.config.write(open(self.info_file, 'w'))
                QMessageBox.about(self.window, 'Tips', f'测试完成,本次测试正确率为:{(self.lr_total / len(self.lexicon_words)) * 100}%')
            except ValueError:
                QMessageBox.critical(self.window, 'Error', '当前词库为空，请先添加单词')

    def local_query(self):
        """
        本地单词查询模块
        :return:
        """
        # 判断是否查询到对应的单词
        flag = False
        # 读取词库单词
        g = open(self.lexicon_file)
        for k in g.readlines():
            keys = list(eval(k.strip("\n")).keys())
            values = list(eval(k.strip("\n")).values())
            union = zip(keys, values)
            self.lexicon_words.update(dict(union))
        g.close()
        user_query = self.window.query_box.text()
        self.window.query_box.clear()
        # 首先判断用户是查询单词还是查询词义
        result = re.search("[a-z]", user_query)
        # 查询单词
        if result:
            for ele in self.lexicon_words.keys():
                if ele == user_query:
                    flag = True
                    # 将查询到的列表转为字符串展示
                    query_result = self.lexicon_words.get(ele)
                    content = ''
                    for k in query_result:
                        content += k + "\n"
                    QMessageBox.about(self.window, 'Result',
                                      f'查询成功!\n单词"{user_query}"在词库中的词义如下:\n{content}')
            # 要查询的单词不在词库中
            if flag == False:
                QMessageBox.warning(self.window, 'Result',
                                  f'查询失败!\n未在词库中找到单词<{user_query}>\n建议使用在线查询')
        else:
            query_content = user_query
            # 用户可能会输入多个词义，先分割
            user_query = re.split("[,， ]", user_query)
            content = ''
            query_result = []
            for ele in user_query:
                query_result = [k for (k,v) in self.lexicon_words.items() if ele in v]
            if query_result:
                for i in query_result:
                    content += i + "\n"
                QMessageBox.about(self.window, 'Result',
                                  f'查询成功!\n词库中具有<{query_content}>词义的单词如下：\n{content}')
            else:
                QMessageBox.warning(self.window, 'Result',
                                  f'查询失败!\n在词库中未查询到相关单词')

    def online_query(self):
        """
        在线查询模块
        :return:
        """
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
        content = self.window.query_box.text()
        self.window.query_box.clear()
        if content != '':
            data = {
                'i': content,
                'doctype': 'json'
            }
            res = requests.post(url, data=data, headers=self.header)
            if res.status_code == 200:
                rdata = res.json()
                if rdata['errorCode'] == 0:
                    QMessageBox.about(self.window, 'Result',
                                      f'单词<{content}>在线查询结果：\n{rdata["translateResult"][0][0]["tgt"]}')
            else:
                QMessageBox.warning(self.window, 'Result',
                                  f'查询失败!\n请检查单词或网络')


    def lexicon_query(self):
        """
        词库查询模块
        :return:
        """
        # 读取词库单词
        g = open(self.lexicon_file)
        for k in g.readlines():
            keys = list(eval(k.strip("\n")).keys())
            values = list(eval(k.strip("\n")).values())
            union = zip(keys, values)
            self.lexicon_words.update(dict(union))
        g.close()
        content = ''
        length = len(self.lexicon_words)
        words_total = list(self.lexicon_words.keys())
        for ele in words_total:
            content += ele + "\n"
        QMessageBox.about(self.window, 'Lexicon', f'当前词库单词个数：{length}\n包括以下单词：\n{content}')


    def __init__(self):
        # 前导模块
        self.dir_create()
        self.configuration()
        self.used_days()
        self.ui_design()
        # 控制器模块
        self.controller()


if __name__ == '__main__':
    app = QApplication()
    nop = Words_Helper()
    nop.window.show()
    app.exec_()