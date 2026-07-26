import requests, re
from datetime import datetime, timedelta
from typing import Optional, List

AIRLINE_NAMES = {
    "Air France":"AF","British Airways":"BA","Lufthansa":"LH","Emirates":"EK",
    "KLM":"KL","easyJet":"U2","Ryanair":"FR","Turkish Airlines":"TK",
    "Transavia":"TO","Royal Air Maroc":"AT","Qatar Airways":"QR","Etihad Airways":"EY",
    "Singapore Airlines":"SQ","Cathay Pacific":"CX","Korean Air":"KE",
    "Air Canada":"AC","Delta":"DL","Delta Air Lines":"DL","United Airlines":"UA",
    "American Airlines":"AA","Swiss":"LX","Austrian Airlines":"OS",
    "Brussels Airlines":"SN","Iberia":"IB","Vueling":"VY","TAP Air Portugal":"TP",
    "ITA Airways":"AZ","Air Algérie":"AH","Tunisair":"TU","Ethiopian Airlines":"ET",
    "South African Airways":"SA","Air India":"AI","EgyptAir":"MS","Aeroflot":"SU",
    "Air China":"CA","Aeromexico":"AM","Vietnam Airlines":"VN",
    "Malaysia Airlines":"MH","Thai Airways":"TG","ANA":"NH","Japan Airlines":"JL",
    "Asiana":"OZ","Wizz Air":"W6","Pegasus":"PC","SunExpress":"XQ",
    "Air Europa":"UX","Air Cote D'Ivoire":"HF","Air Côte d'Ivoire":"HF",
    "Kenya Airways":"KQ","RwandAir":"WB","TAAG Angola Airlines":"DT",
    "Corsair":"SS","Condor":"DE","TUI fly":"X3","Corendon":"XC",
}

AIRLINE_CODES = {v:k for k,v in AIRLINE_NAMES.items()}

AIRLINE_COLORS = {
    "AF":"#002157","BA":"#075AAA","LH":"#05164D","EK":"#C60C30","KL":"#00A1DE",
    "U2":"#FF6600","FR":"#073590","TK":"#C8102E","TO":"#00B140","AT":"#BE0A15",
    "QR":"#5C0632","EY":"#BD8B13","SQ":"#F0A500","CX":"#006564","KE":"#00256C",
    "AC":"#D22630","DL":"#C01933","UA":"#002244","AA":"#B61F23","LX":"#E30613",
    "OS":"#C60000","SN":"#2D2A6E","IB":"#D40000","VY":"#FFD700","TP":"#009DE0",
    "AZ":"#008C45","AH":"#008000","TU":"#CC0000","ET":"#078930","AI":"#C8102E",
    "W6":"#C8102E","PC":"#FF6600","NH":"#003087","JL":"#E60026","TG":"#600080",
    "HF":"#009FE3","KQ":"#C8102E","WB":"#007DC5","MH":"#C00000",
}

