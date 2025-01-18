from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import quote
import os
from selenium.webdriver.edge.service import Service

script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Edge options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument(f"user-data-dir={os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default')}")

# Set environment variable
os.environ["WDM_LOG_LEVEL"] = "0"

# Define color styles for printing
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# Read the message from file
with open(f"{script_dir}\\message.txt", "r", encoding="utf8") as f:
    message_template = f.read()

# Display the message template
print(style.YELLOW + '\nThis is your message template:')
print(style.GREEN + message_template)
print("\n" + style.RESET)

# Read contacts from file
contacts = []
with open(f"{script_dir}\\numbers.txt", "r", encoding="utf8") as f:
    for line in f.read().splitlines():
        if line.strip():
            try:
                name, number = line.split("	")  # Split line into name and number
                contacts.append({"name": name.strip(), "number": number.strip()})
            except ValueError:
                print(style.RED + f"Invalid line format: {line}" + style.RESET)

total_contacts = len(contacts)
print(style.RED + f'We found {total_contacts} contacts in the file.' + style.RESET)

# Set the delay for sending the message
delay = 30

# Initialize the Edge WebDriver with the service and options
service = Service(f"{script_dir}\\msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)


print('Once your browser opens up, sign in to web WhatsApp.')
driver.get('https://web.whatsapp.com')
input(style.MAGENTA + "AFTER logging into WhatsApp Web is complete and your chats are visible, press ENTER..." + style.RESET)

# Loop through the contacts and send the message
for idx, contact in enumerate(contacts):
    name = contact["name"]
    number = contact["number"]
    if not number:
        continue

    print(style.YELLOW + f'{idx + 1}/{total_contacts} => Sending message to {name} ({number}).' + style.RESET)

    try:
        # Customize the message with the recipient's name
        personalized_message = message_template.replace("[NAME]", name)
        encoded_message = quote(personalized_message)
        url = f'https://web.whatsapp.com/send?phone={number}&text={encoded_message}'

        sent = False
        for i in range(3):  # Retry up to 3 times
            if not sent:
                driver.get(url)
                try:
                    click_btn = WebDriverWait(driver, delay).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='11']"))
                    )
                except Exception:
                    print(style.RED + f"\nFailed to send message to {name} ({number}), retry ({i + 1}/3)")
                    print("Make sure your phone and computer are connected to the internet.")
                    print("If there is an alert, please dismiss it." + style.RESET)
                else:
                    sleep(1)
                    click_btn.click()
                    sent = True
                    sleep(3)
                    print(style.GREEN + f'Message sent to {name} ({number})' + style.RESET)

    except Exception as e:
        print(style.RED + f'Failed to send message to {name} ({number}): {str(e)}' + style.RESET)

# Close the driver after completion
driver.quit()