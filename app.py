import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from xml.etree import ElementTree
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import datetime
import numpy as np

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BorsaEmirhan Pro", page_icon="🦁", layout="wide")

# --- CSS (FINTABLES / INVESTING TARZI) ---
st.markdown("""
<style>
    .metric-container {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 13px; color: #666; font-weight: 600; margin-bottom: 5px; }
    .metric-value { font-size: 18px; font-weight: bold; color: #222; }
    .section-header { color: #1f77b4; font-size: 20px; font-weight: bold; border-bottom: 2px solid #1f77b4; margin-top: 20px; margin-bottom: 10px; padding-bottom: 5px; }
    .news-card { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- HİSSE LİSTESİ (TAM KADRO) ---
BIST_STOCKS = [
    "1BINHO.IS - 1000 YATIRIMLAR HOLDİNG", "ACSEL.IS - ACISELSAN", "ADEL.IS - ADEL KALEMCİLİK", "ADESE.IS - ADESE GAYRİMENKUL",
    "ADGYO.IS - ADRA GYO", "ADLVY.IS - ADİL VARLIK YÖNETİM", "AEFES.IS - ANADOLU EFES", "AFYON.IS - AFYON ÇİMENTO",
    "AGESA.IS - AGESA HAYAT", "AGHOL.IS - AG ANADOLU GRUBU", "AGROT.IS - AGROTECH TEKNOLOJİ", "AGYO.IS - ATAKULE GYO",
    "AHGAZ.IS - AHLATCI DOĞAL GAZ", "AHSGY.IS - AHES GYO", "AKBNK.IS - AKBANK", "AKCNS.IS - AKÇANSA", "AKCVR.IS - AKADEMİ ÇEVRE",
    "AKDFA.IS - AKDENİZ FAKTORİNG", "AKENR.IS - AKENERJİ", "AKFGY.IS - AKFEN GYO", "AKFIS.IS - AKFEN İNŞAAT",
    "AKFK.IS - AK FİNANSAL KİRALAMA", "AKFYE.IS - AKFEN YENİLENEBİLİR", "AKGRT.IS - AKSİGORTA", "AKMGY.IS - AKMERKEZ GYO",
    "AKM.IS - AK YATIRIM", "AKSA.IS - AKSA AKRİLİK", "AKSEN.IS - AKSA ENERJİ", "AKSFA.IS - AK FAKTORİNG",
    "AKSGY.IS - AKİŞ GYO", "AKSUE.IS - AKSU ENERJİ", "AKTVK.IS - AKTİF BANK SUKUK", "AKYHO.IS - AKDENİZ YATIRIM HOLDİNG",
    "ALARK.IS - ALARKO HOLDİNG", "ALBRK.IS - ALBARAKA TÜRK", "ALCAR.IS - ALARKO CARRIER", "ALCTL.IS - ALCATEL LUCENT",
    "ALFAS.IS - ALFA SOLAR", "ALFIN.IS - ALTERNATİF FİNANSAL", "ALGYO.IS - ALARKO GYO", "ALKA.IS - ALKİM KAĞIT",
    "ALKIM.IS - ALKİM KİMYA", "ALKLC.IS - ALTINKILIÇ GIDA", "ALNUS.IS - ALNUS YATIRIM", "ALTNY.IS - ALTINAY SAVUNMA",
    "ALVES.IS - ALVES KABLO", "ANELE.IS - ANEL ELEKTRİK", "ANGEN.IS - ANATOLIA TANI", "ANHYT.IS - ANADOLU HAYAT",
    "ANSGR.IS - ANADOLU SİGORTA", "ARASE.IS - DOĞU ARAS ENERJİ", "ARCLK.IS - ARÇELİK", "ARDYZ.IS - ARD BİLİŞİM",
    "ARENA.IS - ARENA BİLGİSAYAR", "ARMGD.IS - ARMADA GIDA", "ARSAN.IS - ARSAN TEKSTİL", "ARTMS.IS - ARTEMİS HALI",
    "ARZUM.IS - ARZUM EV ALETLERİ", "ASGYO.IS - ASCE GYO", "ASELS.IS - ASELSAN", "ASTOR.IS - ASTOR ENERJİ",
    "ASUZU.IS - ANADOLU ISUZU", "ATAGY.IS - ATA GYO", "ATAKP.IS - ATAKEY PATATES", "ATATP.IS - ATP YAZILIM",
    "ATAVK.IS - ATA VARLIK", "ATEKS.IS - AKIN TEKSTİL", "ATLAS.IS - ATLAS MENKUL", "ATLFA.IS - ATILIM FAKTORİNG",
    "ATSYH.IS - ATLANTİS YATIRIM", "AVGYO.IS - AVRASYA GYO", "AVHOL.IS - AVRUPA YATIRIM", "AVOD.IS - A.V.O.D GIDA",
    "AVPGY.IS - AVRUPAKENT GYO", "AVTUR.IS - AVRASYA PETROL", "AYCES.IS - ALTIN YUNUS", "AYDEM.IS - AYDEM ENERJİ",
    "AYEN.IS - AYEN ENERJİ", "AYES.IS - AYES ÇELİK", "AYGAZ.IS - AYGAZ", "AZTEK.IS - AZTEK TEKNOLOJİ",
    "A1CAP.IS - A1 CAPITAL", "BAGFS.IS - BAGFAŞ", "BAHKM.IS - BAHADIR KİMYA", "BAKAB.IS - BAK AMBALAJ",
    "BALAT.IS - BALATACILAR", "BALSU.IS - BALSU GIDA", "BANVT.IS - BANVİT", "BARMA.IS - BAREM AMBALAJ",
    "BASCM.IS - BAŞTAŞ ÇİMENTO", "BASGZ.IS - BAŞKENT DOĞALGAZ", "BAYRK.IS - BAYRAK EBT", "BEGYO.IS - BATI EGE GYO",
    "BERA.IS - BERA HOLDİNG", "BESLR.IS - BESLER GIDA", "BEYAZ.IS - BEYAZ FİLO", "BFREN.IS - BOSCH FREN",
    "BIENY.IS - BİEN YAPI", "BIGCH.IS - BIG CHEFS", "BIGTK.IS - BIG MEDYA", "BIMAS.IS - BİM MAĞAZALAR",
    "BINBN.IS - BİN ULAŞIM", "BIOEN.IS - BİOTREND ENERJİ", "BIZIM.IS - BİZİM TOPTAN", "BJKAS.IS - BEŞİKTAŞ FUTBOL",
    "BLCYT.IS - BİLİCİ YATIRIM", "BLKOM.IS - BİLKOM", "BLUME.IS - BLUME METAL", "BMSTL.IS - BMS BİRLEŞİK METAL",
    "BMSCH.IS - BMS ÇELİK HASIR", "BNTAS.IS - BANTAŞ", "BOBET.IS - BOĞAZİÇİ BETON", "BORLS.IS - BORLEASE OTOMOTİV",
    "BORSK.IS - BOR ŞEKER", "BOSSA.IS - BOSSA", "BRISA.IS - BRİSA", "BRKO.IS - BİRKO", "BRKSN.IS - BERKOSAN",
    "BRKVY.IS - BİRİKİM VARLIK", "BRLSM.IS - BİRLEŞİM MÜHENDİSLİK", "BRMEN.IS - BİRLİK MENSUCAT", "BRSAN.IS - BORUSAN BORU",
    "BRYAT.IS - BORUSAN YATIRIM", "BSOKE.IS - BATISÖKE ÇİMENTO", "BSRFK.IS - BAŞER FAKTORİNG", "BTCIM.IS - BATIÇİM",
    "BUCIM.IS - BURSA ÇİMENTO", "BURCE.IS - BURÇELİK", "BURVA.IS - BURÇELİK VANA", "BVSAN.IS - BÜLBÜLOĞLU VİNÇ",
    "BYDNR.IS - BAYDÖNER", "CANTE.IS - ÇAN2 TERMİK", "CASA.IS - CASA EMTİA", "CATES.IS - ÇATES ELEKTRİK",
    "CCOLA.IS - COCA COLA İÇECEK", "CELHA.IS - ÇELİK HALAT", "CEMAS.IS - ÇEMAŞ DÖKÜM", "CEMTS.IS - ÇEMTAŞ",
    "CEMZY.IS - CEM ZEYTİN", "CEOEM.IS - CEO EVENT", "CIMSA.IS - ÇİMSA", "CLEBI.IS - ÇELEBİ HAVA SERVİSİ",
    "CLKMT.IS - ÇELİK MOTOR", "CMBTN.IS - ÇİMBETON", "CMENT.IS - ÇİMENTAŞ", "CONSE.IS - CONSUS ENERJİ",
    "COSMO.IS - COSMOS YATIRIM", "CRDFA.IS - CREDITWEST FAKTORİNG", "CRFSA.IS - CARREFOURSA", "CUSAN.IS - ÇUHADAROĞLU",
    "CVKMD.IS - CVK MADEN", "CWENE.IS - CW ENERJİ", "DAGI.IS - DAGİ GİYİM", "DAPGM.IS - DAP GAYRİMENKUL",
    "DARDL.IS - DARDANEL", "DCTTR.IS - DCT TRADING", "DENGE.IS - DENGE YATIRIM", "DENFA.IS - DENİZ FAKTORİNG",
    "DERHL.IS - DERLÜKS YATIRIM", "DERIM.IS - DERİMOD", "DESA.IS - DESA DERİ", "DESPC.IS - DESPEC BİLGİSAYAR",
    "DEVA.IS - DEVA HOLDİNG", "DGATE.IS - DATAGATE", "DGGYO.IS - DOĞUŞ GYO", "DGNMO.IS - DOĞANLAR MOBİLYA",
    "DITAS.IS - DİTAŞ DOĞAN", "DMSAS.IS - DEMİSAŞ", "DNISI.IS - DİNAMİK ISI", "DOAS.IS - DOĞUŞ OTOMOTİV",
    "DOCO.IS - DO & CO", "DOFER.IS - DOFER YAPI", "DOGUB.IS - DOĞUSAN BORU", "DOHOL.IS - DOĞAN HOLDİNG",
    "DOKTA.IS - DÖKTAŞ", "DMRGD.IS - DMR UNLU MAMULLER", "DNFIN.IS - DENİZ FİNANSAL", "DOGVY.IS - DOĞRU VARLIK",
    "DURDO.IS - DURAN DOĞAN BASIM", "DURKN.IS - DURUKAN ŞEKERLEME", "DYOBY.IS - DYO BOYA", "DZGYO.IS - DENİZ GYO",
    "EBEBK.IS - EBEBEK", "ECILC.IS - ECZACIBAŞI İLAÇ", "ECOGR.IS - ECOGREEN ENERJİ", "ECZYT.IS - ECZACIBAŞI YATIRIM",
    "EDATA.IS - E-DATA TEKNOLOJİ", "EDIP.IS - EDİP GAYRİMENKUL", "EFOR.IS - EFOR ÇAY", "EGEEN.IS - EGE ENDÜSTRİ",
    "EGEGY.IS - EGEYAPI GYO", "EGGUB.IS - EGE GÜBRE", "EGPRO.IS - EGE PROFİL", "EGSER.IS - EGE SERAMİK",
    "EKGYO.IS - EMLAK KONUT GYO", "EKOFA.IS - EKO FAKTORİNG", "EKOS.IS - EKOS TEKNOLOJİ", "EKOVR.IS - EKOVAR ÇEVRE",
    "EKSUN.IS - EKSUN GIDA", "ELITE.IS - ELİTE NATUREL", "EMKEL.IS - EMEK ELEKTRİK", "EMNIS.IS - EMİNİŞ AMBALAJ",
    "ENERY.IS - ENERYA ENERJİ", "ENJSA.IS - ENERJİSA", "ENKAI.IS - ENKA İNŞAAT", "ENSRI.IS - ENSARİ DERİ",
    "ENTRA.IS - IC ENTERRA", "EPLAS.IS - EGEPLAST", "ERBOS.IS - ERBOSAN", "ERCB.IS - ERCİYAS ÇELİK BORU",
    "EREGL.IS - EREĞLİ DEMİR ÇELİK", "ERSU.IS - ERSU GIDA", "ESCAR.IS - ESCAR FİLO", "ESCOM.IS - ESCORT TEKNOLOJİ",
    "ESEN.IS - ESENBOĞA ELEKTRİK", "ETILR.IS - ETİLER GIDA", "ETYAT.IS - EURO TREND", "EUHOL.IS - EURO YATIRIM",
    "EUKYO.IS - EURO KAPİTAL", "EUPWR.IS - EUROPOWER ENERJİ", "EUREN.IS - EUROPEN ENDÜSTRİ", "EUYO.IS - EURO YATIRIM ORT",
    "EYGYO.IS - EYG GYO", "FADE.IS - FADE GIDA", "FENER.IS - FENERBAHÇE", "FLAP.IS - FLAP KONGRE",
    "FMIZP.IS - FEDERAL MOGUL", "FONET.IS - FONET BİLGİ TEK.", "FORMT.IS - FORMET METAL", "FORTE.IS - FORTE BİLGİ",
    "FRIGO.IS - FRİGO-PAK GIDA", "FROTO.IS - FORD OTOSAN", "FZLGY.IS - FUZUL GYO", "GARAN.IS - GARANTİ BBVA",
    "GARFA.IS - GARANTİ FAKTORİNG", "GEDIK.IS - GEDİK YATIRIM", "GEDZA.IS - GEDİZ AMBALAJ", "GENIL.IS - GEN İLAÇ",
    "GENTS.IS - GENTAŞ", "GEREL.IS - GERSAN ELEKTRİK", "GESAN.IS - GİRİŞİM ELEKTRİK", "GIPTA.IS - GIPTA OFİS",
    "GLBMD.IS - GLOBAL MENKUL", "GLCVY.IS - GELECEK VARLIK", "GLRYH.IS - GÜLER YATIRIM", "GLYHO.IS - GLOBAL YATIRIM HOLDİNG",
    "GMTAS.IS - GİMAT MAĞAZACILIK", "GOKNR.IS - GÖKNUR GIDA", "GOLTS.IS - GÖLTAŞ ÇİMENTO", "GOODY.IS - GOODYEAR",
    "GOZDE.IS - GÖZDE GİRİŞİM", "GRNYO.IS - GARANTİ YATIRIM ORT", "GRSEL.IS - GÜR-SEL TURİZM", "GRTHO.IS - GRAINTURK",
    "GSDDE.IS - GSD DENİZCİLİK", "GSDHO.IS - GSD HOLDİNG", "GSRAY.IS - GALATASARAY", "GUBRF.IS - GÜBRE FABRİKALARI",
    "GUNDG.IS - GÜNDOĞDU GIDA", "GWIND.IS - GALATA WIND", "GZNMI.IS - GEZİNOMİ", "HALKB.IS - HALKBANK",
    "HALKF.IS - HALK FİNANSAL", "HATEK.IS - HATEKS", "HATSN.IS - HAT-SAN GEMİ", "HDFGS.IS - HEDEF GİRİŞİM",
    "HEDEF.IS - HEDEF HOLDİNG", "HEKTS.IS - HEKTAŞ", "HKTM.IS - HİDROPAR", "HLGYO.IS - HALK GYO",
    "HOROZ.IS - HOROZ LOJİSTİK", "HRKET.IS - HAREKET PROJE", "HTTBT.IS - HİTİT BİLGİSAYAR", "HUBVC.IS - HUB GİRİŞİM",
    "HUNER.IS - HUN YENİLENEBİLİR", "HURGZ.IS - HÜRRİYET GAZETECİLİK", "HUZFA.IS - HUZUR FAKTORİNG",
    "ICBCT.IS - ICBC TURKEY", "ICUGS.IS - ICU GİRİŞİM", "IEYHO.IS - IŞIKLAR ENERJİ", "IHAAS.IS - İHLAS HABER AJANSI",
    "IHEVA.IS - İHLAS EV ALETLERİ", "IHGZT.IS - İHLAS GAZETECİLİK", "IHLAS.IS - İHLAS HOLDİNG", "IHLGM.IS - İHLAS GAYRİMENKUL",
    "IHYAY.IS - İHLAS YAYIN", "IMASM.IS - İMAŞ MAKİNA", "INALR.IS - İNALLAR OTOMOTİV", "INDES.IS - İNDEKS BİLGİSAYAR",
    "INFO.IS - İNFO YATIRIM", "INGRM.IS - INGRAM MICRO", "INTEM.IS - İNTEMA", "INVEO.IS - INVEO YATIRIM",
    "INVES.IS - INVESTCO HOLDİNG", "IPEKE.IS - İPEK DOĞAL ENERJİ", "ISBIR.IS - İŞBİR HOLDİNG", "ISCTR.IS - İŞ BANKASI (C)",
    "ISDMR.IS - İSKENDERUN DEMİR ÇELİK", "ISFAK.IS - İŞ FAKTORİNG", "ISFIN.IS - İŞ FİNANSAL", "ISGSY.IS - İŞ GİRİŞİM",
    "ISGYO.IS - İŞ GYO", "ISKPL.IS - IŞIK PLASTİK", "ISMEN.IS - İŞ YATIRIM", "ISSEN.IS - İŞBİR SENTETİK",
    "ISTFK.IS - İSTANBUL FAKTORİNG", "ISYAT.IS - İŞ YATIRIM ORT", "IZENR.IS - İZDEMİR ENERJİ", "IZFAS.IS - İZMİR FIRÇA",
    "IZINV.IS - İZ YATIRIM", "IZMDC.IS - İZMİR DEMİR ÇELİK", "JANTS.IS - JANTSA", "KAPLM.IS - KAPLAMİN",
    "KAREL.IS - KAREL ELEKTRONİK", "KARSN.IS - KARSAN OTOMOTİV", "KARTN.IS - KARTONSAN", "KARYE.IS - KARTAL YENİLENEBİLİR",
    "KATMR.IS - KATMERCİLER", "KAYSE.IS - KAYSERİ ŞEKER", "KBORU.IS - KUZEY BORU", "KCAER.IS - KOCAER ÇELİK",
    "KCHOL.IS - KOÇ HOLDİNG", "KENT.IS - KENT GIDA", "KERVN.IS - KERVANSARAY", "KERVT.IS - KEREVİTAŞ", "KFEIN.IS - KAFEİN YAZILIM",
    "KGYO.IS - KORAY GYO", "KIMMR.IS - ERSAN ALIŞVERİŞ", "KLGYO.IS - KİLER GYO", "KLKIM.IS - KALEKİM",
    "KLMSN.IS - KLİMASAN", "KLSER.IS - KALESERAMİK", "KMPUR.IS - KİMTEKS POLİÜRETAN", "KNFRT.IS - KONFRUT GIDA",
    "KNTFA.IS - KENT FİNANS", "KONKA.IS - KONYA KAĞIT", "KONTR.IS - KONTROLMATİK",
    "KONYA.IS - KONYA ÇİMENTO", "KOPOL.IS - KOZA POLYESTER", "KORDS.IS - KORDSA", "KOZAA.IS - KOZA MADENCİLİK",
    "KOZAL.IS - KOZA ALTIN", "KRDMA.IS - KARDEMİR (A)", "KRDMB.IS - KARDEMİR (B)", "KRDMD.IS - KARDEMİR (D)",
    "KRGYO.IS - KÖRFEZ GYO", "KRONT.IS - KRON TEKNOLOJİ", "KRPLS.IS - KOROPLAST", "KRSTL.IS - KRİSTAL KOLA",
    "KRTEK.IS - KARSU TEKSTİL", "KRVGD.IS - KERVAN GIDA", "KSTUR.IS - KUŞTUR", "KTLEV.IS - KATILIMEVİM",
    "KTSKR.IS - KÜTAHYA ŞEKER", "KUTPO.IS - KÜTAHYA PORSELEN", "KUVVA.IS - KUVVA GIDA", "KUYAS.IS - KUYAŞ YATIRIM",
    "KZBGY.IS - KIZILBÜK GYO", "KZGYO.IS - KUZU GYO", "LIDER.IS - LDR TURİZM", "LIDFA.IS - LİDER FAKTORİNG",
    "LILAK.IS - LİLA KAĞIT", "LINK.IS - LİNK BİLGİSAYAR", "LKMNH.IS - LOKMAN HEKİM", "LMKDC.IS - LİMAK ÇİMENTO",
    "LOGO.IS - LOGO YAZILIM", "LRSHO.IS - LORAS HOLDİNG", "LUKSK.IS - LÜKS KADİFE", "LYDHO.IS - LYDİA HOLDİNG",
    "MAALT.IS - MARMARİS ALTINYUNUS", "MACKO.IS - MACKOLİK", "MAGEN.IS - MARGÜN ENERJİ", "MAKIM.IS - MAKİM MAKİNA",
    "MAKTK.IS - MAKİNA TAKIM", "MANAS.IS - MANAS ENERJİ", "MARBL.IS - TUREKS TURUNÇ MADENCİLİK", "MARKA.IS - MARKA YATIRIM",
    "MARTI.IS - MARTI OTEL", "MAVI.IS - MAVİ GİYİM", "MEDTR.IS - MEDİTERA TIBBİ", "MEGMT.IS - MEGA METAL",
    "MEGAP.IS - MEGA POLİETİLEN", "MEKAG.IS - MEKA BETON", "MGROS.IS - MİGROS", "MHRGY.IS - MHR GYO",
    "MIATK.IS - MİA TEKNOLOJİ", "MMCAS.IS - MMC SANAYİ", "MNDRS.IS - MENDERES TEKSTİL", "MNDTR.IS - MONDİ TURKEY",
    "MNGFA.IS - MNG FAKTORİNG", "MOBTL.IS - MOBİLTEL", "MOGAN.IS - MOGAN ENERJİ", "MPARK.IS - MLP SAĞLIK",
    "MRGYO.IS - MARTI GYO", "MRSHL.IS - MARSHALL", "MSGYO.IS - MİSTRAL GYO", "MTRKS.IS - MATRİKS BİLGİ",
    "MTRYO.IS - METRO YATIRIM ORT", "MZHLD.IS - MAZHAR ZORLU", "NATEN.IS - NATUREL ENERJİ", "NETAS.IS - NETAŞ",
    "NIBAS.IS - NİĞBAŞ", "NTGAZ.IS - NATURELGAZ", "NTHOL.IS - NET HOLDİNG", "NUHCM.IS - NUH ÇİMENTO",
    "NUGYO.IS - NUROL GYO", "OBAMS.IS - OBA MAKARNACILIK", "OBASE.IS - OBASE BİLGİSAYAR", "ODAS.IS - ODAŞ ELEKTRİK",
    "ODINE.IS - ODİNE SOLUTİONS", "OFSYM.IS - OFİS YEM", "ONCSM.IS - ONCOSEM", "ONRYT.IS - ONUR YÜKSEK TEKNOLOJİ",
    "OPET.IS - OPET", "ORCAY.IS - ORÇAY", "ORGE.IS - ORGE ENERJİ", "ORMA.IS - ORMA ORMAN", "OSMEN.IS - OSMANLI YATIRIM",
    "OSTIM.IS - OSTİM", "OTKAR.IS - OTOKAR", "OTTO.IS - OTTO HOLDİNG", "OYAKC.IS - OYAK ÇİMENTO",
    "OYAYO.IS - OYAK YATIRIM ORT", "OYLUM.IS - OYLUM SINAİ", "OYYAT.IS - OYAK YATIRIM", "OZATD.IS - ÖZATA DENİZCİLİK",
    "OZGYO.IS - ÖZDERİCİ GYO", "OZKGY.IS - ÖZAK GYO", "OZRDN.IS - ÖZERDEN AMBALAJ", "OZSUB.IS - ÖZSU BALIK",
    "OZYSR.IS - ÖZYAŞAR TEL", "PAGYO.IS - PANORA GYO", "PAMEL.IS - PAMEL YENİLENEBİLİR", "PAPIL.IS - PAPİLON SAVUNMA",
    "PARSN.IS - PARSAN", "PASEU.IS - PASİFİK EURASIA", "PATEK.IS - PASİFİK TEKNOLOJİ", "PCILT.IS - PC İLETİŞİM",
    "PEKGY.IS - PEKER GYO", "PENGD.IS - PENGUEN GIDA", "PENTA.IS - PENTA TEKNOLOJİ", "PETKM.IS - PETKİM",
    "PETUN.IS - PINAR ET", "PGSUS.IS - PEGASUS", "PINSU.IS - PINAR SU", "PKART.IS - PLASTİKKART", "PKENT.IS - PETROKENT",
    "PLTUR.IS - PLATFORM TURİZM", "PNLSN.IS - PANELSAN", "PNSUT.IS - PINAR SÜT", "POLHO.IS - POLİSAN HOLDİNG",
    "POLTK.IS - POLİTEKNİK METAL", "PRDGS.IS - PARDUS GİRİŞİM", "PRKAB.IS - TÜRK PRYSMİAN", "PRKME.IS - PARK ELEKTRİK",
    "PRZMA.IS - PRİZMA PRES", "PSDTC.IS - PERGAMON DIŞ TİC.", "PSGYO.IS - PASİFİK GYO", "QUAGR.IS - QUA GRANITE",
    "RALYH.IS - RAL YATIRIM", "RAYSG.IS - RAY SİGORTA", "REEDR.IS - REEDER TEKNOLOJİ", "RGYAS.IS - RÖNESANS GYO",
    "RNPOL.IS - RAINBOW POLİKARBONAT", "RODRG.IS - RODRIGO TEKSTİL", "ROYAL.IS - ROYAL HALI", "RTALB.IS - RTA LABORATUVARLARI",
    "RUBNS.IS - RUBENİS TEKSTİL", "RUZYE.IS - RUZY MADENCİLİK", "RYGYO.IS - REYSAŞ GYO", "RYSAS.IS - REYSAŞ LOJİSTİK",
    "SAFKR.IS - SAFKAR", "SAHOL.IS - SABANCI HOLDİNG", "SAMAT.IS - SARAY MATBAACILIK", "SANEL.IS - SAN-EL MÜHENDİSLİK",
    "SANFM.IS - SANİFOAM", "SANKO.IS - SANKO PAZARLAMA", "SARKY.IS - SARKUYSAN", "SARTN.IS - SARTEN AMBALAJ",
    "SASA.IS - SASA POLYESTER", "SAYAS.IS - SAY YENİLENEBİLİR", "SDTTR.IS - SDT UZAY", "SEGMN.IS - SEĞMEN KARDEŞLER",
    "SEGYO.IS - ŞEKER GYO", "SEKFK.IS - ŞEKER FİNANSAL", "SEKUR.IS - SEKURO PLASTİK", "SELEC.IS - SELÇUK ECZA",
    "SELVA.IS - SELVA GIDA", "SEYKM.IS - SEYİTLER KİMYA", "SILVR.IS - SİLVERLİNE", "SISE.IS - ŞİŞECAM",
    "SKBNK.IS - ŞEKERBANK", "SKTAS.IS - SÖKTAŞ", "SKYLP.IS - SKYALP FİNANSAL", "SKYMD.IS - ŞEKER YATIRIM",
    "SMART.IS - SMARTİKS YAZILIM", "SMRFA.IS - SÜMER FAKTORİNG", "SMRTG.IS - SMART GÜNEŞ", "SNGYO.IS - SİNPAŞ GYO",
    "SNICA.IS - SANİCA ISI", "SNKRN.IS - SENKRON GÜVENLİK", "SNPAM.IS - SÖNMEZ PAMUKLU", "SODSN.IS - SODAŞ SODYUM",
    "SOKE.IS - SÖKE DEĞİRMENCİLİK", "SOKM.IS - ŞOK MARKETLER", "SONME.IS - SÖNMEZ FİLAMENT", "SRVGY.IS - SERVET GYO",
    "SUMAS.IS - SUMAŞ SUNİ TAHTA", "SUNTK.IS - SUN TEKSTİL", "SURGY.IS - SUR TATİL EVLERİ GYO", "SUWEN.IS - SUWEN TEKSTİL",
    "TABGD.IS - TAB GIDA", "TARKM.IS - TARKİM BİTKİ", "TATEN.IS - TATLIPINAR ENERJİ", "TATGD.IS - TAT GIDA",
    "TAVHL.IS - TAV HAVALİMANLARI", "TBORG.IS - TÜRK TUBORG", "TCELL.IS - TURKCELL", "TDGYO.IS - TREND GYO",
    "TEBFA.IS - TEB FAKTORİNG", "TEKTU.IS - TEK-ART İNŞAAT", "TERA.IS - TERA YATIRIM", "TEZOL.IS - EUROPAP TEZOL",
    "TGSAS.IS - TGS DIŞ TİCARET", "THYAO.IS - TÜRK HAVA YOLLARI", "TIMUR.IS - TİMUR GAYRİMENKUL", "TKFEN.IS - TEKFEN HOLDİNG",
    "TKNSA.IS - TEKNOSA", "TLMAN.IS - TRABZON LİMAN", "TMPOL.IS - TEMAPOL POLİMER", "TMSN.IS - TÜMOSAN",
    "TOASO.IS - TOFAŞ OTO", "TRCAS.IS - TURCAS PETROL", "TRGYO.IS - TORUNLAR GYO", "TRILC.IS - TURK İLAÇ",
    "TSGYO.IS - TSKB GYO", "TSKB.IS - TSKB", "TSPOR.IS - TRABZONSPOR", "TTKOM.IS - TÜRK TELEKOM",
    "TTRAK.IS - TÜRK TRAKTÖR", "TUCLK.IS - TUĞÇELİK", "TUKAS.IS - TUKAŞ", "TUPRS.IS - TÜPRAŞ", "TUREX.IS - TUREKS TURİZM",
    "TURGG.IS - TÜRKER PROJE", "TURSG.IS - TÜRKİYE SİGORTA", "UFUK.IS - UFUK YATIRIM", "ULAS.IS - ULAŞLAR TURİZM",
    "ULUFA.IS - ULUSAL FAKTORİNG", "ULKER.IS - ÜLKER BİSKÜVİ", "ULUSE.IS - ULUSOY ELEKTRİK", "ULUUN.IS - ULUSOY UN",
    "UMPAS.IS - UMPAŞ HOLDİNG", "UNLU.IS - ÜNLÜ YATIRIM", "USAK.IS - UŞAK SERAMİK", "VAKBN.IS - VAKIFBANK",
    "VAKFA.IS - VAKIF FAKTORİNG", "VAKFN.IS - VAKIF FİNANSAL", "VAKKO.IS - VAKKO", "VANGD.IS - VANET GIDA",
    "VBTYZ.IS - VBT YAZILIM", "VERUS.IS - VERUSA HOLDİNG", "VERTU.IS - VERUSATURK", "VESBE.IS - VESTEL BEYAZ EŞYA",
    "VESTL.IS - VESTEL", "VKFYO.IS - VAKIF MENKUL", "VKGYO.IS - VAKIF GYO", "VKING.IS - VİKİNG KAĞIT",
    "VRGYO.IS - VERA KONSEPT GYO", "YAPRK.IS - YAPRAK SÜT", "YATAS.IS - YATAŞ", "YAYLA.IS - YAYLA ENERJİ",
    "YBTAS.IS - YİBİTAŞ", "YEOTK.IS - YEO TEKNOLOJİ", "YESIL.IS - YEŞİL YATIRIM", "YGGYO.IS - YENİ GİMAT GYO",
    "YGYO.IS - YEŞİL GYO", "YIGIT.IS - YİĞİT AKÜ", "YKBNK.IS - YAPI KREDİ BANKASI", "YKFKT.IS - YAPI KREDİ FAKTORİNG",
    "YKSLN.IS - YÜKSELEN ÇELİK", "YONGA.IS - YONGA MOBİLYA", "YUNSA.IS - YÜNSA", "YYAPI.IS - YEŞİL YAPI",
    "YYLGD.IS - YAYLA AGRO GIDA", "ZEDUR.IS - ZEDUR ENERJİ", "ZOREN.IS - ZORLU ENERJİ", "ZRGYO.IS - ZİRAAT GYO"
]

US_STOCKS = ["AAPL - Apple", "TSLA - Tesla", "MSFT - Microsoft", "NVDA - NVIDIA", "AMZN - Amazon", "GOOGL - Google", "META - Meta", "BTC-USD - Bitcoin", "ETH-USD - Ethereum"]
ALL_STOCKS = ["🔍 MANUEL ARAMA"] + sorted(BIST_STOCKS + US_STOCKS)

# --- FONKSİYONLAR ---
def translate_to_turkish(text):
    try:
        if not text or len(text) < 5: return "Bilgi yok."
        if len(text) > 4900: text = text[:4900]
        return GoogleTranslator(source='auto', target='tr').translate(text)
    except: return text

def format_number(num, prefix="", suffix=""):
    if num is None: return "-"
    if num >= 1e9: return f"{prefix}{num/1e9:.2f} Mrd{suffix}"
    if num >= 1e6: return f"{prefix}{num/1e6:.2f} Mn{suffix}"
    return f"{prefix}{num:,.2f}{suffix}"

def fmt_pct(num):
    if num is None: return "-"
    return f"%{num*100:.2f}"

def get_val(info, key):
    return info.get(key, None)

def technical_analysis(hist):
    close = hist['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    
    score = 0
    if rsi.iloc[-1] < 30: score += 1
    elif rsi.iloc[-1] > 70: score -= 1
    if macd.iloc[-1] > signal.iloc[-1]: score += 1
    else: score -= 1
    if close.iloc[-1] > sma50.iloc[-1]: score += 1
    
    overall = "AL 🟢" if score >= 1 else "SAT 🔴" if score <= -1 else "NÖTR ⚪"
    return {"RSI": f"{rsi.iloc[-1]:.2f}", "MACD": f"{macd.iloc[-1]:.2f}", "Overall": overall, "Score": score, "SMA50": sma50.iloc[-1], "SMA200": sma200.iloc[-1]}

def render_metric(label, value, color="black"):
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value' style='color:{color}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_fundamental_analysis(info):
    st.subheader("1. Fiyat Çarpanları")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: render_metric("F/K (P/E)", format_number(get_val(info, 'trailingPE')))
    with c2: render_metric("İleri F/K", format_number(get_val(info, 'forwardPE')))
    with c3: render_metric("PD/DD (P/B)", format_number(get_val(info, 'priceToBook')))
    with c4: render_metric("Fiyat/Satış", format_number(get_val(info, 'priceToSalesTrailing12Months')))
    with c5: render_metric("PEG Oranı", format_number(get_val(info, 'pegRatio')))
    with c6: render_metric("Piyasa Değeri", format_number(get_val(info, 'marketCap')))

    st.subheader("2. Piyasa Değeri & EV")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric("Firma Değeri (EV)", format_number(get_val(info, 'enterpriseValue')))
    with c2: render_metric("EV/EBITDA", format_number(get_val(info, 'enterpriseToEbitda')))
    with c3: render_metric("EV/Revenue", format_number(get_val(info, 'enterpriseToRevenue')))
    with c4: render_metric("Beta (Oynaklık)", format_number(get_val(info, 'beta')))

    st.subheader("3. Karlılık Oranları")
    c1, c2, c3, c4 = st.columns(4)
    gm = get_val(info, 'grossMargins')
    om = get_val(info, 'operatingMargins')
    pm = get_val(info, 'profitMargins')
    roe = get_val(info, 'returnOnEquity')
    
    with c1: render_metric("Brüt Kâr Marjı", fmt_pct(gm), "green" if gm and gm>0 else "red")
    with c2: render_metric("Faaliyet Marjı", fmt_pct(om), "green" if om and om>0 else "red")
    with c3: render_metric("Net Kâr Marjı", fmt_pct(pm), "green" if pm and pm>0 else "red")
    with c4: render_metric("ROE (Özsermaye)", fmt_pct(roe), "green" if roe and roe>0.15 else "black")

    st.subheader("4. Borçluluk & Nakit")
    c1, c2, c3, c4 = st.columns(4)
    de = get_val(info, 'debtToEquity')
    cash = get_val(info, 'totalCash')
    debt = get_val(info, 'totalDebt')
    
    with c1: render_metric("Borç/Özsermaye", format_number(de, suffix=""), "red" if de and de>100 else "green")
    with c2: render_metric("Toplam Nakit", format_number(cash))
    with c3: render_metric("Toplam Borç", format_number(debt))
    with c4: render_metric("Cari Oran", format_number(get_val(info, 'currentRatio')))

    st.subheader("5. Büyüme & Hisse Başı")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric("Gelir Büyümesi", fmt_pct(get_val(info, 'revenueGrowth')))
    with c2: render_metric("Kâr Büyümesi", fmt_pct(get_val(info, 'earningsGrowth')))
    with c3: render_metric("EPS (Hisse Başı Kâr)", format_number(get_val(info, 'trailingEps')))
    with c4: render_metric("Hisse Başı Defter", format_number(get_val(info, 'bookValue')))

    st.subheader("6. Temettü & Akış")
    c1, c2, c3, c4 = st.columns(4)
    dy = get_val(info, 'dividendYield')
    with c1: render_metric("Temettü Verimi", fmt_pct(dy), "green" if dy and dy>0.05 else "black")
    with c2: render_metric("Temettü Oranı", fmt_pct(get_val(info, 'payoutRatio')))
    with c3: render_metric("Serbest Nakit Akışı", format_number(get_val(info, 'freeCashflow')))
    with c4: render_metric("Operasyonel Nakit", format_number(get_val(info, 'operatingCashflow')))

def fetch_news_rss(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=tr-TR&gl=TR&ceid=TR:tr"
        resp = requests.get(url, timeout=10)
        root = ElementTree.fromstring(resp.content)
        return root.findall('./channel/item')[:10]
    except: return []

def fetch_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        paras = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paras[:6]])
        if len(text) > 200: return text[:1000] + "..."
        return "İçerik çekilemedi."
    except: return "Hata."

# --- MENÜ ---
with st.sidebar:
    st.title("🦁 BORSA PRIME")
    menu = st.radio("MENÜ", ["📊 HİSSE ANALİZ", "🚀 HALKA ARZLAR", "📰 HABERLER"])
    st.divider()
    st.info(f"KAP Veritabanı: {len(BIST_STOCKS)} Şirket")

# --- SAYFA 1: ANALİZ ---
if menu == "📊 HİSSE ANALİZ":
    st.title("📊 Mega Analiz Platformu")
    secim = st.selectbox("Hisse Seçiniz:", ALL_STOCKS)
    
    if "MANUEL" in secim:
        kod = st.text_input("Kod", "THYAO")
        symbol = kod.upper() + ".IS" if ".IS" not in kod.upper() and kod.upper() not in ["AAPL","TSLA"] else kod.upper()
    else:
        symbol = secim.split(" - ")[0]
        
    if st.button("ANALİZ ET 🔍", type="primary"):
        try:
            with st.spinner(f"{symbol} verileri işleniyor..."):
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1y")
                info = stock.info
            
            if not hist.empty:
                st.header(f"{info.get('longName', symbol)}")
                
                # Ana Metrikler (Özet)
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((curr-prev)/prev)*100
                color = "green" if chg > 0 else "red"
                
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<div class='metric-container'><div class='metric-label'>Son Fiyat</div><div class='metric-value' style='color:{color}'>{curr:.2f}</div><small>%{chg:.2f}</small></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-container'><div class='metric-label'>Hacim</div><div class='metric-value'>{format_number(info.get('volume'))}</div></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-container'><div class='metric-label'>Piyasa Değeri</div><div class='metric-value'>{format_number(info.get('marketCap'))}</div></div>", unsafe_allow_html=True)
                c4.markdown(f"<div class='metric-container'><div class='metric-label'>Hedef Fiyat</div><div class='metric-value'>{info.get('targetMeanPrice', '-')}</div></div>", unsafe_allow_html=True)
                
                # Sekmeler
                tab1, tab2, tab3, tab4 = st.tabs(["Genel Bakış", "Temel Analiz (Rasyolar)", "Teknik Analiz", "Şirket Profili"])
                
                with tab1:
                    # Grafik
                    st.subheader("Fiyat Grafiği")
                    hist['MA20'] = hist['Close'].rolling(20).mean()
                    hist['MA50'] = hist['Close'].rolling(50).mean()
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="Fiyat"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], line=dict(color='orange'), name="MA 20"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], line=dict(color='blue'), name="MA 50"), row=1, col=1)
                    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Hacim"), row=2, col=1)
                    fig.update_layout(height=500, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    # Temel Analiz (Rasyolar)
                    render_fundamental_analysis(info)

                with tab3:
                    # Teknik Analiz
                    tech = technical_analysis(hist)
                    st.subheader("Teknik İndikatörler")
                    st.info(f"Genel Sinyal: {tech['Overall']} (Puan: {tech['Score']}/3)")
                    st.table(pd.DataFrame({
                        "Gösterge": ["RSI (14)", "MACD", "SMA 50", "SMA 200"],
                        "Değer": [tech['RSI'], tech['MACD'], f"{tech['SMA50']:.2f}", f"{tech['SMA200']:.2f}"]
                    }))

                with tab4:
                    st.subheader("Şirket Hakkında")
                    with st.spinner("Çevriliyor..."):
                        desc = translate_to_turkish(info.get('longBusinessSummary', ''))
                    st.write(desc)
                    st.markdown(f"**Sektör:** {translate_to_turkish(info.get('sector','-'))}")
                    st.markdown(f"**Çalışan Sayısı:** {info.get('fullTimeEmployees','-')}")

            else:
                st.error("Veri bulunamadı.")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- SAYFA 2: HALKA ARZLAR ---
elif menu == "🚀 HALKA ARZLAR":
    st.title("🚀 Halka Arz Takvimi")
    ipo_list = [
        {"Kod": "KBORU", "Fiyat": "36.20", "Durum": "İşlemde"},
        {"Kod": "REEDR", "Fiyat": "9.30", "Durum": "İşlemde"},
        {"Kod": "TABGD", "Fiyat": "130.00", "Durum": "İşlemde"},
        {"Kod": "HATSN", "Fiyat": "22.60", "Durum": "İşlemde"}
    ]
    st.table(pd.DataFrame(ipo_list))
    st.subheader("Haberler")
    news = fetch_news_rss("Halka Arz SPK")
    for i in news:
        st.markdown(f"🔹 [{i.find('title').text}]({i.find('link').text})")

# --- SAYFA 3: HABERLER ---
elif menu == "📰 HABERLER":
    st.title("📰 Finans Haberleri")
    tab1, tab2 = st.tabs(["BIST", "Kripto"])
    with tab1:
        news = fetch_news_rss("Borsa İstanbul Hisse")
        for i, item in enumerate(news):
            with st.expander(f"📰 {item.find('title').text}"):
                if st.button("Oku", key=f"news_{i}"):
                    content = fetch_full_article(item.find('link').text)
                    st.write(translate_to_turkish(content))
                st.markdown(f"[Link]({item.find('link').text})")
    with tab2:
        news = fetch_news_rss("Bitcoin Kripto")
        for i in news:
            st.markdown(f"- [{i.find('title').text}]({i.find('link').text})")