BOOKING_URLS = {
    "AF": lambda o,d,dep,ret,p: f"https://www.airfrance.fr/FR/fr/local/process/accueil/searchresults.do?depCity={o}&destCity={d}&adults={p}&tripType={'RT' if ret else 'OW'}",
    "BA": lambda o,d,dep,ret,p: f"https://www.britishairways.com/travel/fx/public/fr_fr?eId=106005&Oc={o}&Dc={d}&Md={'1' if ret else '2'}&Cl=M&Ad={p}",
    "LH": lambda o,d,dep,ret,p: f"https://www.lufthansa.com/fr/fr/flight-search?origin={o}&destination={d}&outboundDate={dep}{'&returnDate='+ret if ret else ''}&adults={p}",
    "EK": lambda o,d,dep,ret,p: f"https://www.emirates.com/fr/french/book/flights/#/outbound/selectflight?OriginCode={o}&DestinationCode={d}&JourneyType={'return' if ret else 'oneway'}&Adult={p}",
    "KL": lambda o,d,dep,ret,p: f"https://www.klm.com/search/fr-fr/{o}/{d}/{dep}{'/' + ret if ret else ''}/{p}/0/0/economy",
    "U2": lambda o,d,dep,ret,p: f"https://www.easyjet.com/fr/cheap-flights/{o.lower()}-{d.lower()}",
    "FR": lambda o,d,dep,ret,p: f"https://www.ryanair.com/fr/fr/trip/flights/select?ADTCount={p}&OriginIata={o}&DestinationIata={d}&DateOut={dep}{'&DateIn='+ret+'&isReturn=true' if ret else '&isReturn=false'}",
    "TK": lambda o,d,dep,ret,p: f"https://www.turkishairlines.com/fr-fr/booking/flight-booking/?from={o}&to={d}&date={dep}{'&return='+ret if ret else ''}&adult={p}",
    "QR": lambda o,d,dep,ret,p: f"https://www.qatarairways.com/fr-fr/flights.html",
    "TO": lambda o,d,dep,ret,p: f"https://www.transavia.com/fr-FR/book/flights/?from={o}&to={d}&departure={dep}{'&return='+ret if ret else ''}&adults={p}",
    "IB": lambda o,d,dep,ret,p: f"https://www.iberia.com/fr/flights/{o}-{d}/?adult={p}",
    "TP": lambda o,d,dep,ret,p: f"https://www.flytap.com/fr-fr/flights/{o}/{d}/{dep}/{''+ret+'/' if ret else ''}1/0/0",
    "DL": lambda o,d,dep,ret,p: f"https://www.delta.com/fr/fr/flight-search/book-a-flight",
    "UA": lambda o,d,dep,ret,p: f"https://www.united.com/fr/fr/flight-search/book-a-flight",
    "AA": lambda o,d,dep,ret,p: f"https://www.aa.com/booking/search",
    "AC": lambda o,d,dep,ret,p: f"https://www.aircanada.com/fr/en/aco/home.html",
    "LX": lambda o,d,dep,ret,p: f"https://www.swiss.com/fr/fr/booking/flights",
    "SQ": lambda o,d,dep,ret,p: f"https://www.singaporeair.com/fr_FR/plan-and-book/flights/",
    "AH": lambda o,d,dep,ret,p: f"https://www.airalgerie.dz/reservation",
    "TU": lambda o,d,dep,ret,p: f"https://www.tunisair.com/reservation",
    "AT": lambda o,d,dep,ret,p: f"https://www.royalairmaroc.com/fr",
    "ET": lambda o,d,dep,ret,p: f"https://www.ethiopianairlines.com/book/booking/flight-booking",
    "EY": lambda o,d,dep,ret,p: f"https://www.etihad.com/fr-fr/fly-etihad/book-a-flight",
}

def get_booking_url(code, iata_o, iata_d, dep_date, ret_date, pax):
    fn = BOOKING_URLS.get(code)
    if fn:
        try:
            return fn(iata_o, iata_d, dep_date, ret_date, pax)
        except Exception:
            pass
    return f"https://www.google.com/travel/flights?q=Vols+{iata_o}+vers+{iata_d}&hl=fr&curr=EUR"


def parse_serpapi_time(date_str: str, time_field: str) -> Optional[datetime]:
    """
    Parse robuste des heures SerpApi.
    SerpApi retourne les heures dans plusieurs formats selon la version :
      - ISO complet : "2026-06-16T14:35:00"  (le plus courant)
      - Date+heure  : "2026-06-16, 2:35 PM"
      - Heure seule : "2:35 PM" ou "14:35"
    """
    if not time_field:
        return None
    t = str(time_field).strip()

    # Format ISO complet : 2026-06-16T14:35 ou 2026-06-16 14:35:00
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            pass

    # Format "2026-06-16, 2:35 PM"
    m = re.match(r'(\d{4}-\d{2}-\d{2}),?\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)', t, re.IGNORECASE)
    if m:
        d_part = m.group(1)
        t_part = m.group(2).strip()
        for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(f"{d_part} {t_part}", fmt)
            except ValueError:
                pass

    # Heure seule "2:35 PM" ou "14:35"
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            t_obj = datetime.strptime(t, fmt)
            base  = datetime.strptime(str(date_str), "%Y-%m-%d")
            return base.replace(hour=t_obj.hour, minute=t_obj.minute)
        except ValueError:
            pass

    return None


