import time
import requests
from typing import Dict, Any, List, Optional

# In-memory cache for search queries: query -> { 'timestamp': float, 'data': list }
SEARCH_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes cache

# High-fidelity curated catalog of authentic anime metadata
FALLBACK_CATALOG = [
    {
        'external_id': 42310,
        'title': 'Cyberpunk: Edgerunners',
        'title_english': 'Cyberpunk: Edgerunners',
        'poster_url': 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx120377-ayZPoxiWt4Li.jpg',
        'mal_rating': 8.50,
        'episodes': 10,
        'year': 2022,
        'genres': 'Action, Sci-Fi, Psychological, Drama',
        'synopsis': 'A street kid trying to survive in a technology and body modification-obsessed city of the future.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 20,
        'title': 'Naruto',
        'title_english': 'Naruto',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/13/17405l.jpg',
        'mal_rating': 7.99,
        'episodes': 220,
        'year': 2002,
        'genres': 'Action, Adventure, Fantasy',
        'synopsis': 'Moments prior to Naruto Uzumaki\'s birth, a huge demon known as the Kyuubi, the Nine-Tailed Fox, attacked Konohagakure, the Hidden Leaf Village.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 1735,
        'title': 'Naruto: Shippuuden',
        'title_english': 'Naruto Shippuden',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1565/111305l.jpg',
        'mal_rating': 8.27,
        'episodes': 500,
        'year': 2007,
        'genres': 'Action, Adventure, Fantasy',
        'synopsis': 'It has been two and a half years since Naruto Uzumaki left Konohagakure to train with Jiraiya.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 16498,
        'title': 'Attack on Titan',
        'title_english': 'Attack on Titan',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/10/47347l.jpg',
        'mal_rating': 8.55,
        'episodes': 25,
        'year': 2013,
        'genres': 'Action, Drama, Suspense',
        'synopsis': 'Centuries ago, mankind was slaughtered to near extinction by monstrous humanoid creatures called Titans.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 52991,
        'title': 'Frieren: Beyond Journey\'s End',
        'title_english': 'Frieren: Beyond Journey\'s End',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1015/138062l.jpg',
        'mal_rating': 9.32,
        'episodes': 28,
        'year': 2023,
        'genres': 'Adventure, Drama, Fantasy',
        'synopsis': 'During their decade-long quest to defeat the Demon King, the members of the hero\'s party forge profound bonds.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 40748,
        'title': 'Jujutsu Kaisen',
        'title_english': 'Jujutsu Kaisen',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1171/109222l.jpg',
        'mal_rating': 8.61,
        'episodes': 24,
        'year': 2020,
        'genres': 'Action, Fantasy',
        'synopsis': 'High school student Yuuji Itadori swallows a cursed talisman and becomes host to a powerful curse.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 38000,
        'title': 'Demon Slayer: Kimetsu no Yaiba',
        'title_english': 'Demon Slayer: Kimetsu no Yaiba',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1286/99889l.jpg',
        'mal_rating': 8.48,
        'episodes': 26,
        'year': 2019,
        'genres': 'Action, Fantasy',
        'synopsis': 'Tanjirou Kamado sets out on a perilous journey to become a demon slayer and avenge his family.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 269,
        'title': 'Bleach',
        'title_english': 'Bleach',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/3/40451l.jpg',
        'mal_rating': 7.94,
        'episodes': 366,
        'year': 2004,
        'genres': 'Action, Adventure, Supernatural',
        'synopsis': 'Ichigo Kurosaki is an ordinary high schooler until his family is attacked by a Hollow, a corrupt spirit.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 21,
        'title': 'One Piece',
        'title_english': 'One Piece',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1244/138851l.jpg',
        'mal_rating': 8.73,
        'episodes': 0,
        'year': 1999,
        'genres': 'Action, Adventure, Fantasy',
        'synopsis': 'Monkey D. Luffy embarks on a grand adventure across the Grand Line to find the legendary One Piece treasure.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 52299,
        'title': 'Solo Leveling',
        'title_english': 'Solo Leveling',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1598/141566l.jpg',
        'mal_rating': 8.27,
        'episodes': 12,
        'year': 2024,
        'genres': 'Action, Fantasy',
        'synopsis': 'Known as the weakest hunter of all mankind, Sung Jinwoo encounters a mysterious quest window and starts leveling up.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 1535,
        'title': 'Death Note',
        'title_english': 'Death Note',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1079/138100l.jpg',
        'mal_rating': 8.62,
        'episodes': 37,
        'year': 2006,
        'genres': 'Supernatural, Suspense',
        'synopsis': 'A brilliant high school student discovers a supernatural notebook that grants the ability to kill anyone whose name is written in it.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 5114,
        'title': 'Fullmetal Alchemist: Brotherhood',
        'title_english': 'Fullmetal Alchemist: Brotherhood',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1208/94745l.jpg',
        'mal_rating': 9.10,
        'episodes': 64,
        'year': 2009,
        'genres': 'Action, Adventure, Drama, Fantasy',
        'synopsis': 'Two brothers search for the Philosopher\'s Stone after an attempt at human alchemy goes terribly wrong.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 9253,
        'title': 'Steins;Gate',
        'title_english': 'Steins;Gate',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1935/127974l.jpg',
        'mal_rating': 9.07,
        'episodes': 24,
        'year': 2011,
        'genres': 'Drama, Sci-Fi, Suspense',
        'synopsis': 'A self-proclaimed mad scientist invents a device capable of sending messages into the past.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 44511,
        'title': 'Chainsaw Man',
        'title_english': 'Chainsaw Man',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1806/126216l.jpg',
        'mal_rating': 8.46,
        'episodes': 12,
        'year': 2022,
        'genres': 'Action, Fantasy',
        'synopsis': 'Denji is living a normal life, paying off his deceased father\'s debt to the yakuza by harvesting devil corpses with Pochita.',
        'external_source': 'MyAnimeList'
    },
    {
        'external_id': 31964,
        'title': 'Boku no Hero Academia',
        'title_english': 'My Hero Academia',
        'poster_url': 'https://cdn.myanimelist.net/images/anime/10/78745l.jpg',
        'mal_rating': 7.85,
        'episodes': 13,
        'year': 2016,
        'genres': 'Action',
        'synopsis': 'A quirkless boy named Izuku Midoriya dreams of becoming the world\'s greatest hero.',
        'external_source': 'MyAnimeList'
    }
]


