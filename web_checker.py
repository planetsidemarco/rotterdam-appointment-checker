"""
06/08/24
Marco Tyler-Rodrigue
Selenium webscraper for checking rotterdam municipality appointment times
"""

import time
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from deep_translator import GoogleTranslator
from rotterdam_xpaths import XPATHS as RotterdamXPaths
from email_bot import current_datetime, send_email, EmailContent


def write_textfile(file_name: str, file_contents: List):
    """Helper function to create text files

    Args:
        file_name (str): name of file to be written
        file_contents (List): text to be written to file
    """
    with open(file_name, "w", encoding="utf-8") as file:
        for line in file_contents:
            # Write the string to the file
            file.write(line)


class WebChecker:
    """Class to check websites"""

    def __init__(self, headless: bool = True):
        # Set up Firefox options
        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")

        # Specify the path to Geckodriver
        geckodriver_path = "/usr/local/bin/geckodriver"
        base_url = "https://www.rotterdam.nl"
        appointment_endpoint = (
            "eerste-inschrijving-in-nederland/start-eerste-inschrijving-in-nederland"
        )
        self.full_url = f"{base_url}/{appointment_endpoint}"

        # Set up Firefox service
        firefox_service = FirefoxService(executable_path=geckodriver_path)

        # Initialize the Firefox driver with the specified service
        self.driver = webdriver.Firefox(
            service=firefox_service, options=firefox_options
        )
        self.driver.maximize_window()
        self.driver.get(self.full_url)
        self.element = None
        self.datetime_filename = "date_time.txt"
        self.no_booking_text = "Het spijt ons."
        self.bookings_available = True

    def refresh_page(self):
        """Helper function to refresh webpage"""
        time.sleep(2)
        # Update current url source and get body text
        self.driver.get("view-source:" + self.driver.current_url)
        time.sleep(0.1)
        # Return from source code
        self.driver.get(self.driver.current_url.replace("view-source:", ""))
        time.sleep(1)

    def no_bookings_available(self) -> bool:
        """Creates text file stating no bookings available"""
        print("No bookings available")
        print(f"Saving output to {self.datetime_filename}")
        no_booking_text = ["not currently available\n", f"\n{self.full_url}\n\n"]
        write_textfile(self.datetime_filename, no_booking_text)
        self.bookings_available = False

    def check_for_bookings(self):
        """Helper function to check if no booking text exists on page"""
        if self.bookings_available:
            self.refresh_page()
            current_body_text = self.driver.find_element(By.TAG_NAME, "body").text
            # Check if no booking text exists on page
            if self.no_booking_text in current_body_text:
                self.no_bookings_available()

    def select_action(self, action: str, query: str = ""):
        """Helper function to select input action

        Args:
            action (str): button, dropdown, textbox
            query (str, optional): query for dropdown and textbox elements. Defaults to "".
        """
        match action:
            case "button":
                actions = ActionChains(self.driver)
                actions.move_to_element(self.element)
                self.driver.execute_script("arguments[0].click();", self.element)
            case "dropdown":
                select = Select(self.element)
                select.select_by_value(query)
            case "textbox":
                self.element.clear()
                self.element.send_keys(query)

    def find_and_interact(self, element_key: str, action: str, query: str):
        """Find elements and interact with them on a webpage

        Args:
            element_xpath (str): expected element name
            action (str, optional): type of input element, defaults to "button".
            query (str, optional): query for dropdown and textbox elements. Defaults to "".
        """
        self.check_for_bookings()
        if self.bookings_available:
            print(f"Selecting {element_key} element")
            # Find element on webpage
            try:
                xpath = RotterdamXPaths[element_key]["xpath"]
                self.element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # Scroll found element into view
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", self.element
                )
                time.sleep(1)
                self.select_action(action, query)
                WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
                self.driver.switch_to.window(self.driver.window_handles[-1])
            except TimeoutException:
                print("TimeoutException: XPATH could not be found")
                self.driver.quit()

    def save_full_page_screenshot(self, filename: str):
        """Helper function to save screenshot of current webpage

        Args:
            filename (str): name of image file
        """
        if self.bookings_available:
            time.sleep(0.5)
            file = f"{filename}.png"
            print(f"Saving screenshot to {file}")
            self.driver.save_screenshot(file)

    def save_date_time_text(self):
        """Extract date and time from webpage and creates textfile with result"""
        time.sleep(0.5)
        text = self.driver.find_element(By.TAG_NAME, "body").text
        start, end = "Centrum", "Coolsingel"

        try:
            start_pos = text.index(start) + len(start)
            end_pos = text.index(end)
            filtered_text = text[start_pos:end_pos].strip()
            # Translate text from dutch to english
            translated_text = GoogleTranslator(source="auto", target="en").translate(
                filtered_text
            )
            print(f"Saving earliest appointment date/time to {self.datetime_filename}")
            booking_text = [f"{translated_text}\n", f"\n{self.full_url}\n\n"]
            write_textfile(self.datetime_filename, booking_text)

        except ValueError as e:
            print(e)

    def export_web_data(self, key: str, save_screenshot: bool, save_textfile: bool):
        """Helper function to save web data for specific pages

        Args:
            key (str): name of web page
            save_screenshot (bool): requirement to save screenshot
            save_textfile (bool): requirement to save textfile
        """
        if save_screenshot:
            self.save_full_page_screenshot(key)
        elif save_textfile:
            self.save_date_time_text()


def web_checker(wc: WebChecker):
    """Main function

    Args:
        wc (Class): WebChecker object
    """
    print(f"Checking Rotterdam website appointments at {current_datetime()}")

    # Iterate through the XPATHS dictionary
    for key, value in RotterdamXPaths.items():
        # Navigate through inputs based on rotterdam_xpaths
        wc.find_and_interact(key, value["action"], value["query"])
        # Additional actions for specific keys
        wc.export_web_data(key, value["screenshot"], value["textfile"])

    wc.driver.quit()


if __name__ == "__main__":
    WC = WebChecker(headless=True)

    web_checker(WC)

    content = EmailContent(
        filename="date_time.txt",
        conditional_string="not currently available",
        allowed_attachments=["calendar.png", "options.png"],
        subject="Rotterdam Municipality Appointment Times",
        body="Next appointment ",
    )

    send_email(content)

    print("Check complete and email sent")
