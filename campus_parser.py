from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import time

from threading import Thread


def try_use(warning_message="Unknown error", warning_func=None):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except BaseException:
                print(warning_message)
                if not warning_func:
                    return warning_message
                warning_func()
            else:
                return True
        return wrapper
    return actual_decorator


class MarksThread(Thread):
    def __init__(self, student_account):
        Thread.__init__(self)
        self.driver = None
        self.driver_status = True

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')

        self.student_account = student_account

        self.success = False
        self.status = False

        self.login_url = "https://ecampus.kpi.ua/"
        self.stat_url = "https://campus.kpi.ua/student/index.php?mode=profile"
        self.marks_url = "https://campus.kpi.ua/student/index.php?mode=vedomoststud"

        self.timeout = 3

        self._return = None

    def run(self):
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options)

            self.driver.get(self.login_url)

            auth_fields = self.driver.find_elements_by_class_name("form-control")

            login_field = auth_fields[0]
            password_field = auth_fields[1]

            login = self.student_account[0]
            password = self.student_account[1]

            login_field.send_keys(login)
            password_field.send_keys(password)

            answer = self.click_login()
            if isinstance(answer, str):
                self.close()
                self._return = answer
                return

            # success
            time.sleep(self.timeout)

            answer = self.auth_account()
            if isinstance(answer, str):
                self.close()
                self._return = answer
                return

            time.sleep(self.timeout)

            self.driver.get(self.marks_url)

            time.sleep(self.timeout)

            name = self.driver.find_elements_by_class_name("title")[0].text[9::][:-1]

            table_id = self.driver.find_elements_by_class_name("cntnt")[0]
            rows = table_id.find_elements_by_tag_name("tr")[7::][:-1]

            marks = list()
            for row in rows:
                cols = row.find_elements_by_tag_name("td")
                marks.append(int(cols[-2].text))

            self.driver.get(self.stat_url)

            time.sleep(self.timeout)

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
            self._return = list(), list()
        else:
            info = [name, faculty, group, form_studying, course_studying, speciality, is_studying]
            self._return = info, marks

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

    def get_return(self):
        return self._return

    @try_use("Problem with clicking")
    def click_login(self):
        button_submit = self.driver.find_elements_by_class_name("btn-block")[0]
        button_submit.click()

    @try_use("Problem with authorization")
    def auth_account(self):
        button_login = self.driver.find_elements_by_class_name("btn-lg")[0]
        button_login.click()

    def close(self):
        if self.driver_status:
            self.driver.close()
            self.driver_status = False


class Campus:

    def __init__(self):
        print("Campus obj is creating")
        self.auth_info = list()

    @try_use("self.auth_info is broken")
    def print_logs_passwords(self):
        for i in self.auth_info:
            print(i)
        return True

    @try_use("self.add_logs_passwords() was crashed")
    def add_logs_passwords(self, path="E:\\STUDYING\\pass.txt"):
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
    def add_log_password(self, student_data):
        self.auth_info.append(student_data)
        return True

    @staticmethod
    def get_campus_marks(student_account):
        thread = MarksThread(student_account)
        thread.start()
        if thread.join():
            if isinstance(thread.get_return(), str):
                return list(), list(), thread.get_return()
            return thread.get_return()[0], thread.get_return()[1], True
        return list(), list(), False
