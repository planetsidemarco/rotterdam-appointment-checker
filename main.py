"""
06/08/24
Marco Tyler-Rodrigue
Selenium webscraper for checking rotterdam municipality appointment times
"""

import os
import time
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from deep_translator import GoogleTranslator

XPATHS = {
    "appointment": "//a[@class='styles_button__BEjUn' and @title='Afspraak maken']",
    "overseas": "//input[@class='form-control' and @id='id6']",
    "subject": "//button[@class='btn btn-link btn-block text-left' and @id='id5']",
    "rental": "//select[@class='form-control' and @aria-required='true' and "
    "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:huurOfKoop:field']",
    "postcode": "//input[@type='text' and @class='form-control' and @maxlength='6' and"
    "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:postcodeContainer:postcode']",
    "postcode_input": "//button[@class='btn btn-secondary' and @type='submit' and"
    "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:afspraak']",
    "quantity_input": "//button[@class='btn btn-secondary' and @type='submit' and"
    "@value='button' and @name='verder']",
    "options": "//button[@class='list-group-item list-group-item-action flex-column "
    "align-items-start' and @name='keuzes:0:give-focus']",
    "options_input": "//button[@class='btn btn-secondary' and @type='submit' and @value='button'"
    "and @name='keuzes:0:in-focus:button']",
    "calendar": "//span[@class='input-group-text' and @title='Kies datum ...']",
}


def find_and_interact(element_xpath: str, action: str = "button", query: str = ""):
    """Find elements and interact with them on a webpage

    Args:
        element_xpath (str): expected element name
        action (str, optional): type of element [button, dropdown, textbox]. Defaults to "button".
        query (str, optional): query for dropdown and textbox elements. Defaults to "".
    """
    print(f"Selecting {element_xpath} element")

    element = WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.XPATH, XPATHS[element_xpath]))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    time.sleep(1)

    if action == "dropdown":
        select = Select(element)
        select.select_by_value(query)
    elif action == "textbox":
        element.clear()
        element.send_keys(query)
    else:
        actions = ActionChains(driver)
        actions.move_to_element(element)
        driver.execute_script("arguments[0].click();", element)

    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1])


def get_date_time_text():
    """Extract date and time from webpage and creates textfile with result"""
    time.sleep(1)
    text = driver.find_element(By.TAG_NAME, "body").text
    start, end = "Centrum", "Coolsingel"

    try:
        start_pos = text.index(start) + len(start)
        end_pos = text.index(end)
        filtered_text = text[start_pos:end_pos].strip()
        translated = GoogleTranslator(source="auto", target="en").translate(
            filtered_text
        )
        print("Saving earliest appointment date/time to date_time.txt")
        with open("date_time.txt", "w", encoding="utf-8") as file:
            # Write the string to the file
            file.write(f"{translated}\n")
            file.write(f"\n{BASE_URL}/{APPOINTMENT_ENDPOINT}\n\n")
    except ValueError as e:
        print(e)


def no_bookings_text():
    """Creates text file stating no bookings available"""
    print("Saving output to date_time.txt")
    with open("date_time.txt", "w", encoding="utf-8") as file:
        # Write the string to the file
        file.write("not currently available\n")
        file.write(f"\n{BASE_URL}/{APPOINTMENT_ENDPOINT}\n\n")


def check_for_bookings() -> bool:
    """Helper function to check if no booking text exists on page"""
    bookings = True
    no_booking_text = "Het spijt ons."
    time.sleep(2)
    # Update current url source and get body text
    driver.get("view-source:" + driver.current_url)
    time.sleep(2)
    # Return from source code
    driver.get(driver.current_url.replace("view-source:", ""))
    time.sleep(2)
    current_body_text = driver.find_element(By.TAG_NAME, "body").text
    # Check if no booking text exists on page
    if no_booking_text in current_body_text:
        print("No bookings available")
        no_bookings_text()
        bookings = False
    return bookings


def save_full_page_screenshot(filename: str):
    """Helper function to save screenshot of current webpage

    Args:
        filename (str): name of image file
    """
    time.sleep(1)
    print(f"Saving screenshot to {filename}")
    driver.save_screenshot(filename)


def send_email():
    """Send emails via gmail bot"""
    # Load environment secrets
    env_path = Path("./emailpass.env")
    load_dotenv(dotenv_path=env_path)
    bot_email = f"{os.environ.get('EMAIL_SENDER')}@gmail.com"
    bot_pass = os.environ.get("EMAIL_APP_PASS")
    receiver_email = f"{os.environ.get('EMAIL_RECEIVER')}@gmail.com"

    with open("date_time.txt", "r", encoding="utf-8") as file:
        appointment_times = file.read()

    if "not currently available" in appointment_times:
        attachments = []
    else:
        attachments = ["calendar.png", "options.png"]

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Sending email to {receiver_email} at {current_datetime}")

    message = MIMEMultipart()
    message["From"] = bot_email
    message["To"] = receiver_email
    message["Subject"] = "Rotterdam Municipality Appointment Times"

    # Add body to email
    message.attach(MIMEText(f"Next appointment {appointment_times}", "plain"))

    # Add attachments
    for attachment in attachments:
        filename = os.path.basename(attachment)
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            with open(attachment, "rb") as f:
                img = MIMEImage(f.read(), name=filename)
                message.attach(img)
        else:
            with open(attachment, "rb") as f:
                part = MIMEApplication(f.read(), Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                message.attach(part)

    # Create SMTP session
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(bot_email, bot_pass)
        server.send_message(message)


# Set up Firefox options
firefox_options = Options()
firefox_options.add_argument("--headless")

# Specify the path to Geckodriver
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"
BASE_URL = "https://www.rotterdam.nl"
APPOINTMENT_ENDPOINT = (
    "eerste-inschrijving-in-nederland/start-eerste-inschrijving-in-nederland"
)

# Set up Firefox service
firefox_service = FirefoxService(executable_path=GECKODRIVER_PATH)

# Initialize the Firefox driver with the specified service
driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
driver.maximize_window()
driver.get(f"{BASE_URL}/{APPOINTMENT_ENDPOINT}")

check_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Checking Rotterdam website appointments at {check_datetime}")

find_and_interact("appointment")

find_and_interact("overseas", action="textbox", query="Eerste vestiging buiten Europa")

time.sleep(1)
driver.refresh()
time.sleep(1)

find_and_interact("subject")
find_and_interact("rental", action="dropdown", query="HUUR")
find_and_interact("postcode", action="textbox", query="3039RL")
find_and_interact("postcode_input")
find_and_interact("quantity_input")

if check_for_bookings():
    find_and_interact("options")
    save_full_page_screenshot("options.png")
    get_date_time_text()
    find_and_interact("options_input")
    find_and_interact("calendar")
    save_full_page_screenshot("calendar.png")

driver.quit()

# send_email()
