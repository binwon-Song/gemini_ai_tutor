import speech_recognition as sr
import sys
import sounddevice as sd
r = sr.Recognizer()
# 마이크 설정
r.energy_threshold = 4000
r.dynamic_energy_threshold = True
r.pause_threshold = 1.5  # 음성이 멈춘 후 1.5초 대기
r.phrase_threshold = 0.3  # 구문 시작 감지 임계값 - 기본값: 0.3
r.non_speaking_duration = 1.0  # 음성이 아닌 구간 감지 시간 - 기본값: 0.5
def safe_speech_recognition():
    """안전한 음성 인식 - 타임아웃 오류 처리"""
    try:
        with sr.Microphone() as source:
            print("주변 소음 수준을 조정하고 있습니다...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("음성 인식을 시작합니다. 10초 내에 말씀해 주세요...")
            
            # 타임아웃을 충분히 주고, 구문 시간 제한도 설정
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            
            print("음성 인식 중...")
            text = r.recognize_google(audio, language='ko-KR')
            print(f"인식된 텍스트: {text}")
            return text
            
    except sr.WaitTimeoutError:
        print("시간 초과: 음성이 감지되지 않았습니다.")
        return None
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
        return None
    except sr.RequestError as e:
        print(f"음성 인식 서비스 오류: {e}")
        return None
    
def interactive_speech_recognition():
    """대화형 음성 인식"""
    print("명령어: 's' = 음성 인식 시작, 'q' = 종료")
    
    while True:
        command = input("\n명령을 입력하세요 (s/q): ").lower()
        
        if command == 'q':
            print("프로그램을 종료합니다.")
            break
        elif command == 's':
            text = safe_speech_recognition()
            if text:
                print(f"text recogniztion complete")
                return text
        else:
            print("잘못된 명령입니다. 's' 또는 'q'를 입력해주세요.", file=sys.stderr)

def text_to_speech(text,tts):
    wav = tts.tts(text=text)
    sd.play(wav, samplerate=tts.synthesizer.output_sample_rate)
    sd.wait()

    # Example voice cloning with YourTTS in English, French and Portuguese
    # tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to(device)
    # tts.tts_to_file("This is voice cloning.", speaker_wav="my/cloning/audio.wav", language="en", file_path="output.wav")
    # tts.tts_to_file("C'est le clonage de la voix.", speaker_wav="my/cloning/audio.wav", language="fr-fr", file_path="output.wav")
    # tts.tts_to_file("Isso é clonagem de voz.", speaker_wav="my/cloning/audio.wav", language="pt-br", file_path="output.wav")