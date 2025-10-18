from typing import Dict, List, Any, Optional, Tuple, Sequence, Iterable, Union

from jobs.google_maps_parser.settings import settings
import asyncio
from math import radians, sin, cos, asin, sqrt
import aiohttp

class GooglePlacesClient:
    NEARBY_URL  = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    PHOTO_URL   = "https://maps.googleapis.com/maps/api/place/photo"

    # поля, которые реально нужны (уменьшает биллинг)
    DETAIL_FIELDS = ",".join([
        "name",
        "formatted_address",
        "geometry",
        "photos",
        "rating",
        "reviews",
        "user_ratings_total",
        "types",
        "website",
        "formatted_phone_number",
        "opening_hours",
        "price_level",
        "editorial_summary",
        "business_status",
        "url",
        "place_id",
    ])

    def __init__(
        self,
        api_key: str,
        *,
        language: str = "ru",
        timeout_s: int = 40,
        concurrency: int = 6,
        nearby_radius_m: int = 120,    # первое узкое окно вокруг точки
        photo_maxwidth: int = 800
    ) -> None:
        self.api_key = api_key
        self.language = language
        self.timeout_s = timeout_s
        self.semaphore = asyncio.Semaphore(concurrency)
        self.nearby_radius_m = nearby_radius_m
        self.photo_maxwidth = photo_maxwidth
        self._session: Optional[aiohttp.ClientSession] = None

    # ---------- контекст-менеджер ----------
    async def __aenter__(self) -> "GooglePlacesClient":
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout_s)
            )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ---------- низкоуровневые утилиты ----------
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # расстояние в метрах
        R = 6371000
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))

    async def _fetch_json(self, url: str, params: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
        assert self._session is not None, "Call within 'async with GooglePlacesClient(...)'"
        async with self.semaphore:
            for i in range(retries):
                async with self._session.get(url, params=params) as r:
                    if r.status == 200:
                        return await r.json()
                    # простые ретраи на 429/5xx
                    if r.status in (429, 500, 502, 503, 504):
                        await asyncio.sleep(0.7 * (i + 1))
                        continue
                    # прочие статусы — без ретраев
                    txt = await r.text()
                    raise RuntimeError(f"HTTP {r.status} {url}: {txt[:200]}")
        return {}

    # ---------- шаг 1: находим place_id только по координатам ----------
    async def _place_id_by_coords(self, lat: float, lon: float) -> Tuple[Optional[str], Optional[Tuple[float, float]]]:
        # попытка №1: Nearby с малым радиусом, без фильтра типа
        params = {
            "location": f"{lat},{lon}",
            "radius": str(self.nearby_radius_m),
            "language": self.language,
            "key": self.api_key,
        }
        data = await self._fetch_json(self.NEARBY_URL, params)
        results = data.get("results", [])

        # попытка №2: ранжирование по дистанции с типами размещения
        if not results:
            for t in ("lodging", "campground", "rv_park"):
                params = {
                    "location": f"{lat},{lon}",
                    "rankby": "distance",
                    "type": t,
                    "language": self.language,
                    "key": self.api_key,
                }
                data = await self._fetch_json(self.NEARBY_URL, params)
                results = data.get("results", [])
                if results:
                    break

        if not results:
            return None, None

        # берём ближайший к исходной точке
        results.sort(key=lambda p: self._haversine(
            lat, lon,
            p.get("geometry", {}).get("location", {}).get("lat", lat),
            p.get("geometry", {}).get("location", {}).get("lng", lon)
        ))
        best = results[0]
        pid = best.get("place_id")
        plat = best.get("geometry", {}).get("location", {}).get("lat")
        plon = best.get("geometry", {}).get("location", {}).get("lng")
        return pid, (plat, plon)

    # ---------- шаг 2: детали ----------
    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        params = {
            "place_id": place_id,
            "fields": self.DETAIL_FIELDS,
            "language": self.language,
            "key": self.api_key,
        }
        data = await self._fetch_json(self.DETAILS_URL, params)
        return data.get("result")

    # ---------- fallback: адрес по координатам ----------
    async def _reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        params = {
            "latlng": f"{lat},{lon}",
            "language": self.language,
            "key": self.api_key,
        }
        data = await self._fetch_json(self.GEOCODE_URL, params)
        res = data.get("results", [])
        return res[0]["formatted_address"] if res else None

    # ---------- классификация под ваши enum-строки ----------
    @staticmethod
    def _classify(types: Optional[Sequence[str]], name: str = "") -> str:
        name_l = (name or "").lower()
        types = list(types or [])
        if "campground" in types or "rv_park" in types or "glamping" in name_l or "глэмп" in name_l:
            if any(k in name_l for k in ("lux", "люкс", "premium", "премиум")):
                return "luxury_glamping"
            return "eco_tourism"
        if "lodging" in types:
            if any(k in name_l for k in ("yurt", "юрта", "юртов")):
                return "ethno_tourism"
            if any(k in name_l for k in ("mountain", "горн", "alpine", "альп")):
                return "mountain_house"
            return "family_guest_house"
        return "family_guest_house"

    def _photo_url(self, photo_reference: str) -> str:
        return (
            f"{self.PHOTO_URL}"
            f"?maxwidth={self.photo_maxwidth}"
            f"&photo_reference={photo_reference}"
            f"&key={self.api_key}"
        )

    # ---------- упаковка в вашу целевую структуру ----------
    def _to_record(
        self,
        details: Dict[str, Any],
        coords_fallback: Optional[Tuple[float, float]],
        *,
        region: Optional[str] = None,
        photos_limit: int = 3,
        reviews_limit: int = 5,
    ) -> Dict[str, Any]:
        gloc = (details.get("geometry") or {}).get("location") or {}
        lat = gloc.get("lat") or (coords_fallback[0] if coords_fallback else None)
        lon = gloc.get("lng") or (coords_fallback[1] if coords_fallback else None)

        photos: List[str] = []
        for p in (details.get("photos") or [])[:photos_limit]:
            ref = p.get("photo_reference")
            if ref:
                photos.append(self._photo_url(ref))

        raw_reviews = details.get("reviews") or []
        schedule = None
        if details.get("opening_hours", {}).get("weekday_text"):
            schedule = details["opening_hours"]["weekday_text"]

        description = (details.get("editorial_summary") or {}).get("overview")
        if not description:
            nm = details.get("name", "")
            addr = details.get("formatted_address", "")
            rt = details.get("rating")
            description = f"{nm} расположен по адресу {addr}." + (f" Рейтинг: {rt}/5." if rt else "")

        types = details.get("types") or []
        category = self._classify(types, details.get("name") or "")

        return {
            # базовые поля, которые вы просили
            "name": details.get("name"),
            "address": details.get("formatted_address"),
            "lat": lat,
            "lon": lon,
            "rating": details.get("rating"),
            "ratings_count": details.get("user_ratings_total"),  # общее число оценок в Google
            "reviews_count": len(raw_reviews[:reviews_limit]),   # это top-N из Details, не общий объём
            "description": description,
            "rubrics": types,
            "schedule": schedule,
            "category": category,

            # доп. поля для вашей модели
            "phone": details.get("formatted_phone_number"),
            "website": details.get("website"),
            "photos": photos,
            "reviews": [
                {
                    "author": r.get("author_name"),
                    "rating": r.get("rating"),
                    "text": r.get("text"),
                    "time": r.get("time"),
                }
                for r in raw_reviews[:reviews_limit]
            ],
            "google_place_id": details.get("place_id"),
            "region": region,
            "data_sources": ["google_places"],
            "google_maps_url": details.get("url"),
        }

    # ---------- публичные методы ----------
    async def enrich_point(
        self,
        lat: float,
        lon: float,
        *,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Обогащает одну точку только по координатам.
        Возвращает словарь с полями под вашу схему.
        """
        pid, best_coords = await self._place_id_by_coords(lat, lon)
        if not pid:
            # ничего рядом не нашли — вернём хотя бы адрес
            addr = await self._reverse_geocode(lat, lon)
            return {
                "name": None,
                "address": addr,
                "lat": lat,
                "lon": lon,
                "rating": None,
                "ratings_count": None,
                "reviews_count": 0,
                "description": None,
                "rubrics": None,
                "schedule": None,
                "category": None,
                "google_place_id": None,
                "region": region,
                "data_sources": [],
            }
        details = await self._get_place_details(pid)
        if not details:
            addr = await self._reverse_geocode(lat, lon)
            return {
                "name": None,
                "address": addr,
                "lat": lat,
                "lon": lon,
                "rating": None,
                "ratings_count": None,
                "reviews_count": 0,
                "description": None,
                "rubrics": None,
                "schedule": None,
                "category": None,
                "google_place_id": pid,
                "region": region,
                "data_sources": ["google_places"],
            }
        return self._to_record(details, best_coords or (lat, lon), region=region)

    async def enrich_many(
        self,
        points: Iterable[Union[Tuple[float, float], Dict[str, Any]]],
        *,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Обогащает список точек.
        points: [(lat, lon), ...] либо [{"lat":..., "lon":...}, ...]
        """
        async def one(p) -> Dict[str, Any]:
            if isinstance(p, dict):
                la, lo = float(p["lat"]), float(p["lon"])
            else:
                la, lo = float(p[0]), float(p[1])
            return await self.enrich_point(la, lo, region=region)

        tasks = [asyncio.create_task(one(p)) for p in points]
        out: List[Dict[str, Any]] = []
        for t in asyncio.as_completed(tasks):
            res = await t
            out.append(res)
        return out

    async def enrich_csv(
        self,
        input_csv: str,
        output_csv: str,
        *,
        lat_col: str = "lat",
        lon_col: str = "lon",
        region: Optional[str] = None
    ) -> int:
        """
        Обогащает CSV с колонками lat, lon и сохраняет результат в output_csv.
        Возвращает число записей в выходном файле.
        """
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas is required for enrich_csv")

        df = pd.read_csv(input_csv)
        rows = df.to_dict(orient="records")

        async def _row_to_point(r):
            return await self.enrich_point(float(r[lat_col]), float(r[lon_col]), region=region)

        tasks = [asyncio.create_task(_row_to_point(r)) for r in rows]
        out: List[Dict[str, Any]] = []
        for t in asyncio.as_completed(tasks):
            res = await t
            out.append(res)

        pd.DataFrame(out).to_csv(output_csv, index=False, encoding="utf-8")
        return len(out)