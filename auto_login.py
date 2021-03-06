import os
import config
import time
import logging
import platform
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class AutoLogin(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_gateway = "http://10.253.0.235/srun_portal_pc?ac_id=3&theme=yd"

        if config.log:  # 记录log
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=logging.INFO)
            handler = logging.FileHandler(os.path.join(config.log_path, "log.txt"))
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            if config.debug:  # debug 在控制台输出
                console = logging.StreamHandler()
                console.setLevel(logging.INFO)
                self.logger.addHandler(console)

        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        operating_system = platform.platform()
        if 'Windows' in operating_system:
            self.path = 'webdriver/chromedriver.exe'
        elif 'Mac' in operating_system:
            self.path = 'webdriver/chromedriver_mac64'
        elif 'Linux' in operating_system:
            self.path = 'webdriver/chromedriver_linux64'
        else:
            self.logger.warning("Not support this system :{}".format(operating_system))
            raise Exception("Not support this system :{}".format(operating_system))

    def _check_network(self):
        '''
        检查网络是否畅通
        :return: Ture为畅通，False为不畅通。
        '''
        try:
            req = requests.get('http://www.baidu.com', timeout=5)
            if 'baidu' in req.text:
                return True
            else:
                return False
        except:
            return False

    def _login_srun(self):
        driver = webdriver.Chrome(executable_path=self.path, options=self.options)
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(10)  # 超时
        try:
            driver.get(self.login_gateway)
        except:
            self.logger.warning("Get gatway out of time....try again soon")
            return
        time.sleep(2)
        username_box = driver.find_element_by_xpath('//*[@id="username"]')
        password_box = driver.find_element_by_xpath('//*[@id="password"]')
        username_box.send_keys(self.username)
        password_box.send_keys(self.password)
        driver.find_element_by_xpath('//*[@id="ctcc-login"]').click()  # 登录
        time.sleep(3)
        driver.quit()
        return

    def _login(self):
        '''
        登录网络
        :return: 成功返回True 失败返回 False
        '''
        i = 1
        while i <= config.retry:
            self.logger.info("Start trying times: {}".format(i))
            self._login_srun()
            time.sleep(5)
            status = self._check_network()
            if status:
                self.logger.info("Loging success")
                return True
            else:
                i += 1
                time.sleep(10)  # 等10秒再尝试
        if i > config.retry:
            self.logger.warning("Out of trying times")
            raise Exception("Out of trying times")

    def start(self):
        self.logger.info("Start watching network status")
        while True:
            # check是否掉线
            self.logger.info("Checking network")
            if self._check_network():
                self.logger.info("Network is good")
            else:
                self.logger.info("Network is disconnected. Try login now.")
                self._login()  # 重新登录
            time.sleep(config.check_time)


if __name__ == "__main__":
    login = AutoLogin(config.username, config.passowrd)
    login.start()
