import streamlit as st
from groq import Groq
from fpdf import FPDF

# --- 1. BAĞLANTI VE SAYFA AYARI ---
# GitHub'da güvenli kalması için anahtarı secrets üzerinden alıyoruz
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="EcoLab AI", page_icon="🌱", layout="centered")

# --- 2. YAN PANEL (SIDEBAR) ---
st.sidebar.header("🎓 Öğrenci Bilgileri")
sinif = st.sidebar.selectbox("Kaçıncı sınıfa gidiyorsun?", ["5. Sınıf", "6. Sınıf", "7. Sınıf", "8. Sınıf"])

st.sidebar.header("♻️ Malzeme Depon")
atiklar = st.sidebar.multiselect(
    "Elindeki atıkları seç:",
    ["Plastik Şişe", "Karton Kutu", "Eski Gazete", "Pet Şişe Kapağı", "Tuvalet Kağıdı Rulosu", "Pipet", "Süt Kutusu", "Fener", "Ayna", "Büyüteç"]
)

st.sidebar.header("📚 Ünite Seçimi")
konu = st.sidebar.selectbox(
    "Hangi üniteyi çalışalım?",
    ["Güneş, Dünya ve Ay", "Vücudumuzdaki Sistemler", "Kuvvet ve Hareket", "Madde ve Doğası", "Işığın Yayılması", "Canlılar Dünyası"]
)

hazirlik_suresi = st.sidebar.select_slider(
    "Deney ne kadar uğraştırıcı olsun?",
    options=["Farketmez", "Kısa ve Kolay", "Orta", "Kapsamlı Proje"]
)

# --- 3. ANA EKRAN ---
st.title("🌱 EcoLab AI: Atıktan Bilime")
st.write(f"Şu an **{sinif}** seviyesinde, **{konu}** ünitesi için elindeki atıklarla deney tasarlıyoruz.")

if st.button("Deneyi Tasarla! ✨"):
    if not atiklar:
        st.error("Lütfen malzeme deposundan seçim yap!")
    else:
        with st.spinner(f'{sinif} {konu} deneyi hazırlanıyor...'):
            try:
                # Yapay zekaya giden talimat
                komut = f"""
                Sen uzman bir Fen Bilimleri öğretmenisin. 
                SADECE TÜRKÇE konuş. 
                
                ÖĞRENCİ BİLGİSİ: {sinif}
                SEÇİLEN ÜNİTE: {konu}
                MALZEMELER: {atiklar}
                ZAMAN SINIRI: {hazirlik_suresi}
                
                GÖREV: Sadece seçilen üniteye ({konu}) odaklanarak bilimsel bir deney tasarla.
                Deneyin şu bölümleri olsun:
                1. Deneyin Adı
                2. Amacı
                3. Gerekli Malzemeler
                4. Adım Adım Yapılışı
                5. Bilimsel Açıklaması (Çocuğun anlayacağı dilde)
                """

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": komut}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2
                )

                deney_sonucu = chat_completion.choices[0].message.content
                
                st.balloons()
                st.success("Deney başarıyla hazırlandı! 🧪")
                st.markdown(deney_sonucu)

                # --- PDF OLUŞTURMA BÖLÜMÜ ---
                st.divider()
                
                         
                # --- PDF OLUŞTURMA BÖLÜMÜ ---
                st.divider()
                
                def pdf_hazirla(metin):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=12)
                    # Karakterleri PDF dostu hale getiriyoruz
                    duzeltme = {"İ":"I","ı":"i","Ş":"S","ş":"s","Ğ":"G","ğ":"g","Ç":"C","ç":"c","Ö":"O","ö":"o","Ü":"U","ü":"u"}
                    yeni_metin = metin
                    for k, v in duzeltme.items():
                        yeni_metin = yeni_metin.replace(k, v)
                    safe_text = yeni_metin.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, safe_text)
                    return bytes(pdf.output())

                # Butonu göster
                pdf_data = pdf_hazirla(deney_sonucu)
                st.download_button(
                    label="📄 Deneyi PDF Olarak İndir",
                    data=pdf_data,
                    file_name="deney_raporu.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

st.divider()
st.caption("EcoLab AI - Geleceğin Bilim İnsanları İçin")



