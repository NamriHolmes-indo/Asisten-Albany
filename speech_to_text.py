import queue
import sounddevice as sd
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from TTS.api import TTS
from datetime import datetime
import time
import noisereduce as nr
import win32gui
from buka_prog import launch_app_by_name
import random
import re

is_speaking = False

if torch.cuda.is_available():
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if vram_gb >= 12:
        model_name = "large-v3"
    elif vram_gb >= 10:
        model_name = "medium"
    elif vram_gb >= 5:
        model_name = "small"
    else:
        model_name = "base"
else:
    model_name = "medium"

processor = WhisperProcessor.from_pretrained(f"openai/whisper-{model_name}")
model = WhisperForConditionalGeneration.from_pretrained(
    f"openai/whisper-{model_name}",
    device_map="auto" if torch.cuda.is_available() else None,
    # device_map="cpu",
    offload_folder="offload",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    # torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
)

device = model.device
dtype = next(model.parameters()).dtype

tts = TTS(
    model_path="./model/id-vits/checkpoint_1260000-inference.pth",
    config_path="./model/id-vits/config.json",
    progress_bar=False,
    gpu=torch.cuda.is_available(),
)

q = queue.Queue()
playback_buffer = np.zeros(0, dtype=np.float32)


def callback(indata, frames, time_info, status):
    global is_speaking
    if status:
        print(status)
    if is_speaking:
        return
    q.put(indata.copy())


def speak(text):
    global playback_buffer, is_speaking
    is_speaking = True
    print("🤖 :", text)
    audio = tts.tts(text, speaker="gadis")
    playback_buffer = np.concatenate((playback_buffer, audio))
    sd.play(audio, samplerate=tts.synthesizer.output_sample_rate)
    sd.wait()
    is_speaking = False


def is_voice(buffer, threshold=0.01):
    rms = np.sqrt(np.mean(buffer**2))
    return rms > threshold, rms


def normalize_text(text):
    corrections = {
        "jombra": "jam berapa",
        "pas karam": "sekarang",
        "metropoga": "terbuka",
        "antarpulka": "yang terbuka",
    }
    for wrong, correct in corrections.items():
        if wrong in text:
            text = text.replace(wrong, correct)
    return text


def spell_time(hour, minute):
    angka = [
        "nol",
        "satu",
        "dua",
        "tiga",
        "empat",
        "lima",
        "enam",
        "tujuh",
        "delapan",
        "sembilan",
    ]

    def spell_number(n):
        if n < 10:
            return angka[n]
        elif n < 20:
            return angka[n - 10] + " belas"
        else:
            puluhan = n // 10
            satuan = n % 10
            if satuan == 0:
                return angka[puluhan] + " puluh"
            else:
                return angka[puluhan] + " puluh " + angka[satuan]

    jam = spell_number(hour)
    menit = spell_number(minute)
    return f"{jam} lewat {menit}"


def number_to_words(n):
    angka = [
        "nol",
        "satu",
        "dua",
        "tiga",
        "empat",
        "lima",
        "enam",
        "tujuh",
        "delapan",
        "sembilan",
    ]
    if n < 10:
        return angka[n]
    elif n < 20:
        return angka[n - 10] + " belas"
    else:
        puluhan = n // 10
        satuan = n % 10
        if satuan == 0:
            return angka[puluhan] + " puluh"
        else:
            return angka[puluhan] + " puluh " + angka[satuan]


APP_ALIASES = {
    "db first": "dbeaver",
    "db firsts": "dbeaver",
    "d baver": "dbeaver",
    "etsual": "edge",
    "etjual": "edge",
    "ej": "edge",
    "krom": "chrome",
    "crom": "chrome",
    "jamper": "chrome",
    "kroni": "chrome",
    "chakranata": "cakranata",
    "chakra nata": "cakranata",
    "jakranata": "cakranata",
    "akan apa": "cakranata",
    "jakrana kan": "cakranata",
    "jakrana kan": "cakranata",
    "cakran apa?": "cakranata",
    "cakran apa": "cakranata",
}

OPEN_APP_TRIGGERS = [
    "bukakan",
    "buka aplikasi",
    "hai albani buka",
    "hai albani, buka",
    "albani buka",
    "albani, buka",
    "buka",
]

ALBANI_ALIASES = [
    "albani",
    "albany",
    "al bani",
    "al baniy",
    "al bani",
    "alba",
    "almanik",
    "halal balik",
    "halo balik",
    "albanny",
    "albaniy",
    "al bani ni",
]

GREETING_KEYWORDS = [
    "halo",
    "hai",
    "hei",
    "hey",
    "hello",
    "pagi",
    "siang",
    "sore",
    "malam",
    "oi",
    "woi",
    "bro",
    "permisi",
    "assalamualaikum",
    "salam",
]

ALBANI_RESPONSES = [
    "Hai, Albani di sini, saya sudah aktif",
    "Ya, Albani siap membantu",
    "Halo, Albani aktif",
    "Hai, saya Albani",
]


def normalize_app_names(text: str) -> str:
    for wrong, correct in APP_ALIASES.items():
        if wrong in text:
            text = text.replace(wrong, correct)
    return text


def enum_windows():
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)

    win32gui.EnumWindows(callback, None)
    return windows


def jumlah_aplikasi():
    titles = enum_windows()
    apps = []
    for t in titles:
        if " - " in t:
            app_name = t.split(" - ")[-1]
        else:
            app_name = t
        apps.append(app_name)

    unique_apps = list(set(apps))
    jumlah_apps = len(unique_apps)
    jumlah_apps_text = number_to_words(jumlah_apps)

    return unique_apps, jumlah_apps_text


