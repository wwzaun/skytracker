import requests
import json
from datetime import datetime, date
from typing import List, Optional, Dict
import time

# ─── Codes IATA des aéroports par ville ───────────────────────────────────────
VILLE_TO_IATA = {
    "Paris": ["CDG", "ORY"],
    "Londres": ["LHR", "LGW", "STN"],
    "New York": ["JFK", "EWR", "LGA"],
    "Los Angeles": ["LAX"],
    "Tokyo": ["NRT", "HND"],
    "Dubaï": ["DXB"],
    "Barcelone": ["BCN"],
    "Amsterdam": ["AMS"],
    "Francfort": ["FRA"],
    "Singapour": ["SIN"],
    "Sydney": ["SYD"],
    "Toronto": ["YYZ"],
    "Madrid": ["MAD"],
    "Rome": ["FCO", "CIA"],
    "Bangkok": ["BKK", "DMK"],
    "Istanbul": ["IST"],
    "Montréal": ["YUL"],
    "São Paulo": ["GRU"],
    "Marrakech": ["RAK"],
    "Lisbonne": ["LIS"],
    "Athènes": ["ATH"],
    "Miami": ["MIA"],
    "Tunis": ["TUN"],
    "Alger": ["ALG"],
    "Casablanca": ["CMN"],
    "Doha": ["DOH"],
    "Hong Kong": ["HKG"],
    "Séoul": ["ICN"],
    "Mumbai": ["BOM"],
    "Le Caire": ["CAI"],
    "Nairobi": ["NBO"],
    "Johannesburg": ["JNB"],
    "Mexico": ["MEX"],
    "Buenos Aires": ["EZE"],
    "Chicago": ["ORD"],
    "Genève": ["GVA"],
    "Zurich": ["ZRH"],
    "Vienne": ["VIE"],
    "Bruxelles": ["BRU"],
    "Munich": ["MUC"],
    "Milan": ["MXP", "LIN"],
    "Copenhague": ["CPH"],
    "Moscou": ["SVO", "DME"],
    "Pékin": ["PEK", "PKX"],
}


