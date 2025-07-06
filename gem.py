from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from TTS.api import TTS

from gem_util import GeminiUtil
import gem_stt

device = "cpu"
options = Options()
# options.add_argument("--headless")  # Runs Chrome in headless mode (no GUI)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False).to(device)


gemini = GeminiUtil(driver)
cvs_title="test"
gemini.login(cvs_title)

for i in range(3):
    voice_text=gem_stt.interactive_speech_recognition()

    gemini.query(voice_text)
    ans=gemini.get_answer()
    print(ans)
    gem_stt.text_to_speech(ans,tts)