speak("albani telah aktif, siap menjadi personal asisten")


def extract_app_name(text: str) -> str | None:
    for trigger in OPEN_APP_TRIGGERS:
        if trigger in text:
            return text.split(trigger, 1)[1].strip()
    return None


def sanitize_app_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def handle_open_app_command(text_lower: str) -> bool:
    app_name = extract_app_name(text_lower)

    if not app_name:
        return False

    if not app_name:
        speak("Aplikasi apa yang mau dibuka?")
        return True

    app_name = normalize_app_names(app_name)
    speak(f"Baik, membuka {app_name}")

    try:
        clean_app_name = sanitize_app_name(app_name)
        print("🧼 App name (raw):", repr(app_name))
        print("🧼 App name (clean):", repr(clean_app_name))

        result = launch_app_by_name(clean_app_name)

        if result["status"] == "multiple":
            speak(f"Ada beberapa aplikasi bernama {app_name}")
            speak("Silakan pilih secara manual ya")
            return True

        if result["status"] == "not_found":
            speak(f"Maaf, aplikasi {app_name} tidak ditemukan")
            return True

        speak(f"{result['name']} berhasil dibuka")
        return True

    except Exception as e:
        print("❌ Error buka aplikasi:", e)
        speak(f"Maaf, terjadi kesalahan saat membuka {app_name}")
        return True


def is_greeting(text: str) -> bool:
    return any(word in text for word in GREETING_KEYWORDS)


def contains_albani(text: str) -> bool:
    return any(alias in text for alias in ALBANI_ALIASES)


def handle_greeting(text_lower: str) -> bool:
    if contains_albani(text_lower) and is_greeting(text_lower):
        speak(random.choice(ALBANI_RESPONSES))
        return True

    if contains_albani(text_lower):
        speak(random.choice(ALBANI_RESPONSES))
        return True

    return False


with sd.InputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="float32",
    channels=1,
    callback=callback,
):
    print("🎤 Mulai bicara... (CTRL+C untuk stop)")
    buffer = np.zeros(0, dtype=np.float32)

    while True:
        data = q.get()
        buffer = np.concatenate((buffer, data.flatten()))

        if len(buffer) < 16000 * 5:
            continue

        detected, rms = is_voice(buffer)
        if not detected:
            print(f"🔇 Suara lemah (RMS={rms:.4f}), diabaikan")
            buffer = np.zeros(0, dtype=np.float32)
            continue

        print("⏳ Processing suara...")

        reduced_noise = nr.reduce_noise(y=buffer, sr=16000)
        buffer = np.zeros(0, dtype=np.float32)

        input_features = processor(
            reduced_noise,
            sampling_rate=16000,
            return_tensors="pt",
        ).input_features.to(device=device, dtype=dtype)

        forced_decoder_ids = processor.get_decoder_prompt_ids(
            language="indonesian",
            task="transcribe",
        )

        predicted_ids = model.generate(
            input_features,
            forced_decoder_ids=forced_decoder_ids,
            max_length=225,
            num_beams=5,
            no_repeat_ngram_size=2,
        )

        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[
            0
        ].lower()

        if not text.strip():
            continue

        if len(text.split()) <= 1 and text in ["yep", "ya", "hmm", "uh", "eh"]:
            continue

        text = normalize_text(text)
        text_lower = text.lower()

        now = datetime.now()
        hour = now.hour

        print("👤 Kamu:", text)

        if handle_open_app_command(text_lower):
            continue

        if handle_open_app_command(text_lower):
            continue

        if handle_greeting(text_lower):
            continue

        if any(
            w in text_lower
            for w in ["halo albany", "halo albani", "hai albanni", "halo albanny"]
        ):
            speak("Hai, albani di sini")
            if hour >= 23 or hour < 5:
                speak("kamu kenapa belum tidur")
            continue

        if any(w in text_lower for w in ["kopi", "ngopi", "coffee", "kupi"]):
            speak("Kok ngopi sih, kebanyakan kopi ndak sehat loh buat jantung mu")
            continue

        if any(w in text_lower for w in ["kerja", "kerjaan", "ngerjain"]):
            speak("masih kerja ya, apa tidak lelah")
            if hour >= 23 or hour < 5:
                now_spelled = spell_time(now.hour, now.minute)
                speak(f"Sudah jam {now_spelled} loh, emang ndak ngantuk ?")
            continue

        if any(
            w in text_lower
            for w in ["jam berapa", "pukul berapa", "tunjukkan waktu", "tunjukan waktu"]
        ):
            now_spelled = spell_time(now.hour, now.minute)
            speak(f"Sekarang jam {now_spelled}")
            continue

        unique_apps, jumlah_apps_text = jumlah_aplikasi()

        if any(
            w in text_lower
            for w in [
                "aplikasi yang terbuka",
                "aplikasi terbuka",
                "aplikasi yang berjalan",
            ]
        ):
            if "apa saja" in text_lower:
                speak("Aplikasi yang terbuka saat ini: " + ", ".join(unique_apps))
            else:
                speak(f"Ada {jumlah_apps_text} aplikasi terbuka saat ini.")
            continue

        elif "apakah" in text_lower and "terbuka" in text_lower:
            words = text_lower.split()
            try:
                idx = words.index("apakah")
                app_asked = words[idx + 1]
            except (ValueError, IndexError):
                app_asked = None

            if app_asked:
                found = any(app_asked in app.lower() for app in unique_apps)
                speak(
                    f"Ya, {app_asked} sedang terbuka"
                    if found
                    else f"Tidak, {app_asked} tidak terbuka"
                )
