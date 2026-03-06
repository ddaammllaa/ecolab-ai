import streamlit as st
from groq import Groq

# --- 1. BAĞLANTI VE SAYFA AYARI ---
# Kendi API anahtarını buraya yapıştır
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="EcoLab AI", page_icon="🌱", layout="centered")
st.title("🌱 EcoLab AI: Atıktan Bilime")

# --- 2. TÜM MÜFREDAT ÜNİTELERİ (5-8. SINIF) ---
konu_sozlugu = {
    "5. Sınıf": [
        "Güneş, Dünya ve Ay", "Canlılar Dünyası", "Kuvvetin Ölçülmesi ve Sürtünme", 
        "Madde ve Değişim", "Işığın Yayılması", "İnsan ve Çevre", "Elektrik Devre Elemanları"
    ],
    "6. Sınıf": [
        "Güneş Sistemi ve Tutulmalar", "Vücudumuzdaki Sistemler", "Kuvvet ve Hareket (Bileşke Kuvvet)", 
        "Madde ve Isı (Yoğunluk)", "Ses ve Özellikleri", "Vücudumuzdaki Sistemler ve Sağlığı", "İletim (Elektrik)"
    ],
    "7. Sınıf": [
        "Güneş Sistemi ve Ötesi", "Hücre ve Bölünmeler", "Kuvvet ve Enerji (İş-Enerji)", 
        "Saf Madde ve Karışımlar", "Işığın Madde ile Etkileşimi (Aynalar)", "Canlılarda Üreme ve Gelişme", "Elektrik Devreleri"
    ],
    "8. Sınıf": [
        "Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç (Katı, Sıvı, Gaz)", 
        "Madde ve Endüstri (Periyodik Sistem)", "Basit Makineler", "Enerji Dönüşümleri ve Çevre Bilimi", "Elektrik Yükleri ve Elektrik Enerjisi"
    ]
}

# --- 3. YAN PANEL (KULLANICI SEÇİMLERİ) ---
st.sidebar.header("🎓 Öğrenci Bilgileri")
sinif = st.sidebar.selectbox("Kaçıncı sınıfa gidiyorsun?", list(konu_sozlugu.keys()))

st.sidebar.header("♻️ Malzeme Depon")
atiklar = st.sidebar.multiselect(
    "Elindeki atıkları seç:",
    ["Plastik Şişe", "Karton Rulo", "Pipet", "Eski CD", "Paket Lastiği", "Kapak", 
     "Gazete", "Balon", "Mıknatıs", "İp", "Cetvel", "Su", "Tuz", "Şeker", 
     "Alüminyum Folyo", "Kürdan", "Fener", "Ayna", "Pil", "Kablo"]
)

st.sidebar.header("📚 Ünite Seçimi")
# Seçilen sınıfa göre otomatik güncellenen ünite listesi
konu = st.sidebar.selectbox("Hangi üniteyi çalışalım?", konu_sozlugu[sinif])

st.sidebar.header("🛠️ Hazırlık Seviyesi")
hazirlik_suresi = st.sidebar.select_slider(
    "Deney ne kadar uğraştırıcı olsun?",
    options=["Farketmez", "Pratik (2-5 dk)", "Özenli (10-15 dk)", "Kapsamlı (>20 dk)"]
)

# --- 4. DENEY OLUŞTURMA ---
if st.button("Deneyi Tasarla! ✨"):
    if not atiklar:
        st.error("Lütfen malzeme deposundan seçim yap!")
    else:
        with st.spinner(f'{sinif} {konu} deneyi hazırlanıyor...'):
            try:
                # Yapay zekayı disipline eden "Öğretmen" emri
                komut = f"""
                Sen uzman bir Fen Bilimleri öğretmenisin. 
                SADECE TÜRKÇE konuş. 'together', 'understanding' gibi yabancı kelimeleri ASLA kullanma.
                
                ÖĞRENCİ BİLGİSİ: {sinif}
                SEÇİLEN ÜNİTE: {konu}
                MALZEMELER: {atiklar}
                ZAMAN SINIRI: {hazirlik_suresi}
                
                GÖREV: Sadece seçilen üniteye ({konu}) odaklanarak bilimsel bir deney tasarla. 
                Eğer malzemeler yetersizse, evde bulunan temel şeyleri (tuz, kalem, bardak) ekleyebilirsin.
                Dili 13-14 yaşındaki bir çocuğun anlayacağı kadar SADE tut.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": komut}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2 # Dil hatasını önlemek için düşük yaratıcılık
                )
                
                st.balloons() # Başarı efekti!
                st.success(f"Deney başarıyla hazırlandı! 🧪")
                st.markdown(chat_completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

st.divider()
st.caption("EcoLab AI - Geleceğin Bilim İnsanları İçin")