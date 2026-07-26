"""
SkyTracker v9 — Fonctionnalités avancées
- Mode flexible amélioré (calendrier des prix)
- Sélecteur de classe corrigé
- Multi-destinations
- Options bagages avec logo
- Conditions (annulation, remboursement)
- Temps d'escale affiché
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import os, math, urllib.request, csv, io, re

st.set_page_config(page_title="Choisy voyages ✈", page_icon="✈️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:#0A0E1A;color:#E8EAF0}
.hero-title{font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
  background:linear-gradient(135deg,#4FC3F7 0%,#7C4DFF 50%,#E040FB 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;text-align:center;margin-bottom:.2rem}
.hero-sub{text-align:center;color:#6B7A99;font-size:.95rem;margin-bottom:1.5rem}
.search-panel{background:linear-gradient(145deg,#12182E,#1A2240);
  border:1px solid #2A3560;border-radius:20px;padding:1.75rem;margin-bottom:1.25rem}
.flight-card{background:linear-gradient(145deg,#12182E,#161E38);
  border:1px solid #2A3560;border-radius:16px;padding:1.25rem 1.5rem;
  margin-bottom:.8rem;position:relative;overflow:hidden}
.flight-card::before{content:'';position:absolute;top:0;left:0;
  width:4px;height:100%;background:linear-gradient(180deg,#4FC3F7,#7C4DFF)}
.best-price::before{background:linear-gradient(180deg,#00E676,#00BCD4)!important}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.72rem;font-weight:600;margin:2px}
.badge-green{background:rgba(0,230,118,.15);color:#00E676;border:1px solid rgba(0,230,118,.3)}
.badge-blue{background:rgba(79,195,247,.15);color:#4FC3F7;border:1px solid rgba(79,195,247,.3)}
.badge-purple{background:rgba(124,77,255,.15);color:#B39DDB;border:1px solid rgba(124,77,255,.3)}
.badge-orange{background:rgba(255,167,38,.15);color:#FFA726;border:1px solid rgba(255,167,38,.3)}
.badge-red{background:rgba(244,67,54,.15);color:#EF5350;border:1px solid rgba(244,67,54,.3)}
.badge-teal{background:rgba(0,188,140,.15);color:#00BC8C;border:1px solid rgba(0,188,140,.3)}
.badge-grey{background:rgba(107,122,153,.15);color:#6B7A99;border:1px solid #2A3560}
.price-main{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#4FC3F7}
.time-big{font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:#E8EAF0}
.time-iata{font-size:.72rem;color:#6B7A99;letter-spacing:1px}
.flight-line{border-top:1px dashed #2A3560;position:relative;margin:0 .75rem}
.flight-line::after{content:'✈';position:absolute;top:-10px;left:50%;
  transform:translateX(-50%);font-size:13px;background:#12182E;padding:0 5px;color:#4FC3F7}
.metric-card{background:linear-gradient(145deg,#12182E,#161E38);
  border:1px solid #2A3560;border-radius:12px;padding:.9rem;text-align:center}
.metric-val{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#4FC3F7}
.metric-lbl{font-size:.76rem;color:#6B7A99;margin-top:2px}
.stButton>button{background:linear-gradient(135deg,#4FC3F7,#7C4DFF)!important;
  color:white!important;border:none!important;border-radius:12px!important;
  font-family:'Syne',sans-serif!important;font-weight:600!important;width:100%!important}
.stButton>button:hover{opacity:.9!important;transform:translateY(-1px)!important}
section[data-testid="stSidebar"]{background:#0D1426!important;border-right:1px solid #2A3560!important}
.stTabs [data-baseweb="tab-list"]{background:#0D1426;border-radius:12px;padding:4px;gap:4px}
.stTabs [data-baseweb="tab"]{background:transparent!important;border-radius:8px!important;color:#6B7A99!important}
.stTabs [aria-selected="true"]{background:#1A2240!important;color:#4FC3F7!important}
.segment-box{background:#0D1426;border:1px solid #2A3560;border-radius:10px;
  padding:.75rem 1rem;margin:.4rem 0}
.layover-box{background:rgba(255,167,38,.06);border:1px solid rgba(255,167,38,.2);
  border-radius:8px;padding:.5rem 1rem;margin:.3rem 1.5rem;
  font-size:.8rem;color:#FFA726;text-align:center}
.conditions-box{background:#0D1426;border:1px solid #2A3560;border-radius:12px;padding:1rem}
.cond-row{display:flex;align-items:center;gap:10px;padding:.4rem 0;
  border-bottom:1px solid #1A2240;font-size:.85rem}
.cond-row:last-child{border-bottom:none}
.flex-calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin:1rem 0}
.cal-day{background:#12182E;border:1px solid #2A3560;border-radius:8px;
  padding:.4rem;text-align:center;cursor:pointer;transition:all .15s}
.cal-day:hover{border-color:#4FC3F7}
.cal-day.best{border-color:#00E676;background:rgba(0,230,118,.08)}
.cal-day.selected{border-color:#4FC3F7;background:rgba(79,195,247,.1)}
.setup-box{background:linear-gradient(145deg,#12182E,#1A2240);
  border:1px solid #2A3560;border-radius:20px;padding:2.5rem;
  max-width:560px;margin:2rem auto;text-align:center}
.setup-step{background:#0D1426;border:1px solid #2A3560;border-radius:12px;
  padding:1rem 1.25rem;margin-bottom:.75rem;text-align:left;
  display:flex;align-items:flex-start;gap:12px}
.step-num{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;
  color:#4FC3F7;min-width:28px}
.multi-leg{background:#0D1426;border:1px solid #2A3560;border-radius:12px;
  padding:.75rem 1rem;margin-bottom:.5rem;display:flex;align-items:center;gap:8px}
</style>
""", unsafe_allow_html=True)

