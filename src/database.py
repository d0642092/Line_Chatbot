import pymysql

class Database():
    def __init__(self, DB, user, password):
        # __DB like private in java
        self.__DB = DB
        self.__user = user
        self.__password = password
        self.__mapping = {
            'laptopID':
            {'command': 'lapID Like "%{0}%"',
             'keyword': ['laptopID']},
            'Warranty':
            {'command': 'lapWarranty Like "%{0}%',
             'keyword': ['Warranty']},
            'GPU':
            {'command': 'lapGPU Like "%{0}%"',
             'keyword': ['GPU']},
            'CPU':
            {'command': 'lapCPU Like "%{0}%"',
             'keyword': ['CPU']},
            'RAM':
            {'command': 'lapRAM Like "%{0}%"',
             'keyword': ['RAM']},
            'Capacity':
            {'command': '{0} Like "%{1}%"',
             'keyword': ['Attribute', 'Capacity']},
            'Max_Min':
            {'command': '{0} in (select {1}({2}) from laptop )',
             'keyword': ['Attribute', 'Max_Min', 'Attribute']},
            'number1':
            {'command': 'lapPrice between {0} and {1}',
             'keyword': ['number', 'number1']},
            'number':
            {'command': 'lapPrice {0} {1}',
             'keyword': ''},
            'lapNO':
            {'command': ' lapNo = {0}',
             'keyword': ''},
            'date-period':
            {'command': ' disStart between "{0}" and "{1}"',
             'keyword': ['date-period']},
        }

    def __create_where_commend(self, keyword, where):
        checkList = ['laptopID', 'Warranty', 'GPU', 'CPU', 'Capacity', 'RAM',
                     'Max_Min', 'number', 'date-period', 'lapNO']
        for key in checkList:
            try:
                command = ''
                if keyword[key] == '':
                    continue
                # create condition
                command = self.__mapping[key]['command']
                if key == 'number':
                    # check price is between, less or more
                    if keyword['number1'] != '':
                        attr = [str(keyword[item])
                                for item in self.__mapping['number1']['keyword']]
                        command = self.__mapping['number1']['command']
                    elif "小於" in keyword["valueCompare"]:
                        attr = ['<=', str(keyword['number'])]
                    elif "大於" in keyword["valueCompare"]:
                        attr = ['>=', str(keyword['number'])]
                elif key == 'date-period':
                    attr = keyword[key].split('/')
                elif key == 'lapNO':
                    attr = [str(keyword[key]['number'])]
                else:
                    attr = [str(keyword[item])
                            for item in self.__mapping[key]['keyword']]

                # multiple  conditions
                command = command.format(*attr)
                if where == "where ":
                    where += command
                else:
                    where += " and " + command
            except KeyError:
                continue
            return where

    def check_userID(self, userID):
        command = 'insert into users(userID) select "%s" where "%s" not in (select userID from users)' % (
            userID, userID)
        self.__nowUser = userID
        message = self.__execute_command(command, changeList=False)
        return None

    def get_userID(self):
        return self.__nowUser

    # computer information and sorting
    def computer_list(self, event, keyword):
        if event == "電腦":
            if keyword["Action"] == '':
                return {1: "請輸入查詢/關注/移除"}
        else:
            if keyword["orderby"] == '':
                return {1: "請輸入以什麼排序"}
        message = self.__create_computer_command(keyword)
        return message

    def __create_computer_command(self, keyword):
        command = "select distinct lapNO,lapID,if(lapNO in (select lapNO from laptop,discount where lapNO = disNO and CURDATE() between disStart and disEnd),disprice,lapprice) as lapPrice,lapCPU,lapGPU,lapRAM,lapDisk,lapWarranty,lapImage,lapBrand from laptop left join discount on lapNO = disNO "
        command += self.__create_where_commend(keyword, "where ")
        print(command)
        try:
            # check whether need sort
            if keyword["orderby"] != '':
                orderby = ' order by ' + \
                    keyword["orderby"]["Attribute"] + " " + keyword["ASC_DESC"]
            command += orderby
        finally:
            message = self.__execute_command(
                command, onlyExecute=False, discount=False)
            return message

    # attention list
    def attention_list(self, event, keyword):
        select = 'select * '
        From = 'from laptop,attention '
        where = 'where att_NO = lapNO and att_userID = "' + self.__nowUser + '"'
        where = self.__create_where_commend(keyword, where)
        command = select + From + where
        message = self.__execute_command(
            command, onlyExecute=False, discount=False)
        return message

    # computer discount
    def computer_discount(self, event, keyword):
        select = 'select lapNO,lapID,lapPrice,disPrice,disStart,disEnd'
        From = ' from laptop,discount '
        where = 'where lapNO = disNO'
        where = self.__create_where_commend(keyword, where)
        command = select + From + where
        try:
            if keyword["orderby"] != '':
                if keyword["orderby"]["Attribute"] == "lapPrice":
                    orderby = ' order by disPrice ' + keyword["ASC_DESC"]
                else:
                    orderby = ' order by ' + \
                        keyword["orderby"]["Attribute"] + \
                        " " + keyword["ASC_DESC"]
                command += orderby
        finally:
            message = self.__execute_command(command, onlyExecute=False)
            return message

    # change attention list
    def change_attention_list(self, event, keyword):
        if keyword["Action"] == "delete":
            delete = 'delete from attention '
            where = 'where att_userID = "' + \
                self.__nowUser + '" and att_NO in ('
            select = 'select lapNO from laptop ' + \
                self.__create_where_commend(keyword, "where ") + ')'
            command = delete + where + select
        elif keyword["Action"] == 'insert':
            insert = 'insert into attention(att_NO,att_userID)'
            select = 'select lapNO,"' + self.__nowUser + '"'
            From = " from laptop "
            where = self.__create_where_commend(keyword, "where ")
            command = insert + select + From + where
        message = self.__execute_command(command)
        return message

    # execute command: default onlyExecute, if onlyExecute is false, default is discount information
    def __execute_command(self, command, onlyExecute=True, changeList=True, discount=True):
        db = pymysql.connect('localhost', 'username',
                             'password', 'databaseName')
        cursor = db.cursor()
        message = {}
        mesID = 1
        # whether return data information
        if onlyExecute:
            try:
                cursor.execute(command)
                if changeList:
                    message[mesID] = '已完成命令'
            except:
                # add repeat data
                message[mesID] = '資料重複'
        else:
            titles = ['編號', "名稱", "價錢", "CPU", "GPU",
                      "RAM", "硬碟", "保固", "image", "品牌"]
            if discount:
                titles = ['編號', "名稱", "原價", "折扣價", "特價開始", "特價結束"]
            cursor.execute(command)
            results = cursor.fetchall()
            if not results:
                message[mesID] = '沒有資料'
            else:
                for row in results:
                    # push one data
                    information = ''
                    for col, title in zip(row, titles):
                        if col != None:
                            information += title + " : " + str(col) + "\n"
                    message[mesID] = information
        db.commit()
        cursor.close()
        db.close()
        return message