class SerpApiFlightsClient:
    API_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def test_connection(self) -> dict:
        try:
            resp = requests.get(self.API_URL, params={
                "engine":"google_flights","api_key":self.api_key,
                "departure_id":"CDG","arrival_id":"LHR",
                "outbound_date":"2026-09-01","adults":1,
                "currency":"EUR","hl":"fr"}, timeout=15)
            data = resp.json()
            if "error" in data:
                return {"ok":False,"error":data["error"]}
            return {"ok":True}
        except Exception as e:
            return {"ok":False,"error":str(e)}

    def search(self, origin, destination, departure_date,
               return_date=None, adults=1, cabin="economy",
               max_stops=None, currency="EUR") -> List[dict]:
        cabin_map = {"economy":1,"premium_economy":2,"business":3,"first":4}
        params = {
            "engine":         "google_flights",
            "api_key":        self.api_key,
            "departure_id":   origin.upper(),
            "arrival_id":     destination.upper(),
            "outbound_date":  departure_date,
            "adults":         adults,
            "travel_class":   cabin_map.get(cabin.lower(), 1),
            "currency":       currency,
            "hl":             "fr",
            "type":           1 if return_date else 2,
        }
        if return_date:
            params["return_date"] = return_date
        if max_stops == 0:
            params["stops"] = 1

        resp = requests.get(self.API_URL, params=params, timeout=25)
        data = resp.json()
        if "error" in data:
            raise ValueError(data["error"])
        return self._parse(data, origin, destination, departure_date,
                           return_date, adults, max_stops)

    def _parse(self, data, iata_o, iata_d, dep_date, ret_date, adults, max_stops):
        results = []
        ret_str = str(ret_date) if ret_date else None

        for section in ["best_flights", "other_flights"]:
            for offer in data.get(section, []):
                try:
                    flights = offer.get("flights", [])
                    if not flights:
                        continue

                    price = float(offer.get("price", 0))
                    if price <= 0:
                        continue

                    total_dur = int(offer.get("total_duration", 0))
                    first = flights[0]
                    last  = flights[-1]

                    dep_ap = first.get("departure_airport", {})
                    arr_ap = last.get("arrival_airport",   {})

                    dep_iata = dep_ap.get("id", iata_o)
                    arr_iata = arr_ap.get("id", iata_d)

                    # ── Heures : format ISO complet dans SerpApi ──────────────
                    dep_time_raw = dep_ap.get("time", "")
                    arr_time_raw = arr_ap.get("time", "")

                    dep_dt = parse_serpapi_time(dep_date, dep_time_raw)
                    arr_dt = parse_serpapi_time(dep_date, arr_time_raw)

                    # Vol de nuit : arrivée le lendemain
                    if dep_dt and arr_dt and arr_dt < dep_dt:
                        arr_dt += timedelta(days=1)

                    dep_fmt = dep_dt.strftime("%Y-%m-%d %H:%M") if dep_dt else f"{dep_date} 00:00"
                    arr_fmt = arr_dt.strftime("%Y-%m-%d %H:%M") if arr_dt else f"{dep_date} 00:00"

                    # ── Compagnie ─────────────────────────────────────────────
                    airline_name = first.get("airline", "")
                    logo_url     = first.get("airline_logo", "")

                    # Extraire code depuis URL du logo
                    airline_code = ""
                    if logo_url:
                        m = re.search(r'/([A-Z0-9]{2})(?:\.png|\.svg|/)', logo_url)
                        if m:
                            airline_code = m.group(1)
                    if not airline_code or len(airline_code) < 2:
                        airline_code = AIRLINE_NAMES.get(airline_name, "")
                    if not airline_code:
                        # Dernier recours : 2 premières lettres du nom
                        airline_code = (airline_name[:2].upper() if airline_name else "??")

                    flight_num = first.get("flight_number", f"{airline_code}000")

                    # ── Escales ───────────────────────────────────────────────
                    nb_escales   = len(flights) - 1
                    escale_villes = ",".join([
                        f.get("arrival_airport",{}).get("id","")
                        for f in flights[:-1]
                        if f.get("arrival_airport",{}).get("id","")
                    ])

                    if max_stops is not None and nb_escales > max_stops:
                        continue

                    # Durée calculée si non fournie
                    if not total_dur and dep_dt and arr_dt:
                        total_dur = int((arr_dt - dep_dt).total_seconds() / 60)

                    # CO2
                    co2 = offer.get("carbon_emissions", {})

                    results.append({
                        "source":             "serpapi",
                        "flight_number":      flight_num,
                        "airline_code":       airline_code,
                        "airline_name":       airline_name or AIRLINE_CODES.get(airline_code, airline_code),
                        "airline_color":      AIRLINE_COLORS.get(airline_code, "#4FC3F7"),
                        "iata_o":             dep_iata,
                        "iata_d":             arr_iata,
                        "date_depart":        dep_fmt,
                        "date_arrivee":       arr_fmt,
                        "duree_minutes":      total_dur,
                        "escales":            nb_escales,
                        "escale_villes":      escale_villes,
                        "prix":               price,
                        "prix_business":      round(price * 3.2, 2),
                        "places_disponibles": 9,
                        "currency":           "EUR",
                        "prix_par_pax":       round(price / adults, 2),
                        "deep_link":          get_booking_url(
                                                  airline_code, dep_iata, arr_iata,
                                                  str(dep_date), ret_str, adults),
                        "carbon_emissions":   co2,
                    })
                except Exception:
                    continue

        return sorted(results, key=lambda x: x["prix"])