# ── Client SerpApi ────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        from serpapi_client import SerpApiFlightsClient
        key = ""
        try: key = st.secrets.get("SERPAPI_KEY","")
        except Exception: pass
        if not key: key = os.getenv("SERPAPI_KEY","")
        if key and key not in ("votre_cle_serpapi_ici",""):
            return SerpApiFlightsClient(key)
    except Exception: pass
    return None

# ── Aéroports ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400)
def load_airports():
    url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    airports = []
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            content = r.read().decode("utf-8")
        for row in csv.reader(io.StringIO(content)):
            if len(row) < 9: continue
            try:
                iata = row[4].strip().strip('"')
                if not iata or len(iata)!=3 or iata==r'\N': continue
                airports.append({
                    "iata":iata,"name":row[1].strip().strip('"'),
                    "city":row[2].strip().strip('"'),
                    "country":row[3].strip().strip('"'),
                    "lat":float(row[6]),"lon":float(row[7]),
                    "label":f"{row[2].strip().strip(chr(34))} – {row[1].strip().strip(chr(34))} ({iata}), {row[3].strip().strip(chr(34))}"
                })
            except: continue
    except Exception as e:
        st.warning(f"Chargement aéroports local : {e}")
    return airports

@st.cache_data(ttl=86400)
def ap_dict():
    return {a["iata"]:a for a in load_airports()}

def iata_from_label(lbl):
    m = re.search(r'\(([A-Z]{3})\)',lbl)
    return m.group(1) if m else ""

# ── Cabine ─────────────────────────────────────────────────────────────────────
CABIN_LABELS = {"economy":"Économique","premium_economy":"Premium Éco",
                "business":"Business","first":"Première"}
CABIN_API    = {"economy":1,"premium_economy":2,"business":3,"first":4}
CABIN_ICONS  = {"economy":"🪑","premium_economy":"🛋️","business":"💺","first":"👑"}

# ── Bagages ───────────────────────────────────────────────────────────────────
BAGGAGE_INFO = {
    "economy":{
        "cabine":"1 bagage cabine (10 kg)","soute":"1 bagage soute 23 kg inclus",
        "icon":"🧳","note":"Supplément pour 2ème bagage soute : ~50-80€"
    },
    "premium_economy":{
        "cabine":"1 bagage cabine (12 kg)","soute":"2 bagages soute 23 kg inclus",
        "icon":"🧳🧳","note":"Excédent de poids accepté jusqu'à 28 kg"
    },
    "business":{
        "cabine":"2 bagages cabine (18 kg)","soute":"2 bagages soute 32 kg inclus",
        "icon":"🧳🧳🧳","note":"Service de livraison bagages disponible"
    },
    "first":{
        "cabine":"2 bagages cabine (18 kg)","soute":"3 bagages soute 32 kg inclus",
        "icon":"🧳🧳🧳🧳","note":"Service de conciergerie bagages inclus"
    },
}

# ── Conditions tarifaires ─────────────────────────────────────────────────────
CONDITIONS = {
    "economy":{
        "annulation":{"label":"Annulation","ok":False,"detail":"Non remboursable après émission","icon":"❌"},
        "modif":{"label":"Modification","ok":True,"detail":"Possible avec frais (~150-250€)","icon":"⚠️"},
        "remboursement":{"label":"Remboursement","ok":False,"detail":"Avoir ou frais de dossier uniquement","icon":"❌"},
        "upgrade":{"label":"Surclassement","ok":True,"detail":"Possible selon disponibilité","icon":"✅"},
        "miles":{"label":"Miles","ok":True,"detail":"Accumulation de miles incluse","icon":"✅"},
    },
    "premium_economy":{
        "annulation":{"label":"Annulation","ok":True,"detail":"Remboursable avec frais (~100€)","icon":"⚠️"},
        "modif":{"label":"Modification","ok":True,"detail":"Possible avec frais (~80€)","icon":"⚠️"},
        "remboursement":{"label":"Remboursement","ok":True,"detail":"Remboursement partiel (80%)","icon":"⚠️"},
        "upgrade":{"label":"Surclassement","ok":True,"detail":"Prioritaire selon disponibilité","icon":"✅"},
        "miles":{"label":"Miles","ok":True,"detail":"Accumulation 125% des miles","icon":"✅"},
    },
    "business":{
        "annulation":{"label":"Annulation","ok":True,"detail":"Remboursable sans frais jusqu'à 24h avant","icon":"✅"},
        "modif":{"label":"Modification","ok":True,"detail":"Gratuite jusqu'à 24h avant départ","icon":"✅"},
        "remboursement":{"label":"Remboursement","ok":True,"detail":"Remboursement intégral possible","icon":"✅"},
        "upgrade":{"label":"Surclassement","ok":True,"detail":"Surclassement Première si disponible","icon":"✅"},
        "miles":{"label":"Miles","ok":True,"detail":"Accumulation 200% des miles","icon":"✅"},
    },
    "first":{
        "annulation":{"label":"Annulation","ok":True,"detail":"Remboursable sans frais à tout moment","icon":"✅"},
        "modif":{"label":"Modification","ok":True,"detail":"Illimitée et gratuite","icon":"✅"},
        "remboursement":{"label":"Remboursement","ok":True,"detail":"Remboursement intégral immédiat","icon":"✅"},
        "upgrade":{"label":"Surclassement","ok":True,"detail":"Non applicable (classe maximale)","icon":"—"},
        "miles":{"label":"Miles","ok":True,"detail":"Accumulation 300% des miles","icon":"✅"},
    },
}

