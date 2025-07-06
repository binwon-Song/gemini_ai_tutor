from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import dotenv
prompt_element='//*[@id="app-root"]/main/side-navigation-v2/bard-sidenav-container/bard-sidenav-content/div[2]/div/div[2]/chat-window/div/input-container/div/input-area-v2/div/div/div[1]/div/div/rich-textarea/div[1]'
prompt_btn_element='//*[@id="app-root"]/main/side-navigation-v2/bard-sidenav-container/bard-sidenav-content/div[2]/div/div[2]/chat-window/div/input-container/div/input-area-v2/div/div/div[3]/div/div[2]'
answer_element='//*[@id="chat-history"]/infinite-scroller'
dotenv.load_dotenv()
google_id=dotenv.get_key(".env", "id")
google_password=dotenv.get_key(".env", "pwd")

def wait_for_element(driver, xpath, timeout=10):
    """Wait for an element to be present and visible in the DOM."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        time.sleep(1)  # 추가로 1초 더 기다림
        return element
    except TimeoutException:
        print(f"Timeout waiting for element: {xpath}")
        return None

def find_conversations_list(driver):
    """Try multiple selectors to find the conversations list."""
    possible_selectors = [
        "//div[contains(@id, 'conversations-list')]",
        "//*[@id='conversations-list-2']",
        "//div[contains(@class, 'conversation')]//parent::div",
        "//div[contains(@class, 'conversations')]",
        "//nav//div[contains(@class, 'conversation')]//parent::div"
        "//*[@id='conversations-list']", 
    ]
    for selector in possible_selectors:
        try:
            print(f"Trying selector: {selector}")
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            print(f"Found conversations list with selector: {selector}")
            return element
        except TimeoutException:
            continue
    
    print("Could not find conversations list with any selector")
    return None

def wait_answer(driver, timeout=60):
    print("Waiting for Gemini to finish generating response...")
    
    try:
        stop_button_selectors = [
            "//button[contains(@aria-label, 'Stop')]",
            "//button[contains(@class, 'stop')]",
            "//button[contains(text(), 'Stop')]",
            "//*[contains(@class, 'stop-icon')]"
        ]
        
        for selector in stop_button_selectors:
            try:
                # Wait for stop button to appear
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print(f"Found stop button: {selector}")
                # Wait for it to disappear
                WebDriverWait(driver, timeout).until_not(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print("Stop button disappeared")
                return True
            except TimeoutException:
                continue
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    
class GeminiUtil:
    def __init__(self, driver):
        self.driver = driver

    def login(self,cvs_target="test"):
        self.driver.get("https://gemini.google.com/")
        # Click the "Sign in" button
        sign_in_button = self.driver.find_element(By.XPATH, "//*[@id='gb']/div/div[1]/a")
        sign_in_button.click()
        # wait_for_element(self.driver, "//input[@type='email']", timeout=10)
        time.sleep(2)

        # Enter email
        email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
        email_input.send_keys(google_id)
        self.driver.find_element(By.XPATH, "//*[@id='identifierNext']/div/button").click()
        time.sleep(3)

        # Enter password
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(google_password)
        self.driver.find_element(By.XPATH, "//*[@id='passwordNext']/div/button").click()
        time.sleep(10)

        print("Waiting for page to load completely...")

        cvs_items = find_conversations_list(self.driver)

        if cvs_items:
            cvs_list = cvs_items.find_elements(By.XPATH, "./child::*")
            print(f"Found {len(cvs_list)} conversation items.")
            
            cvs_target = "test"
            opic_element = None
            
            for item in cvs_list:
                item_text = item.text.strip()
                print(f"Checking item with text: '{item_text}'")
                if item_text == cvs_target:
                    opic_element = item
                    break

            if opic_element:
                print(f"Found element with text '{cvs_target}'")
                opic_element.click()
            else:
                print(f"Element with text '{cvs_target}' not found")
        else:
            print("Could not find conversations list. The page might not be fully loaded or the structure has changed.")
            exit()
    def query(self, prompt_input):
        # prompt_input="how is the weather today?"
        prompt_element_found = wait_for_element(self.driver, prompt_element, timeout=15)
        if prompt_element_found:
            prompt = self.driver.find_element(By.XPATH, prompt_element)
            prompt.click()
            prompt.send_keys(prompt_input)
            
            try:
                send_button = self.driver.find_element(By.XPATH, prompt_btn_element)
                send_button.click()
                wait_answer(self.driver)
                print("Stop icon is gone, now you can get the answer.")
            except NoSuchElementException:
                print("Could not find send button, message might have been sent automatically")
        else:
            print("Could not find prompt element")
    
    def get_answer(self):
        answer_items=self.driver.find_element(By.XPATH, answer_element)
        answer_items_list = answer_items.find_elements(By.XPATH, "./*")
        print(f"Found {len(answer_items_list)} direct child elements (depth 1)")

        # 각 직접 자식 요소의 정보 출력
        for i, child in enumerate(answer_items_list):
            print(f"Child {i+1}: tag={child.tag_name}, text='{child.text[:50]}...'")
        latest_answer_item = answer_items_list[-1]
        latest_answer_id = latest_answer_item.get_attribute('id')
        latest_xpath = f'//*[@id="message-content-id-r_{latest_answer_id}"]'

        latest_answer = self.driver.find_element(By.XPATH, latest_xpath).text
        # print(f"Latest answer: {latest_answer}")
        return latest_answer
