import streamlit as st
from groq import Groq
import google.generativeai as genai
import PIL.Image
import requests
import time
import sqlite3

# --- 1. GİZLİ BAĞLANTI VE AYARLAR ---
# Bu anahtarları Streamlit Cloud panelindeki "Secrets" kısmına eklemeyi unutma!
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
IMGBB_API_KEY = st.secrets["IMGBB_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
vision_model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="EcoLab AI", page_icon="🌱", layout="wide")

# --- 2. VERİTABANI İŞLEMLERİ (KALICILIK) ---
def veritabani_hazırla():
    conn = sqlite3.connect('deney_verileri.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vitrin 
                 (foto TEXT, sinif TEXT, konu TEXT)''')
    conn.commit()
    conn.close()

def vitrine_ekle_kalici(url, sinif, konu):
    conn = sqlite3.connect('deney_verileri.db')
    c = conn.cursor()
    c.execute("INSERT INTO vitrin VALUES (?, ?, ?)", (url, sinif, konu))
    conn.commit()
    conn.close()

def vitrini_getir_kalici():
    conn = sqlite3.connect('deney_verileri.db')
    c = conn.cursor()
    c.execute("SELECT * FROM vitrin ORDER BY rowid DESC")
    veriler = c.fetchall()
    conn.close()
    return veriler

veritabani_hazırla()

# --- 3. YARDIMCI FONKSİYONLAR ---
def foto_yukle_imgbb(file):
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY}
        files = {"image": file.getvalue()}
        res = requests.post(url, payload, files=files).json()
        return res["data"]["url"]
    except: return None

def fotograf_uygun_mu(yuklenen_dosya):
    try:
        yuklenen_dosya.seek(0)
        img = PIL.Image.open(yuklenen_dosya)
        istek = """Görseli şu 3 kriter açısından incele: 
        1. İNSAN YÜZÜ var mı? 
        2. ŞİDDET veya KORKU içeriği var mı? 
        3. UYGUNSUZ (Cinsel vb.) bir içerik var mı?
        
        Eğer bunlardan biri varsa 'YASAK' yaz. 
        Eğer bunlar yoksa ve bir makete, deneye veya projeye benziyorsa 'UYGUN' yaz.
        Sadece tek kelime cevap ver."""
        cevap = vision_model.generate_content([istek, img])
        return cevap.text.strip().upper()
    except: return "UYGUN"

# --- 4. YAN PANEL (TOPLULUK VİTRİNİ) ---
konu_listesi = {
    "5. Sınıf": ["Güneş, Dünya ve Ay", "Canlılar Dünyası", "Kuvvetin Ölçülmesi", "Madde ve Değişim", "Işığın Yayılması"],
    "6. Sınıf": ["Güneş Sistemi ve Tutulmalar", "Vücudumuzdaki Sistemler", "Kuvvet ve Hareket", "Madde ve Isı", "Ses ve Özellikleri"],
    "7. Sınıf": ["Güneş Sistemi ve Ötesi", "Hücre ve Bölünmeler", "Kuvvet ve Enerji", "Saf Madde ve Karışımlar", "Işığın Madde ile Etkileşimi"],
    "8. Sınıf": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri"]
}

with st.sidebar:
    st.title("🌍 Topluluk Vitrini")
    gelen_veriler = vitrini_getir_kalici()
    if gelen_veriler:
        sutunlar = st.columns(2)
        for i, (f_url, f_sinif, f_konu) in enumerate(gelen_veriler):
            with sutunlar[i % 2]:
                st.image(f_url, use_container_width=True)
                st.caption(f"{f_sinif} | {f_konu}")
    else:
        st.info("Henüz paylaşım yok. İlk sen paylaş! 😊")
    
    st.divider()
    st.header("🎓 Bilgilerini Seç")
    sinif = st.selectbox("Kaçıncı sınıfa gidiyorsun?", list(konu_listesi.keys()))
    konu = st.selectbox("Ünite Seçimi:", konu_listesi[sinif])
    atiklar = st.multiselect("Malzeme Depon:", ["Plastik Şişe", "Karton Kutu", "Gazete", "Kapak", "Pipet", "Süt Kutusu", "Fener", "Ayna", "Büyüteç"])
    zorluk = st.select_slider("Zorluk Seviyesi:", options=["Fark Etmez", "Kolay", "Orta", "Zor"], value="Fark Etmez")

# --- 5. ANA EKRAN ---
st.title("🌱 EcoLab AI: Atıktan Bilime")

if 'deney_hazir' not in st.session_state: st.session_state.deney_hazir = False
if 'deney_metni' not in st.session_state: st.session_state.deney_metni = ""

if st.button("Deneyi Tasarla! ✨", use_container_width=True):
    if not atiklar:
        st.error("Lütfen malzeme seç!")
    else:
        with st.spinner('Deneyin hazırlanıyor...'):
            komut = f"{sinif} {konu} ünitesi için {atiklar} ile Türkçe bir deney hazırla. Başlıkları büyük ve kalın yap."
            res = client.chat.completions.create(messages=[{"role":"user","content":komut}], model="llama-3.3-70b-versatile")
            st.session_state.deney_metni = res.choices[0].message.content
            st.session_state.deney_hazir = True
            st.balloons()
            st.rerun()

if st.session_state.deney_hazir:
    st.success(f"Deney başarıyla hazırlandı! ✅")
    st.markdown(st.session_state.deney_metni)
    
    st.divider()
    # PDF HATASI ALMAMAK İÇİN .TXT OLARAK İNDİRME
    st.download_button("📄 Deney Raporunu İndir (.txt)", data=st.session_state.deney_metni, file_name="ecolab_deney.txt", use_container_width=True)
    
    # GERİ BİLDİRİM FORMU
    with st.expander("😊 Gelişim İçin Fikir Ver"):
        st.components.v1.iframe("https://forms.gle/kKBKzXZhYCDRKbg1A", height=350)
    
    if st.button("🗑️ Baştan Başla", use_container_width=True):
        st.session_state.deney_hazir = False
        st.session_state.deney_metni = ""
        st.rerun()

    st.divider()
    st.subheader("📸 Deneyini Vitrine Gönder")
    foto_dosya = st.file_uploader("Fotoğraf seç!", type=["jpg", "png", "jpeg"])

    if foto_dosya is not None:
        if st.button("Onayla ve Vitrine Gönder 🚀"):
            with st.spinner('AI Analiz Ediyor...'):
                sonuc = fotograf_uygun_mu(foto_dosya)
                if "YASAK" in sonuc:
                    st.error("⚠️ Üzgünüm, güvenlik kuralları gereği yüz veya uygunsuz içerik içeren fotoğrafları paylaşamam.")
                else:
                    link = foto_yukle_imgbb(foto_dosya)
                    if link:
                        vitrine_ekle_kalici(link, sinif, konu)
                        st.success("✅ Deneyin Topluluk Vitrinine Eklendi!")
                        st.snow()
                        time.sleep(2)
                        st.rerun()

# --- 6. İMZA ---
st.divider()
st.markdown("<h5 style='text-align: center;'>EcoLab AI © 2026 | Damla</h5>", unsafe_allow_html=True)