# ── Agrégateurs ───────────────────────────────────────────────────────────────
def agg_urls(iata_o, iata_d, dep, ret, pax):
    d = dep.strftime("%Y-%m-%d") if hasattr(dep,"strftime") else str(dep)
    r = ret.strftime("%Y-%m-%d") if ret and hasattr(ret,"strftime") else (str(ret) if ret else None)
    yd=d.replace("-",""); yr=r.replace("-","") if r else ""
    return {
        "🔍 Google Flights":f"https://www.google.com/travel/flights?q=Vols+{iata_o}+vers+{iata_d}&hl=fr&curr=EUR",
        "✈ Kayak":f"https://www.kayak.fr/flights/{iata_o}-{iata_d}/{d}{'/' + r if r else ''}/{pax}adults?sort=price_a",
        "🌐 Skyscanner":f"https://www.skyscanner.fr/transport/vols/{iata_o.lower()}/{iata_d.lower()}/{yd}{'/' + yr if yr else ''}/?adultsv2={pax}&rtn={'1' if r else '0'}",
        "💰 Momondo":f"https://www.momondo.fr/flight-search/{iata_o}-{iata_d}/{d}{'/' + r if r else ''}?adults={pax}",
    }

# ── Formatage ─────────────────────────────────────────────────────────────────
def fmt_dur(m):
    if not m: return "—"
    h,mn=divmod(int(m),60)
    return f"{h}h{mn:02d}"

def fmt_prix(p):
    return f"{float(p):,.0f} €".replace(","," ")

def fmt_date(s):
    try:
        return datetime.strptime(str(s)[:16],"%Y-%m-%d %H:%M").strftime("%d %b %H:%M")
    except: return str(s)[:16]

