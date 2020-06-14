from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import asyncio
import time

import ujson
import asyncio
from aiohttp import web

import pandas as pd
import numpy as np
from openpyxl import load_workbook


def try_use(warning_message="Unknown error", warning_func=None):
    def actual_decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except BaseException:
                print(warning_message)
                if warning_func:
                    warning_func()
                return False
            else:
                return True
        return wrapper
    return actual_decorator


"""
def save_info(params, marks, startrow=1):
    df_list = list()

    cols_names = ['Faculty', 'Group', 'Studying form', 'Course', 'Speciality', 'Studying status']

    for i in range(len(params)):
        cur_list = list()
        cur_list.append(params[i])
        df_list.append(pd.DataFrame({cols_names[i]: cur_list}))

    for i in range(len(marks)):
        cur_list = list()
        cur_list.append(marks[i])
        df_list.append(pd.DataFrame({"": cur_list}))

    writer = pd.ExcelWriter('stat.xlsx', engine='openpyxl')
    try:
        book = load_workbook("stat.xlsx")
    except BaseException:
        pass
    else:
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    i = 0
    for df in df_list:
        df.to_excel(writer, sheet_name='new_df', startcol=i, startrow=startrow * 2, index=False)
        i += 1

    writer.save()
"""


class Campus:

    def __init__(self):
        print("Campus obj is creating")
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')

        self.timeout = 1

        self.driver = None
        self.driver_status = True

        self.auth_info = list()

        self.login_url = "https://ecampus.kpi.ua/"
        self.stat_url = "https://campus.kpi.ua/student/index.php?mode=profile"
        self.marks_url = "https://campus.kpi.ua/student/index.php?mode=vedomoststud"

    def close(self):
        if self.driver_status:
            self.driver.close()
            self.driver_status = False

    def page_has_loaded(self):
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    @try_use("self.auth_info is broken")
    async def print_logs_passwords(self):
        for i in self.auth_info:
            print(i)
        return True

    @try_use("self.add_logs_passwords() was crashed")
    async def add_logs_passwords(self, path="E:\\STUDYING\\pass.txt"):
        """
        :append: auth_info : list<list>
        [0] - login
        [1] - password
        """

        with open(path) as f:
            body_info = f.readlines()
            for i in range(int(len(body_info) / 5)):
                student_data = [body_info[2 + 5 * i].replace("\n", ""), body_info[3 + 5 * i].replace("\n", "")]
                self.auth_info.append(student_data)

        return True

    @try_use("self.add_log_password() was crashed")
    async def add_log_password(self, student_data):
        self.auth_info.append(student_data)
        return True

    @try_use("Problem with clicking")
    async def click_login(self):
        button_submit = self.driver.find_elements_by_class_name("btn-block")[0]
        button_submit.click()
        return True

    @try_use("Problem with authorization")
    async def auth_account(self):
        button_login = self.driver.find_elements_by_class_name("btn-lg")[0]
        button_login.click()
        return True

    async def get_campus_marks(self, student_account, startrow=0):
        try:

            self.driver = webdriver.Chrome(chrome_options=self.options)
            self.driver_status = True

            self.driver.get(self.login_url)

            auth_fields = self.driver.find_elements_by_class_name("form-control")

            login_field = auth_fields[0]
            password_field = auth_fields[1]

            print(student_account)

            login = student_account[0]
            password = student_account[1]

            login_field.send_keys(login)
            password_field.send_keys(password)

            if not await self.click_login():
                self.close()
                return False

            # success
            await asyncio.sleep(3)

            if not await self.auth_account():
                self.close()
                return False

            await asyncio.sleep(3)

            self.driver.get(self.marks_url)

            await asyncio.sleep(3)

            name = self.driver.find_elements_by_class_name("title")[0].text[9::][:-1]
            print(name)

            table_id = self.driver.find_elements_by_class_name("cntnt")[0]
            rows = table_id.find_elements_by_tag_name("tr")[7::][:-1]

            marks = list()
            for row in rows:
                try:
                    cols = row.find_elements_by_tag_name("td")
                except BaseException:
                    pass
                else:
                    try:
                        marks.append(int(cols[-2].text))
                    except BaseException:
                        pass

            self.driver.get(self.stat_url)

            await asyncio.sleep(3.5)

            table_id = self.driver.find_elements_by_class_name("cntnt")[0]
            rows = table_id.find_elements_by_tag_name("tr")[4::][:-6]

            faculty = rows[0].find_elements_by_tag_name("td")[0].text
            group = rows[1].find_elements_by_tag_name("td")[0].text
            form_studying = rows[3].find_elements_by_tag_name("td")[0].text
            course_studying = rows[4].find_elements_by_tag_name("td")[0].text
            speciality = rows[5].find_elements_by_tag_name("td")[0].text
            is_studying = rows[6].find_elements_by_tag_name("td")[0].text

            self.close()

        except BaseException:
            self.close()
        else:
            return [faculty, group, form_studying, course_studying, speciality, is_studying], marks

        return False


async def main():
    campus = Campus()
    await campus.add_logs_passwords()

    startrow = 0
    for student_account in campus.auth_info:
        await campus.get_campus_marks(student_account, startrow)
        startrow += 1


if __name__ == '__main__':
    asyncio.run(main())
