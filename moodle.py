from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import json
import re
import os
import requests

class Moodle:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        self.driver = webdriver.Firefox(options=options)
        self.sessionkey = None
        self.cookies = {}

    def login(self, user, passwd):
        self.driver.get("https://moodle.tu-dortmund.de/auth/sso/index.php")
        time.sleep(2)
        
        username = self.driver.find_element(By.ID, "idToken1")
        password = self.driver.find_element(By.ID, "idToken2")
        username.send_keys(user)
        password.send_keys(passwd)
        
        login_btn = self.driver.find_element(By.ID, "loginButton_0")
        login_btn.click()
        
        time.sleep(5)
        
        html = self.driver.page_source
        match = re.search(r'"sesskey":"(.*?)"', html)
        if match:
            self.sessionkey = match.group(1)
            print(f"   Sessionkey: {self.sessionkey}")
        else:
            raise Exception("Sesskey could not be found")
        
        self.cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}

    def logout(self):
        if self.cookies:
            logout_url = f"https://moodle.tu-dortmund.de/login/logout.php?sesskey={self.sessionkey}"
            self.driver.get(logout_url)
            time.sleep(1)

    def load_courses(self, course_limit=10):
        url = f"https://moodle.tu-dortmund.de/lib/ajax/service.php?sesskey={self.sessionkey}&info=core_course_get_recent_courses"
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = [{
            "index":0,
            "methodname":"core_course_get_recent_courses",
            "args":{"limit": course_limit}
        }]
        r = requests.post(url, headers=headers, cookies=self.cookies, json=data)
        r.raise_for_status()
        return r.json()[0]["data"]

    def load_course_page(self, course_id):
        url = f"https://moodle.tu-dortmund.de/course/view.php?id={course_id}"
        r = requests.get(url, cookies=self.cookies)
        r.raise_for_status()
        return r.text

    def extract_content_ids(self, course_page_html):
        search = r'<a.*?href="https://moodle.tu-dortmund.de/mod/resource/view.php\?id=(\d+)".*?>'
        return [m.group(1) for m in re.finditer(search, course_page_html)]

    def extract_assignment_links(self, course_id):
        self.driver.get(f"https://moodle.tu-dortmund.de/course/view.php?id={course_id}")
        time.sleep(1)

        assignments = []
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/mod/assign/view.php?id=']")
        for el in elements:
            title = el.text.strip()
            url = el.get_attribute("href")
            if url not in [a['url'] for a in assignments]:
                assignments.append({"title": title, "url": url})
        return assignments

    def extract_assignment_content(self, assignment_url):
        self.driver.get(assignment_url)
        time.sleep(1)

        try:
            content_el = self.driver.find_element(By.CSS_SELECTOR, ".box")
            content_html = content_el.get_attribute("innerHTML")
        except:
            content_html = "No content found"
        
        return content_html

    def close(self):
        self.logout()
        self.driver.quit()
