import streamlit as st
import yfinance as yf
from textblob import TextBlob
import requests
from xml.etree import ElementTree
import time

# Sayfa Düzeni
st.set_page_config(page_title="Borsa Asistanı", page_icon="💰", layout="wide")

st.title("💰 Yatırımcı Asistanı: Haber & Analiz")
st.markdown("**Strateji:** Fiyat her şey değildir. Piyasanın ne konuştuğu daha önemlidir.")

# Yan panel (Sidebar)
with st.sidebar:
    st.header("Ayarlar")
    symbol = st.text_input("Hisse Kodu", "THYAO.IS", help="BIST için sonuna .IS ekleyin (Örn: GARAN.IS)")
    st.info("💡 İpucu: Türk hisseleri için .IS uzantısını unutmayın.")

if st.button("HİSSEYİ ANALİZ ET", type="primary"):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Piyasa Verileri")
        with st.spinner('Fiyatlar çekiliyor...'):
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    st.metric(label="Son Fiyat", value=f"{current_price:.2f} TRY")
                    
                    info = stock.info
                    if 'marketCap' in info:
                        mcap = info['marketCap'] / 1000000000
                        st.write(f"**Piyasa Değeri:** {mcap:.1f} Milyar")
                else:
                    st.warning("Fiyat verisi anlık alınamadı.")
            except Exception as e:
                st.error("Veri çekme hatası.")

    with col2:
        st.subheader("📰 Haberler ve Yorumlar")
        with st.spinner('Haberler taranıyor...'):
            try:
                # Dil ayarı
                lang = "tr" if ".IS" in symbol.upper() else "en"
                gl = "TR" if lang == "tr" else "US"
                
                rss_url = f"https://news.google.com/rss/search?q={symbol}&hl={lang}-{gl}&gl={gl}&ceid={gl}:{lang}"
                response = requests.get(rss_url)
                root = ElementTree.fromstring(response.content)
                
                items = root.findall('./channel/item')
                
                if not items:
                    st.info("Güncel haber bulunamadı.")
                
                total_score = 0
                count = 0
                
                for item in items[:5]:
                    title = item.find('title').text
                    link = item.find('link').text
                    pubDate = item.find('pubDate').text
                    
                    # Analiz
                    blob = TextBlob(title)
                    try:
                        if lang == "tr":
                            score = blob.translate(from_lang='tr', to='en').sentiment.polarity
                        else:
                            score = blob.sentiment.polarity
                    except:
                        score = 0 
                    
                    total_score += score
                    count += 1
                    
                    # Renklendirme
                    if score > 0.1:
                        color = "green"
                        mood = "OLUMLU"
                    elif score < -0.1:
                        color = "red"
                        mood = "OLUMSUZ"
                    else:
                        color = "gray"
                        mood = "NOTR"
                    
                    st.markdown(f"""
                    <div style="padding:10px; border-left: 5px solid {color}; background-color: #f0f2f6; margin-bottom: 10px;">
                        <a href="{link}" style="text-decoration:none; color:black; font-weight:bold;">{title}</a><br>
                        <span style="color:{color}; font-weight:bold;">{mood}</span> <span style="font-size:12px; color:#555;">({pubDate})</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if count > 0:
                    avg = total_score / count
                    st.divider()
                    if avg > 0.05:
                        st.success(f"GENEL ALGI: POZİTİF (+{avg:.2f})")
                    elif avg < -0.05:
                        st.error(f"GENEL ALGI: NEGATİF ({avg:.2f})")
                    else:
                        st.warning(f"GENEL ALGI: KARARSIZ ({avg:.2f})")
                        
            except Exception as e:
                st.error(f"Hata: {e}")