class AmadeusClient:
    """
    Client Amadeus API — Flight Offers Search
    Inscription gratuite : https://developers.amadeus.com
    Free tier : 2000 requêtes/mois
    """

    AUTH_URL  = "https://test.api.amadeus.com/v1/security/oauth2/token"
    SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id     = client_id
        self.client_secret = client_secret
        self._token        = None
        self._token_expiry = 0

    def _get_token(self) -> str:
        """Récupère ou renouvelle le token OAuth2."""
        if self._token and time.time() < self._token_expiry - 60:
            return self._token

        resp = requests.post(self.AUTH_URL, data={
            "grant_type":    "client_credentials",
            "client_id":     self.client_id,
            "client_secret": self.client_secret,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self._token        = data["access_token"]
        self._token_expiry = time.time() + data["expires_in"]
        return self._token

    def search_flights(
        self,
        origin:         str,           # IATA ex: "CDG"
        destination:    str,           # IATA ex: "JFK"
        departure_date: str,           # "YYYY-MM-DD"
        return_date:    Optional[str] = None,
        adults:         int = 1,
        max_results:    int = 20,
        currency:       str = "EUR",
        non_stop:       bool = False,
    ) -> List[Dict]:
        """
        Recherche de vrais vols via Amadeus.
        Retourne une liste de dicts normalisés.
        """
        token = self._get_token()
        params = {
            "originLocationCode":      origin,
            "destinationLocationCode": destination,
            "departureDate":           departure_date,
            "adults":                  adults,
            "max":                     max_results,
            "currencyCode":            currency,
            "nonStop":                 str(non_stop).lower(),
        }
        if return_date:
            params["returnDate"] = return_date

        resp = requests.get(
            self.SEARCH_URL,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return self._parse_results(data, adults)

    def _parse_results(self, data: dict, adults: int) -> List[Dict]:
        """Parse la réponse Amadeus en format normalisé."""
        results = []
        offers  = data.get("data", [])
        dicts   = data.get("dictionaries", {})
        carriers= dicts.get("carriers", {})
        aircraft= dicts.get("aircraft", {})

        for offer in offers:
            try:
                price_total = float(offer["price"]["grandTotal"])
                price_pp    = float(offer["price"]["total"]) / adults

                for itinerary in offer["itineraries"]:
                    segments  = itinerary["segments"]
                    nb_escales = len(segments) - 1

                    first_seg  = segments[0]
                    last_seg   = segments[-1]

                    dep_iata = first_seg["departure"]["iataCode"]
                    arr_iata = last_seg["arrival"]["iataCode"]
                    dep_time = first_seg["departure"]["at"]
                    arr_time = last_seg["arrival"]["at"]

                    # Durée totale
                    duration_str = itinerary["duration"]  # ex: "PT7H30M"
                    dur_min = self._parse_duration(duration_str)

                    # Compagnie principale
                    carrier_code = first_seg["carrierCode"]
                    carrier_name = carriers.get(carrier_code, carrier_code)

                    # Numéro de vol
                    flight_num = f"{carrier_code}{first_seg['number']}"

                    # Villes d'escale
                    stop_cities = [s["departure"]["iataCode"] for s in segments[1:]]

                    # Classe de cabine
                    cabin = "economy"
                    try:
                        cabin_raw = (offer["travelerPricings"][0]
                                     ["fareDetailsBySegment"][0]
                                     .get("cabin", "ECONOMY"))
                        cabin_map = {
                            "ECONOMY":"economy", "PREMIUM_ECONOMY":"premium",
                            "BUSINESS":"business", "FIRST":"first"
                        }
                        cabin = cabin_map.get(cabin_raw.upper(), "economy")
                    except Exception:
                        pass

                    # Lien de réservation direct
                    book_url = _booking_url(
                        carrier_code, dep_iata, arr_iata,
                        dep_time[:10], None, adults, carrier_name
                    )

                    results.append({
                        "source":        "amadeus_real",
                        "flight_number": flight_num,
                        "airline_iata":  carrier_code,
                        "airline_name":  carrier_name,
                        "origin_iata":   dep_iata,
                        "dest_iata":     arr_iata,
                        "departure":     dep_time,
                        "arrival":       arr_time,
                        "duration_min":  dur_min,
                        "stops":         nb_escales,
                        "stop_cities":   stop_cities,
                        "price":         price_total,
                        "price_pp":      price_pp,
                        "currency":      offer["price"]["currency"],
                        "cabin":         cabin,
                        "seats_left":    offer.get("numberOfBookableSeats"),
                        "deep_link":     book_url,
                        "is_real":       True,
                    })
            except Exception as e:
                continue

        return sorted(results, key=lambda x: x["price"])

    @staticmethod
    def _parse_duration(dur_str: str) -> int:
        """Convertit 'PT7H30M' en minutes."""
        import re
        h = int(re.search(r'(\d+)H', dur_str).group(1)) if 'H' in dur_str else 0
        m = int(re.search(r'(\d+)M', dur_str).group(1)) if 'M' in dur_str else 0
        return h * 60 + m


def _booking_url(code, o, d, dep, ret, pax, name):
    """URL de réservation directe pré-remplie."""
    r = ret or ""
    urls = {
        "AF": f"https://www.airfrance.fr/FR/fr/local/process/accueil/searchresults.do?depCity={o}&destCity={d}&adults={pax}&tripType={'RT' if r else 'OW'}",
        "BA": f"https://www.britishairways.com/travel/fx/public/fr_fr?eId=106005&Oc={o}&Dc={d}&Md={'1' if r else '2'}&Cl=M&Ad={pax}",
        "LH": f"https://www.lufthansa.com/fr/fr/flight-search?origin={o}&destination={d}&outboundDate={dep}{'&returnDate='+r if r else ''}&adults={pax}",
        "EK": f"https://www.emirates.com/fr/french/book/flights/#/outbound/selectflight?OriginCode={o}&DestinationCode={d}&JourneyType={'return' if r else 'oneway'}&Adult={pax}",
        "KL": f"https://www.klm.com/search/fr-fr/{o}/{d}/{dep}{'/' + r if r else ''}/{pax}/0/0/economy",
        "U2": f"https://www.easyjet.com/fr/cheap-flights/{o.lower()}-{d.lower()}",
        "FR": f"https://www.ryanair.com/fr/fr/trip/flights/select?ADTCount={pax}&OriginIata={o}&DestinationIata={d}&DateOut={dep}{'&DateIn='+r+'&isReturn=true' if r else '&isReturn=false'}",
        "TK": f"https://www.turkishairlines.com/fr-fr/booking/flight-booking/?from={o}&to={d}&date={dep}{'&return='+r if r else ''}&adult={pax}",
        "TO": f"https://www.transavia.com/fr-FR/book/flights/?from={o}&to={d}&departure={dep}{'&return='+r if r else ''}&adults={pax}",
        "QR": f"https://www.qatarairways.com/fr-fr/flights.html",
        "EY": f"https://www.etihad.com/fr-fr/fly-etihad/book-a-flight",
        "SQ": f"https://www.singaporeair.com/fr_FR/plan-and-book/flights/",
        "IB": f"https://www.iberia.com/fr/flights/{o}-{d}/?adult={pax}",
        "AT": f"https://www.royalairmaroc.com/fr/reservation/recherche",
        "TP": f"https://www.flytap.com/fr-fr/vols",
        "LX": f"https://www.swiss.com/fr/fr/fly/offers/book",
        "OS": f"https://www.austrian.com/fr/fr/book/flights",
        "AH": f"https://www.airalgerie.dz/reservation",
        "TU": f"https://www.tunisair.com/reservation",
        "MS": f"https://www.egyptair.com/fr/fly/pages/book-a-flight.aspx",
        "ET": f"https://www.ethiopianairlines.com/fr/book/booking",
    }
    return urls.get(code,
        f"https://www.google.com/travel/flights?q=Vols+{o}+vers+{d}&hl=fr&curr=EUR")