# ── Render vol ────────────────────────────────────────────────────────────────
def render_vol(v, is_best, iata_o, iata_d, dep, ret, pax, cabin):
    from serpapi_client import get_booking_url
    try:
        dep_dt=datetime.strptime(str(v["date_depart"])[:16],"%Y-%m-%d %H:%M")
        arr_dt=datetime.strptime(str(v["date_arrivee"])[:16],"%Y-%m-%d %H:%M")
    except: dep_dt=arr_dt=datetime.now()

    days_diff=(arr_dt.date()-dep_dt.date()).days
    nb_esc=int(v.get("escales",0))
    esc_v=str(v.get("escale_villes","") or "")
    segments=v.get("segments",[])

    if nb_esc==0: esc_txt="✅ Direct"; esc_cls="badge-green"
    elif nb_esc==1: esc_txt=f"1 escale{' via '+esc_v if esc_v else ''}"; esc_cls="badge-orange"
    else: esc_txt=f"{nb_esc} escales{' via '+esc_v if esc_v else ''}"; esc_cls="badge-orange"

    places=int(v.get("places_disponibles",9))
    places_b=f'<span class="badge badge-orange">⚡ {places} places</span>' if places<10 else ""
    best_b='<span class="badge badge-green">🏷 Meilleur prix</span>' if is_best else ""

    code=v.get("airline_code","??")
    name=v.get("airline_name",code)
    color=v.get("airline_color","#4FC3F7")
    fnum=v.get("flight_number","")
    prix=float(v.get("prix",0))
    pbiz=float(v.get("prix_business",prix*3))

    co2=v.get("carbon_emissions",{})
    co2_b=""
    if co2 and isinstance(co2,dict) and co2.get("difference_percent"):
        diff=co2["difference_percent"]
        co2_b=f'<span class="badge badge-teal">🌿 CO₂ {"+" if diff>0 else ""}{diff}%</span>'

    bag=BAGGAGE_INFO.get(cabin,BAGGAGE_INFO["economy"])
    dep_s=dep.strftime("%Y-%m-%d") if hasattr(dep,"strftime") else str(dep)
    ret_s=ret.strftime("%Y-%m-%d") if ret and hasattr(ret,"strftime") else (str(ret) if ret else None)
    url=v.get("deep_link") or get_booking_url(code,iata_o,iata_d,dep_s,ret_s,pax)

    st.markdown(f"""
    <div class="flight-card {'best-price' if is_best else ''}">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
        <div style="min-width:130px">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
            <div style="width:10px;height:10px;border-radius:50%;background:{color}"></div>
            <span style="font-size:.78rem;color:#6B7A99">{code}</span>
          </div>
          <div style="font-size:.93rem;font-weight:600;color:#E8EAF0">{name}</div>
          <div style="font-size:.73rem;color:#4B5A7A;margin-top:1px">{fnum}</div>
          <div style="margin-top:5px;display:flex;gap:3px;flex-wrap:wrap">
            <span class="badge badge-green" style="font-size:.68rem">✅ Prix réel</span>
            {co2_b}
          </div>
        </div>
        <div style="text-align:center;min-width:75px">
          <div class="time-big">{dep_dt.strftime('%H:%M')}</div>
          <div class="time-iata">{v.get('iata_o',iata_o)}</div>
          <div style="font-size:.7rem;color:#4B5A7A">{dep_dt.strftime('%d %b')}</div>
        </div>
        <div style="flex:1;min-width:110px;padding:0 .75rem">
          <div style="color:#4B5A7A;font-size:.78rem;text-align:center">{fmt_dur(v.get('duree_minutes',0))}</div>
          <div class="flight-line"></div>
          <div style="text-align:center;margin-top:5px">
            <span class="badge {esc_cls}">{esc_txt}</span>
          </div>
        </div>
        <div style="text-align:center;min-width:75px">
          <div class="time-big">{arr_dt.strftime('%H:%M')}{'+'+str(days_diff) if days_diff>0 else ''}</div>
          <div class="time-iata">{v.get('iata_d',iata_d)}</div>
          <div style="font-size:.7rem;color:#4B5A7A">{arr_dt.strftime('%d %b')}</div>
        </div>
        <div style="text-align:right;min-width:130px">
          <div class="price-main">{fmt_prix(prix)}</div>
          <div style="font-size:.78rem;color:#6B7A99">{fmt_prix(prix/pax)}/pers · {CABIN_ICONS.get(cabin,'')} {CABIN_LABELS.get(cabin,'')}</div>
          <div style="margin-top:5px">{best_b} {places_b}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"📋 {fnum} — Détails complets"):
        t1,t2,t3,t4 = st.tabs(["✈️ Itinéraire","🧳 Bagages","📋 Conditions","💳 Réserver"])

        with t1:
            # Segments détaillés avec temps d'escale
            if segments:
                for i,seg in enumerate(segments):
                    seg_dep=seg.get("departure_airport",{})
                    seg_arr=seg.get("arrival_airport",{})
                    seg_dep_t=seg.get("dep_time","")
                    seg_arr_t=seg.get("arr_time","")
                    seg_dur=seg.get("duration",0)
                    seg_airline=seg.get("airline","")
                    seg_num=seg.get("flight_number","")
                    aircraft=seg.get("aircraft","")
                    st.markdown(f"""
                    <div class="segment-box">
                      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                        <div>
                          <span style="font-size:.78rem;color:#6B7A99">{seg_airline} · {seg_num}</span>
                          {f'<span class="badge badge-grey">{aircraft}</span>' if aircraft else ''}
                        </div>
                        <span class="badge badge-blue">⏱ {fmt_dur(seg_dur)}</span>
                      </div>
                      <div style="display:flex;align-items:center;gap:12px;margin-top:8px">
                        <div style="text-align:center">
                          <div style="font-size:1.15rem;font-weight:700;color:#E8EAF0">{seg_dep_t}</div>
                          <div style="font-size:.72rem;color:#6B7A99">{seg_dep.get('id','')} · {seg_dep.get('name','')}</div>
                        </div>
                        <div style="flex:1;border-top:1px dashed #2A3560;position:relative">
                          <span style="position:absolute;top:-9px;left:50%;transform:translateX(-50%);
                            background:#0D1426;padding:0 5px;font-size:12px">✈</span>
                        </div>
                        <div style="text-align:center">
                          <div style="font-size:1.15rem;font-weight:700;color:#E8EAF0">{seg_arr_t}</div>
                          <div style="font-size:.72rem;color:#6B7A99">{seg_arr.get('id','')} · {seg_arr.get('name','')}</div>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Temps d'escale entre segments
                    if i < len(segments)-1:
                        layover=v.get("layovers",[])
                        if i < len(layover):
                            lay=layover[i]
                            lay_dur=lay.get("duration",0)
                            lay_name=lay.get("name","")
                            overnight=" 🌙 Nuit sur place" if lay.get("overnight") else ""
                            st.markdown(f"""
                            <div class="layover-box">
                              ⏳ Escale à <b>{lay_name}</b> — {fmt_dur(lay_dur)}{overnight}
                            </div>
                            """, unsafe_allow_html=True)
                        elif esc_v:
                            st.markdown(f"""
                            <div class="layover-box">⏳ Escale via {esc_v.split(',')[i] if i<len(esc_v.split(',')) else esc_v}</div>
                            """, unsafe_allow_html=True)
            else:
                # Affichage simplifié sans segments détaillés
                c1,c2,c3=st.columns(3)
                with c1: st.metric("Durée totale",fmt_dur(v.get("duree_minutes",0)))
                with c2: st.metric("Escales","Direct" if nb_esc==0 else f"{nb_esc} — {esc_v}")
                with c3: st.metric("Places restantes",places)

        with t2:
            bag=BAGGAGE_INFO.get(cabin,BAGGAGE_INFO["economy"])
            st.markdown(f"""
            <div class="conditions-box">
              <div style="font-size:1.1rem;font-weight:600;color:#E8EAF0;margin-bottom:.75rem">
                {bag['icon']} Franchise bagages — {CABIN_LABELS.get(cabin,'')}
              </div>
              <div class="cond-row">
                <span style="font-size:1.2rem">🎒</span>
                <div>
                  <div style="font-weight:500;color:#E8EAF0">Bagage cabine</div>
                  <div style="font-size:.82rem;color:#6B7A99">{bag['cabine']}</div>
                </div>
              </div>
              <div class="cond-row">
                <span style="font-size:1.2rem">🧳</span>
                <div>
                  <div style="font-weight:500;color:#E8EAF0">Bagage en soute</div>
                  <div style="font-size:.82rem;color:#6B7A99">{bag['soute']}</div>
                </div>
              </div>
              <div style="margin-top:.75rem;padding:.6rem;background:rgba(79,195,247,.05);
                border-radius:8px;font-size:.8rem;color:#6B7A99">
                ℹ️ {bag['note']}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with t3:
            conds=CONDITIONS.get(cabin,CONDITIONS["economy"])
            st.markdown('<div class="conditions-box">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size:1.1rem;font-weight:600;color:#E8EAF0;margin-bottom:.75rem">
              📋 Conditions tarifaires — {CABIN_LABELS.get(cabin,'')}
            </div>
            """, unsafe_allow_html=True)
            for key,cond in conds.items():
                color_detail="#00E676" if cond["ok"] else "#EF5350"
                st.markdown(f"""
                <div class="cond-row">
                  <span style="font-size:1.1rem">{cond['icon']}</span>
                  <div style="flex:1">
                    <div style="font-weight:500;color:#E8EAF0">{cond['label']}</div>
                    <div style="font-size:.8rem;color:{color_detail}">{cond['detail']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("⚠️ Conditions indicatives. Vérifiez sur le site de la compagnie avant réservation.")

        with t4:
            c1,c2=st.columns(2)
            with c1:
                st.metric("Prix total",fmt_prix(prix*pax))
                st.metric("Prix / personne",fmt_prix(prix))
            with c2:
                st.metric("Classe",f"{CABIN_ICONS.get(cabin,'')} {CABIN_LABELS.get(cabin,'')}")
                st.metric("Passagers",pax)
            if co2 and isinstance(co2,dict):
                kg=co2.get("this_flight",""); diff=co2.get("difference_percent","")
                if kg: st.caption(f"🌿 CO₂ estimé : {kg} kg ({'+'if diff and diff>0 else ''}{diff}% vs moyenne)")
            st.markdown(f"""
            <a href="{url}" target="_blank" style="
                display:block;text-align:center;padding:.8rem 1.5rem;
                background:linear-gradient(135deg,#4FC3F7,#7C4DFF);
                color:white;border-radius:12px;text-decoration:none;
                font-weight:700;font-family:'Syne',sans-serif;margin-top:.75rem;font-size:1rem">
                ✈ Réserver sur {name} →
            </a>""", unsafe_allow_html=True)

# ── Écran config ──────────────────────────────────────────────────────────────
def show_setup():
    st.markdown("""
    <div class="setup-box">
      <div style="font-size:3rem;margin-bottom:1rem">🔑</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;
           color:#E8EAF0;margin-bottom:.5rem">Configurez SerpApi</div>
      <div style="color:#6B7A99;font-size:.9rem;margin-bottom:1.5rem">
        Pour voir de vrais prix de vols en temps réel,<br>une clé SerpApi gratuite est nécessaire.
      </div>
      <div class="setup-step">
        <div class="step-num">1</div>
        <div><div style="font-weight:600;color:#E8EAF0">Créer un compte gratuit</div>
          <div style="font-size:.85rem;color:#6B7A99;margin-top:2px">
            <a href="https://serpapi.com" target="_blank" style="color:#4FC3F7">serpapi.com</a>
            → Start Free Trial → vérifiez votre email</div></div>
      </div>
      <div class="setup-step">
        <div class="step-num">2</div>
        <div><div style="font-weight:600;color:#E8EAF0">Copier votre API Key</div>
          <div style="font-size:.85rem;color:#6B7A99;margin-top:2px">Dans votre dashboard → copiez la clé</div></div>
      </div>
      <div class="setup-step">
        <div class="step-num">3</div>
        <div><div style="font-weight:600;color:#E8EAF0">Coller dans le menu latéral gauche</div>
          <div style="font-size:.85rem;color:#6B7A99;margin-top:2px">Cliquez ☰ → collez la clé → Activer</div></div>
      </div>
      <div style="margin-top:1rem;padding:.75rem;background:#0D1426;border-radius:10px;
           border:1px solid #2A3560;font-size:.82rem;color:#6B7A99">
        🎁 <b style="color:#4FC3F7">100 recherches gratuites / mois</b> · Pas de CB requise
      </div>
    </div>""", unsafe_allow_html=True)

# ── App principale ────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="hero-title">✈ Choisy voyages</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub"> 7 000+ aéroports · Conditions & bagages détaillés</div>',
                unsafe_allow_html=True)

    client = get_client()
    if not client and "serpapi_key" in st.session_state:
        try:
            from serpapi_client import SerpApiFlightsClient
            client = SerpApiFlightsClient(st.session_state["serpapi_key"])
        except Exception: pass

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🔑 SerpApi")
        if client:
            st.success("✅ Connectée")
            if st.button("Changer de clé"):
                st.session_state.pop("serpapi_key",None)
                st.rerun()
        else:
            st.markdown("**[→ serpapi.com](https://serpapi.com)** · 100 req/mois gratuit")
            k = st.text_input("API Key",type="password",placeholder="Collez votre clé...")
            if st.button("🔌 Activer"):
                if k.strip():
                    try:
                        from serpapi_client import SerpApiFlightsClient
                        c = SerpApiFlightsClient(k.strip())
                        r = c.test_connection()
                        if r["ok"]:
                            st.session_state["serpapi_key"]=k.strip()
                            st.success("✅ Connectée !"); st.rerun()
                        else: st.error(f"❌ {r.get('error','Clé invalide')}")
                    except Exception as e: st.error(f"❌ {e}")
                else: st.warning("Entrez votre clé.")

        if client:
            st.markdown("---")
            st.markdown("## 🎛️ Filtres")
            prix_max=st.slider("Prix max (€)",50,5000,3000,50)
            esc_c=st.radio("Escales",["Tous","Direct","Max 1","Max 2"])
            esc_m={"Tous":None,"Direct":0,"Max 1":1,"Max 2":2}
            sort_by=st.selectbox("Trier par",
                ["💰 Prix croissant","💰 Prix décroissant","⏱️ Durée","🕐 Heure départ"])
        else:
            prix_max=3000; esc_c="Tous"; esc_m={"Tous":None}; sort_by="💰 Prix croissant"

    if not client:
        show_setup(); return

    with st.spinner("Chargement des aéroports..."):
        adict=ap_dict(); labels=[a["label"] for a in load_airports()]

    # ── Panneau de recherche ──────────────────────────────────────────────────
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)

    # Type de trajet
    c_type,c_pax,c_cabin=st.columns([3,1,1])
    with c_type:
        trip=st.radio("Trajet",
            ["✈️ Aller simple","🔄 Aller-retour","📅 Flexible (±3 jours)","🗺️ Multi-destinations"],
            horizontal=True,label_visibility="collapsed")
    with c_pax:
        pax=st.selectbox("Passagers",[1,2,3,4,5,6],label_visibility="collapsed")
    with c_cabin:
        cabin=st.selectbox("Classe",
            list(CABIN_LABELS.keys()),
            format_func=lambda x:f"{CABIN_ICONS[x]} {CABIN_LABELS[x]}",
            label_visibility="collapsed")

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Mode Multi-destinations ───────────────────────────────────────────────
    if "Multi" in trip:
        st.markdown("**🗺️ Ajoutez vos étapes**")
        if "legs" not in st.session_state:
            st.session_state["legs"]=[
                {"from":"","to":"","date":""},
                {"from":"","to":"","date":""},
            ]
        legs=st.session_state["legs"]
        for i,leg in enumerate(legs):
            ca,cb,cc,cd=st.columns([2,2,1.5,.5])
            with ca:
                idx_o=next((j for j,l in enumerate(labels) if "(CDG)" in l),0) if i==0 else 0
                lo=st.selectbox(f"Départ {i+1}",labels,index=idx_o,key=f"leg_o_{i}",label_visibility="collapsed")
                leg["from"]=iata_from_label(lo)
            with cb:
                idx_d=next((j for j,l in enumerate(labels) if "(JFK)" in l),1) if i==0 else 0
                ld=st.selectbox(f"Dest {i+1}",labels,index=idx_d,key=f"leg_d_{i}",label_visibility="collapsed")
                leg["to"]=iata_from_label(ld)
            with cc:
                dd=st.date_input(f"Date {i+1}",
                    value=date.today()+timedelta(days=14+i*7),
                    min_value=date.today(),
                    max_value=date.today()+timedelta(days=330),
                    key=f"leg_date_{i}",label_visibility="collapsed")
                leg["date"]=dd
            with cd:
                if i>=2 and st.button("✕",key=f"rm_{i}"):
                    legs.pop(i); st.rerun()
        if len(legs)<5:
            if st.button("➕ Ajouter une étape"):
                legs.append({"from":"","to":"","date":date.today()+timedelta(days=14+len(legs)*7)})
                st.rerun()
        go_btn=st.button("🔍 Rechercher tous les vols")
        iata_o=legs[0]["from"]; iata_d=legs[-1]["to"]
        dep=legs[0]["date"]; ret=None
    else:
        # Recherche standard / flexible
        c1,c2,c3,c4,c5=st.columns([2,2,1.5,1.5,1])
        with c1:
            st.markdown("**🛫 Départ**")
            def_o=next((i for i,l in enumerate(labels) if "(CDG)" in l),0)
            lbl_o=st.selectbox("Départ",labels,index=def_o,label_visibility="collapsed",key="sel_o")
            iata_o=iata_from_label(lbl_o)
        with c2:
            st.markdown("**🛬 Destination**")
            def_d=next((i for i,l in enumerate(labels) if "(JFK)" in l),1)
            lbl_d=st.selectbox("Destination",labels,index=def_d,label_visibility="collapsed",key="sel_d")
            iata_d=iata_from_label(lbl_d)
        with c3:
            st.markdown("**📅 Date aller**")
            dep=st.date_input("Aller",value=date.today()+timedelta(days=14),
                min_value=date.today(),max_value=date.today()+timedelta(days=330),
                label_visibility="collapsed")
        with c4:
            st.markdown("**📅 Date retour**")
            has_ret="retour" in trip.lower()
            if has_ret:
                ret=st.date_input("Retour",value=dep+timedelta(days=7),
                    min_value=dep,max_value=date.today()+timedelta(days=330),
                    label_visibility="collapsed")
            else:
                ret=None
                st.markdown('<div style="color:#4B5A7A;font-size:.85rem;padding-top:8px">— Non requis</div>',
                    unsafe_allow_html=True)
        with c5:
            st.markdown("**&nbsp;**")
            go_btn=st.button("🔍 Rechercher")
        legs=None

    st.markdown('</div>',unsafe_allow_html=True)

    # Agrégateurs
    if iata_o and iata_d:
        agg=agg_urls(iata_o,iata_d,dep,ret,pax)
        cols=st.columns(4); clrs=["#4FC3F7","#FF9800","#00C853","#E040FB"]
        for i,(name,url) in enumerate(agg.items()):
            with cols[i]:
                st.markdown(
                    f'<a href="{url}" target="_blank" style="display:block;text-align:center;'
                    f'padding:.65rem;background:linear-gradient(145deg,#12182E,#161E38);'
                    f'border:1px solid {clrs[i]};border-radius:12px;color:{clrs[i]};'
                    f'text-decoration:none;font-weight:600;font-size:.88rem;margin-bottom:.5rem">'
                    f'{name}</a>',unsafe_allow_html=True)

    # ── Résultats ─────────────────────────────────────────────────────────────
    if go_btn or "last_s" in st.session_state:
        if go_btn:
            if iata_o==iata_d:
                st.warning("⚠️ Départ et destination identiques."); return
            st.session_state["last_s"]={
                "iata_o":iata_o,"iata_d":iata_d,"dep":dep,"ret":ret,
                "pax":pax,"cabin":cabin,"trip":trip,"legs":legs,
                "prix_max":prix_max,"esc":esc_m[esc_c],"sort":sort_by,
            }

        s=st.session_state["last_s"]
        io=s["iata_o"]; id_=s["iata_d"]
        d_dep=s["dep"]; d_ret=s["ret"]
        n_pax=s["pax"]; cab=s["cabin"]
        max_p=s.get("prix_max",3000); max_e=s.get("esc"); srt=s.get("sort","💰 Prix croissant")
        s_legs=s.get("legs")

        ao=adict.get(io,{}); ad_=adict.get(id_,{})
        city_o=ao.get("city",io); city_d=ad_.get("city",id_)
        cabin_lbl=CABIN_LABELS.get(cab,cab)
        cabin_icon=CABIN_ICONS.get(cab,"")

        tab_vols,tab_flex,tab_carte,tab_analyse=st.tabs(
            ["✈️ Vols","📅 Calendrier flexible","🗺️ Carte","📊 Analyse"])

        with tab_vols:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;flex-wrap:wrap">
              <span style="font-family:'Syne';font-size:1.15rem;font-weight:700;color:#E8EAF0">
                {city_o} → {city_d}
              </span>
              <span class="badge badge-blue">{io} → {id_}</span>
              <span class="badge badge-purple">👥 {n_pax} passager{'s' if n_pax>1 else ''}</span>
              <span class="badge badge-teal">{cabin_icon} {cabin_lbl}</span>
            </div>""",unsafe_allow_html=True)

            with st.spinner("🔍 Recherche des vols en cours..."):
                try:
                    dep_str=d_dep.strftime("%Y-%m-%d") if hasattr(d_dep,"strftime") else str(d_dep)
                    ret_str=(d_ret.strftime("%Y-%m-%d") if d_ret and hasattr(d_ret,"strftime")
                             else str(d_ret) if d_ret else None)

                    # Multi-destinations
                    if s_legs and len(s_legs)>=2:
                        all_vols=[]
                        for leg in s_legs:
                            if not leg.get("from") or not leg.get("to"): continue
                            ld=leg["date"]
                            lds=ld.strftime("%Y-%m-%d") if hasattr(ld,"strftime") else str(ld)
                            try:
                                rows=client.search(
                                    origin=leg["from"],destination=leg["to"],
                                    departure_date=lds,adults=n_pax,
                                    cabin=cab,max_stops=max_e)
                                all_vols.extend(rows[:5])
                            except Exception as e:
                                st.warning(f"Leg {leg['from']}→{leg['to']}: {e}")
                        vols=all_vols
                    elif "Flexible" in s["trip"]:
                        # Mode flexible : recherche sur ±3 jours
                        dates=[d_dep+timedelta(days=i) for i in range(-3,4)]
                        all_v=[]; seen=set()
                        for dd in dates:
                            ds=dd.strftime("%Y-%m-%d") if hasattr(dd,"strftime") else str(dd)
                            try:
                                rows=client.search(origin=io,destination=id_,
                                    departure_date=ds,adults=n_pax,cabin=cab,max_stops=max_e)
                                for v in rows:
                                    key=(v["flight_number"],v["date_depart"])
                                    if key not in seen:
                                        seen.add(key); all_v.append(v)
                            except Exception: pass
                        vols=all_v
                    else:
                        vols=client.search(origin=io,destination=id_,
                            departure_date=dep_str,return_date=ret_str,
                            adults=n_pax,cabin=cab,max_stops=max_e)
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
                    vols=[]

            # Filtres
            if max_p: vols=[v for v in vols if float(v.get("prix",0))<=max_p]

            # Tri
            def sk(v):
                if "décroissant" in srt: return -float(v.get("prix",0))
                if "Durée" in srt: return int(v.get("duree_minutes",0))
                if "Heure" in srt: return str(v.get("date_depart",""))
                return float(v.get("prix",0))
            vols=sorted(vols,key=sk)

            if vols:
                pl=[float(v.get("prix",0)) for v in vols]
                m1,m2,m3,m4=st.columns(4)
                for col_m,(val,lbl) in zip([m1,m2,m3,m4],[
                    (fmt_prix(min(pl)),"Meilleur prix"),
                    (fmt_prix(sum(pl)/len(pl)),"Prix moyen"),
                    (str(len(vols)),"Vols trouvés"),
                    (str(sum(1 for v in vols if int(v.get("escales",0))==0)),"Directs"),
                ]):
                    with col_m:
                        st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div>'
                                    f'<div class="metric-lbl">{lbl}</div></div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                for i,v in enumerate(vols[:30]):
                    render_vol(v,i==0,io,id_,d_dep,d_ret,n_pax,cab)
            else:
                st.markdown("""
                <div style="text-align:center;padding:3rem;color:#6B7A99">
                  <div style="font-size:3rem">🔍</div>
                  <div style="font-size:1.1rem;font-weight:600;color:#E8EAF0;margin-bottom:8px">
                    Aucun vol trouvé
                  </div>
                  <div>Essayez d'autres dates, une autre classe, ou les comparateurs ci-dessus.</div>
                </div>""",unsafe_allow_html=True)

        # ── Onglet Calendrier Flexible ─────────────────────────────────────────
        with tab_flex:
            st.markdown("### 📅 Calendrier des prix — Choisissez le meilleur jour")
            st.markdown("*Comparaison des prix sur les 14 prochains jours depuis votre date*")

            with st.spinner("Chargement du calendrier..."):
                cal_data={}
                base=d_dep if hasattr(d_dep,"strftime") else date.today()
                dep_str=base.strftime("%Y-%m-%d")
                for i in range(14):
                    dd=base+timedelta(days=i-3)
                    if dd<date.today(): continue
                    ds=dd.strftime("%Y-%m-%d")
                    try:
                        rows=client.search(origin=io,destination=id_,
                            departure_date=ds,adults=n_pax,cabin=cab,max_stops=0)
                        if rows:
                            cal_data[ds]={"min":min(float(v["prix"]) for v in rows),
                                          "count":len(rows),"date":dd}
                    except Exception: pass

            if cal_data:
                prices=[v["min"] for v in cal_data.values()]
                min_p=min(prices); max_p2=max(prices)

                # Graphique calendrier
                dates_list=sorted(cal_data.keys())
                fig_cal=go.Figure()
                bar_colors=[]
                for d_k in dates_list:
                    p=cal_data[d_k]["min"]
                    if p==min_p: bar_colors.append("#00E676")
                    elif p<min_p*1.1: bar_colors.append("#4FC3F7")
                    elif p>min_p*1.3: bar_colors.append("#EF5350")
                    else: bar_colors.append("#7C4DFF")

                fig_cal.add_trace(go.Bar(
                    x=[cal_data[d]["date"].strftime("%d %b") for d in dates_list],
                    y=[cal_data[d]["min"] for d in dates_list],
                    marker_color=bar_colors,
                    text=[fmt_prix(cal_data[d]["min"]) for d in dates_list],
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>Prix min: %{y:.0f} €<extra></extra>",
                ))
                fig_cal.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter",color="#6B7A99"),
                    xaxis=dict(gridcolor="#1A2240"),
                    yaxis=dict(gridcolor="#1A2240",ticksuffix=" €"),
                    height=320,margin=dict(l=0,r=0,t=30,b=0),
                    showlegend=False,
                )
                st.plotly_chart(fig_cal,width="stretch")

                # Résumé textuel
                best_date=min(cal_data,key=lambda d:cal_data[d]["min"])
                best_info=cal_data[best_date]
                st.success(f"🏷 **Meilleur prix détecté :** {fmt_prix(best_info['min'])} "
                           f"le **{best_info['date'].strftime('%A %d %b')}** "
                           f"({best_info['count']} vols disponibles)")

                # Tableau récap
                rows_cal=[{
                    "Date":cal_data[d]["date"].strftime("%a %d %b"),
                    "Prix min":fmt_prix(cal_data[d]["min"]),
                    "Vols":cal_data[d]["count"],
                    "Tendance":"🟢 Meilleur" if cal_data[d]["min"]==min_p
                              else "🔴 Cher" if cal_data[d]["min"]>min_p*1.3
                              else "🟡 Correct"
                } for d in dates_list]
                st.dataframe(pd.DataFrame(rows_cal),hide_index=True,use_container_width=True)
            else:
                st.info("Aucune donnée de prix disponible pour ce trajet sur les prochains jours.")

        # ── Carte ─────────────────────────────────────────────────────────────
        with tab_carte:
            st.markdown("### 🗺️ Trajet")
            if ao and ad_:
                lat_o,lon_o=ao.get("lat",0),ao.get("lon",0)
                lat_d,lon_d=ad_.get("lat",0),ad_.get("lon",0)
                n=60
                lats=[lat_o+(lat_d-lat_o)*i/n for i in range(n+1)]
                lons=[lon_o+(lon_d-lon_o)*i/n for i in range(n+1)]
                mid=n//2
                for i in range(1,n):
                    f=1-abs(i-mid)/mid; lats[i]+=4*f; lons[i]+=2*f
                fig_map=go.Figure()
                fig_map.add_trace(go.Scattermap(lat=lats,lon=lons,mode="lines",
                    line=dict(color="#4FC3F7",width=3),opacity=0.8,name="Trajet"))
                fig_map.add_trace(go.Scattermap(lat=[lat_o],lon=[lon_o],mode="markers+text",
                    marker=dict(size=16,color="#00E676"),
                    text=[f"✈ {city_o}"],textposition="top right",
                    textfont=dict(color="white",size=12),name=city_o))
                fig_map.add_trace(go.Scattermap(lat=[lat_d],lon=[lon_d],mode="markers+text",
                    marker=dict(size=16,color="#E040FB"),
                    text=[f"🏁 {city_d}"],textposition="top right",
                    textfont=dict(color="white",size=12),name=city_d))
                clat=(lat_o+lat_d)/2; clon=(lon_o+lon_d)/2
                dist=math.sqrt((lat_d-lat_o)**2+(lon_d-lon_o)**2)
                zoom=max(1,7-math.log(dist+1)*1.5)
                fig_map.update_layout(
                    map=dict(style="dark",center=dict(lat=clat,lon=clon),zoom=zoom),
                    paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=0,b=0),height=500,
                    legend=dict(bgcolor="rgba(18,24,46,0.8)",bordercolor="#2A3560",font=dict(color="#E8EAF0")))
                st.plotly_chart(fig_map,width="stretch")

        # ── Analyse ───────────────────────────────────────────────────────────
        with tab_analyse:
            vols_an=st.session_state.get("last_s",{})
            # Récupérer les vols depuis le dernier search
            if "vols_cache" in st.session_state and st.session_state["vols_cache"]:
                vols_data=st.session_state["vols_cache"]
            else: vols_data=[]
            if vols_data:
                df_a=pd.DataFrame(vols_data); df_a["prix"]=df_a["prix"].astype(float)
                c1,c2=st.columns(2)
                with c1:
                    g=df_a.groupby("airline_name").agg(nb=("prix","count"),pm=("prix","mean")).reset_index()
                    fb=px.bar(g,x="airline_name",y="nb",color="pm",
                              color_continuous_scale=["#00E676","#4FC3F7","#7C4DFF"],
                              title="Vols par compagnie")
                    fb.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#6B7A99"),height=280,margin=dict(l=0,r=0,t=40,b=0),
                        xaxis_tickangle=-30)
                    st.plotly_chart(fb,width="stretch")
                with c2:
                    fh=px.histogram(df_a,x="prix",nbins=12,title="Distribution des prix",
                                    color_discrete_sequence=["#4FC3F7"])
                    fh.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#6B7A99"),height=280,margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fh,width="stretch")
            else:
                st.info("Lancez une recherche pour voir l'analyse.")

if __name__=="__main__":
    main()
