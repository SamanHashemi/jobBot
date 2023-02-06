import re
import time
import Config as config
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

JOB_TITLE = "//h1[@class='job_title']"
COMPANY_TITLE = "//section[@class='location_and_company']/h3/span/a"
LOCATION_INFO = "//section[@class='location_and_company']/h3/a/span"
DESCRIPTION = "//div[@class='jobDescriptionSection']"
SALARY = "//span[@class='data t_compensation']"
LOGIN_PAGE = "https://www.linkedin.com/home"


class ZipRecruiter:
    def __init__(self):
        print("We're initiating over here")
        try:
            options = Options()
            ua = UserAgent()
            user_agent = ua.random
            print(user_agent)
            options.add_argument(f'user-agent={user_agent}')
            self.driver = uc.Chrome(
                options=options,
                service=Service("/usr/local/bin/chromedriver")
            )
            self.driver.get(LOGIN_PAGE)
            print("Trying to Log In")
        except Exception as e:
            print("WARNING: Chrome Driver" + str(e))
        try:
            self.driver.find_element(
                By.XPATH,
                "//input[@autocomplete='username']"
            ).send_keys(config.linkedInEmail)
            time.sleep(0.25)
            self.driver.find_element(
                By.XPATH,
                "//input[@autocomplete='current-password']"
            ).send_keys(config.password).send_keys(config.linkedInPassword)
            time.sleep(0.25)
            self.driver.find_element("type", 'submit').click()
            time.sleep(30)
        except Exception as e:
            print("ERROR: Couldn't Log In" + str(e))
        else:
            print("Logged In!")

    def get_page_link(self, position, page):
        # TODO: Create util.py including all website urls
        search = position.replace(' ', '%20')
        url = "https://www.linkedin.com/jobs/search/?" + \
              "&f_AL=true&f_WT=2" + \
              "&keywords=" + search + \
              "&refresh=true" + \
              "&start=" + str(page)*25
        self.driver.get(url)
        time.sleep(5)

    def smooth_scroll(self, height):
        for i in range(1, height, 5):
            self.driver.execute_script("window.scrollTo(0, {});".format(i))

    def center_item(self, item):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'})",
            item
        )

    def get_item_text(self, item):
        text_item = self.driver.find_element(By.XPATH, item)
        return WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(text_item)).text

    def zip_link_apply(self):
        for position in config.positions:
            for page in range(0, 20):
                self.get_page_link(position, page)  # TODO: Iterate over all jobs titles in config
                time.sleep(1)
                jobs = self.driver.find_elements(
                    By.XPATH,
                    "//button[contains(text(), '1-Click Apply')]/../../div[@class='job_title_and_org']//a[contains(@class,'job_link')]"
                )
                job_urls = [url.get_attribute('href') for url in jobs]
                print(job_urls)

                for url in job_urls:
                    try:
                        self.driver.get(url)
                        time.sleep(1)

                        # Get information about the job
                        description = ""
                        try:
                            title = self.get_item_text(JOB_TITLE)
                            company = self.get_item_text(COMPANY_TITLE)
                            location = self.get_item_text(LOCATION_INFO)
                            description = self.get_item_text(DESCRIPTION)
                        except Exception as e:
                            print("Couldn't get information about the position: ", str(e))
                        try:
                            salary = self.get_item_text(SALARY)
                        except:
                            salary = "No salary posted"

                        year_text = re.findall(r"\d+.*years.*$", description)
                        min_experience = max([int(s) for s in re.search(r"\d+", year_text[0]).group(0)]) if len(year_text) else 0

                        apply_button = self.driver.find_element(By.XPATH, "//a[@class='pc_control pc_link ']")

                        # If the title or description doesn't contain unwanted words, and years exp is high enough
                        if any((fail_word := title_word) in title for title_word in config.avoid_words):
                            print("Did not apply to: ", title)
                            print("There was a mismatch word in the title: ", fail_word)
                        elif any((fail_word := word) in description for word in config.avoid_words):
                            print("Did not apply to: ", title)
                            print("There was a mismatch word in the description: ", fail_word)
                        elif min_experience > config.years_exp:
                            print("Did not apply to: ", title)
                            print("Experience Required was too high ", min_experience)
                        else:
                            print("Applying to: ", title)
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(apply_button)).click()
                            # TODO: Additional Question Answers loop
                            # while True: break if we reach a question we don't have the answer for
                            # if we find a question that we don't have an answer for:
                            # Save all the questions as a separate text lines
                            # Associate the text file to a the company information (link, title, description, etc..)
                            # Once the application has finished running compile all the qs and ask them via terminal
                            # Save the relevant questions for the the future applications
                            # Once the user has filled the information for a particualr job go back and apply to that job
                            # else:
                            # if we have the answer fill it out and continue
                            if True:  # Change to ensure button was clicked w no need for questions
                                print("Applied To: " + str(company))
                                print("For position: " + str(title))
                                print("Located In: " + str(location))
                                print("Paying: " + str(salary))
                                print("With these requirements: " + str(description))

                        time.sleep(1)

                    except Exception as e:
                        print("ERROR: Could not apply to that job. errmsg: " + str(e))  # TODO: Add the job title and send the info to a DB
                        time.sleep(5)


ZipRecruiter().zip_link_apply()