class JikanService:
    """
    Robust anime metadata service.
    First attempts Jikan API (MyAnimeList), then seamlessly falls back to AniList GraphQL
    and local catalog to ensure live posters, total episode counts, and community scores
    are reliably returned regardless of regional network blocks.
    """

    JIKAN_BASE_URL = "https://api.jikan.moe/v4/anime"
    ANILIST_URL = "https://graphql.anilist.co"

    @classmethod
    def search(cls, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search anime titles with caching and resilient fallback.
        Returns a dict with { 'success': bool, 'data': list, 'source': str, 'query': str }.
        """
        clean_q = (query or '').strip()
        if not clean_q:
            return {
                'success': False,
                'error': 'Search query parameter "q" cannot be empty.',
                'data': []
            }

        cache_key = f"{clean_q.lower()}_{limit}"
        now = time.time()

        # 1. Check in-memory cache
        if cache_key in SEARCH_CACHE:
            cached = SEARCH_CACHE[cache_key]
            if now - cached['timestamp'] < CACHE_TTL_SECONDS:
                return {
                    'success': True,
                    'query': clean_q,
                    'count': len(cached['data']),
                    'data': cached['data'],
                    'source': cached.get('source', 'cache')
                }

        # 2. Try Jikan API (MyAnimeList)
        items = cls._try_jikan(clean_q, limit)
        source = 'jikan'

        # 3. If Jikan fails/times out, try AniList GraphQL (Cloudflare hosted, global uptime)
        if not items:
            items = cls._try_anilist(clean_q, limit)
            source = 'anilist'

        # 4. If still no items, check local fallback catalog
        if not items:
            items = cls._search_fallback(clean_q, limit)
            source = 'fallback'

        if items:
            SEARCH_CACHE[cache_key] = {
                'timestamp': now,
                'data': items,
                'source': source
            }
            return {
                'success': True,
                'query': clean_q,
                'count': len(items),
                'data': items,
                'source': source
            }

        return {
            'success': False,
            'error': f'No anime found matching "{clean_q}".',
            'data': []
        }

    @classmethod
    def fetch_single_metadata(cls, title: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the best matching metadata record for a single anime title.
        Used to auto-populate missing posters, episode counts, or community ratings.
        """
        res = cls.search(title, limit=1)
        if res.get('success') and res.get('data'):
            return res['data'][0]
        return None

    @classmethod
    def _try_jikan(cls, query: str, limit: int) -> List[Dict[str, Any]]:
        headers = {
            'User-Agent': 'AniTrack-Watchlist/1.0',
            'Accept': 'application/json'
        }
        params = {'q': query, 'limit': limit, 'sfw': 'true'}
        try:
            resp = requests.get(cls.JIKAN_BASE_URL, params=params, headers=headers, timeout=1.8)
            if resp.status_code == 200:
                raw_items = resp.json().get('data', [])
                return cls._normalize_jikan_items(raw_items)
        except Exception:
            pass
        return []

    @classmethod
    def _try_anilist(cls, query: str, limit: int) -> List[Dict[str, Any]]:
        gql_query = """
        query ($search: String, $limit: Int) {
            Page(perPage: $limit) {
                media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
                    id
                    idMal
                    title { romaji english native }
                    episodes
                    averageScore
                    coverImage { extraLarge large medium }
                    seasonYear
                    genres
                    description
                }
            }
        }
        """
        try:
            resp = requests.post(
                cls.ANILIST_URL,
                json={'query': gql_query, 'variables': {'search': query, 'limit': limit}},
                timeout=3.0
            )
            if resp.status_code == 200:
                media_list = resp.json().get('data', {}).get('Page', {}).get('media', [])
                results = []
                for m in media_list:
                    # Score converted to 10-point scale
                    raw_score = m.get('averageScore')
                    mal_score = round(raw_score / 10.0, 2) if raw_score is not None else None

                    poster = (m.get('coverImage', {}).get('extraLarge') or 
                              m.get('coverImage', {}).get('large') or 
                              m.get('coverImage', {}).get('medium'))

                    titles = m.get('title', {})
                    display_title = titles.get('english') or titles.get('romaji') or 'Unknown Title'

                    results.append({
                        'external_id': m.get('idMal') or m.get('id'),
                        'title': display_title,
                        'title_english': titles.get('english'),
                        'poster_url': poster,
                        'mal_rating': mal_score,
                        'episodes': m.get('episodes') or 0,
                        'year': m.get('seasonYear'),
                        'genres': ', '.join(m.get('genres', [])),
                        'synopsis': (m.get('description') or '').replace('<br>', ' ').replace('<i>', '').replace('</i>', '')[:300],
                        'external_source': 'MyAnimeList'
                    })
                return results
        except Exception:
            pass
        return []

    @staticmethod
    def _normalize_jikan_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in raw_items:
            images = item.get('images', {})
            jpg = images.get('jpg', {})
            poster = jpg.get('large_image_url') or jpg.get('image_url') or None

            year = item.get('year')
            if not year:
                aired_from = item.get('aired', {}).get('from')
                if aired_from and len(aired_from) >= 4:
                    try:
                        year = int(aired_from[:4])
                    except ValueError:
                        year = None

            genre_names = [g.get('name') for g in item.get('genres', []) if g.get('name')]

            results.append({
                'external_id': item.get('mal_id'),
                'title': item.get('title') or 'Unknown Title',
                'title_english': item.get('title_english'),
                'poster_url': poster,
                'mal_rating': float(item.get('score')) if item.get('score') is not None else None,
                'episodes': item.get('episodes') or 0,
                'year': year,
                'genres': ', '.join(genre_names),
                'synopsis': item.get('synopsis') or '',
                'external_source': 'MyAnimeList'
            })
        return results

    @staticmethod
    def _search_fallback(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        matched = []
        for item in FALLBACK_CATALOG:
            title = item.get('title', '').lower()
            title_en = item.get('title_english', '').lower()
            genres = item.get('genres', '').lower()

            if q in title or q in title_en or q in genres:
                matched.append(item)
                if len(matched) >= limit:
                    break
        return matched
