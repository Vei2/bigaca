import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random
import time
import logging
import re

class WebAccessModule:
    def __init__(self, api_core=None):
        self.api_core = api_core
        self.id = 'web-access-module'
        self.name = 'Модуль Веб-Доступа'
        self.status = {
            'active': True,
            'requests_count': 0,
            'last_query': None,
            'search_engines_used': [],
            'fallback_used': False,
            'blocked_content_count': 0,
            'extremist_blocked': 0,
            'com_blocked': 0
        }
        
        self.extremist_materials = [
            "hizb-ut-tahrir.org", "hts.ru", "hizb.org",
            "tablig.ru", "tablighi-jamaat.org",
            "imaratkavkaz.com", "kavkazcenter.com",
            "quran.com", "quran.ru", "islamhouse.com",
            "jihadology.net", "musavat.com",
            "pravaya.sektor.org.ua", "pravysectornow.com",
            "azov.info", "azov.org.ua",
            "bileta.org", "bookfinder.ru", "bookz.ru",
            "rusfront.org", "rusfront.com",
            "nationandstate.org", "nationandstate.com",
            "white-power.ru", "white-power.org",
            "skinhead.ru", "skinhead.su",
            "stormfront.org", "stormfront.ru",
            "aryanbrotherhood.org", "aryanbrotherhood.ru",
            "sensay-iv.ru", "allatra.ru", "allatra.org",
            "booksite.ru", "booklib.net",
            "ruskline.ru", "rusradicals.org",
            "neo-nazi.ru", "neo-nazi.org",
            "national-socialist.ru", "national-socialist.org",
            "isis.org", "isil.org", "daesh.org",
            "alqaeda.org", "al-qaeda.net",
            "taliban.org", "taliban.net",
            "boko-haram.org", "boko-haram.net"
        ]
        
        self.blocked_com_domains = [
            "facebook.com", "instagram.com", "twitter.com", "telegram.me",
            "tiktok.com", "youtube.com", "pinterest.com", "reddit.com",
            "4pda.to", "forum.ixbt.com", "livelib.ru", "meduza.io",
            "grani.ru", "echo.msk.ru", "novayagazeta.ru", "tvrain.ru",
            "bbc.com", "radiosvoboda.org", "golos-ameriki.ru", "kasparov.ru",
            "polit.ru", "svoboda.org", "mariupol.tv", "ukraina.ru",
            "strana.ua", "ukrinform.ua", "tsn.ua"
        ]
        
        self.allowed_community_sources = [
            "rutube.ru", "dzen.ru", "zen.yandex.ru", "ok.ru",
            "pikabu.ru", "habr.com", "vc.ru", "dtf.ru"
        ]
        
        essential_programming_sites = [
            "github.com", "stackoverflow.com", "gitlab.com", "codeberg.org",
            "mdn.mozilla.org", "docs.python.org", "golang.org", "rust-lang.org",
            "docs.microsoft.com", "developer.apple.com"
        ]
        
        for site in essential_programming_sites:
            if site.endswith('.com') and site in self.blocked_com_domains:
                self.blocked_com_domains.remove(site)
        
        for site in essential_programming_sites:
            if site not in self.allowed_community_sources:
                self.allowed_community_sources.append(site)
        
        russian_programming_sites = [
            "stackoverflow.ru", "sql.ru", "rsdn.org", "cpp-reference.ru",
            "php.ru", "javascript.ru", "pythonworld.ru", "eax.me", "m.habr.com"
        ]
        
        self.trusted_sources = [
            "cyberleninka.ru", "elibrary.ru", "dic.academic.ru", "ru.wikipedia.org",
            "gramota.ru", "philology.ru", "pg.ru", "duma.gov.ru", "council.gov.ru",
            "rg.ru", "pravo.gov.ru", "government.ru", "kremlin.ru",
            "fsb.ru", "svr.gov.ru", "mvd.ru", "mil.ru", "mchs.gov.ru",
            "fso.gov.ru", "rosgvard.gov.ru", "tass.ru", "ria.ru", "interfax.ru",
            "kommersant.ru", "iz.ru", "fontanka.ru", "minzdrav.gov.ru",
            "minfin.gov.ru", "rosstat.gov.ru", "rospotrebnadzor.ru", "fns.gov.ru",
            *self.allowed_community_sources,
            *russian_programming_sites
        ]
        
        self.source_categories = {
            'academic': ["cyberleninka.ru", "elibrary.ru", "dic.academic.ru", "gramota.ru", "philology.ru"],
            'encyclopedia': ["ru.wikipedia.org"],
            'parliamentary': ["pg.ru", "duma.gov.ru", "council.gov.ru"],
            'government_media': ["rg.ru", "pravo.gov.ru", "tass.ru", "ria.ru", "interfax.ru"],
            'executive': ["government.ru", "kremlin.ru", "premier.gov.ru"],
            'security_services': ["fsb.ru", "svr.gov.ru"],
            'law_enforcement': ["mvd.ru", "fso.gov.ru", "rosgvard.gov.ru"],
            'defense': ["mil.ru", "mchs.gov.ru"],
            'official_media': ["kommersant.ru", "iz.ru", "fontanka.ru"],
            'federal_ministries': ["minzdrav.gov.ru", "minfin.gov.ru", "rosstat.gov.ru", "rospotrebnadzor.ru"],
            'community': self.allowed_community_sources,
            'programming': [
                "github.com", "stackoverflow.com", "gitlab.com", "codeberg.org",
                "mdn.mozilla.org", "docs.python.org", "golang.org", "rust-lang.org",
                "docs.microsoft.com", "developer.apple.com", "habr.com", "stackoverflow.ru",
                "sql.ru", "rsdn.org", "cpp-reference.ru", "php.ru", "javascript.ru",
                "pythonworld.ru", "eax.me", "m.habr.com", "vc.ru", "dtf.ru"
            ]
        }
        
        logging.info("💻 СИСТЕМА ПРОГРАММИРОВАНИЯ: Интегрированы ключевые российские и международные ресурсы для разработчиков")
        logging.info(f"✅ Разрешены для поиска: GitHub, StackOverflow, GitLab, Хабр, SQL.ru и другие программистские ресурсы")

    def init(self):
        logging.info(f"🌐 Инициализация {self.name}...")
        logging.warning("🛡️ БЕЗОПАСНЫЙ ПОИСК: Экстремистские материалы и опасные .com домены блокируются, "
                       "но разрешены российские комьюнити (Пикабу, Хабр) и видеохостинги (Рутуб, Дзен)")
        logging.info("🔧 ДОПОЛНЕНИЕ: Система теперь включает полную поддержку программистских ресурсов")
        
        self.api_core.register_analysis_function('web_search', self.web_search, {
            'description': 'Выполняет поиск по официальным российским источникам + разрешённым комьюнити (Пикабу, Хабр, Рутуб) + программистским ресурсам',
            'moduleId': self.id,
            'security_level': 'high',  # Высокий уровень безопасности с разрешёнными исключениями
            'compliance': 'fz-114'     # Соответствие ФЗ "О противодействии экстремистской деятельности"
        })
        logging.info(f"✅ {self.name} готов к работе с балансом безопасности и полезного контента.")

    def is_extremist_content(self, domain, url):
        """Проверка на экстремистский контент по официальным спискам"""
        # Проверка по списку экстремистских материалов
        for extremist_domain in self.extremist_materials:
            if extremist_domain in domain or extremist_domain in url:
                self.status['extremist_blocked'] += 1
                logging.warning(f"☠️ ЭКСТРЕМИСТСКИЙ МАТЕРИАЛ ЗАБЛОКИРОВАН: {domain} ({url})")
                return True
        
        # Проверка по шаблонам (джихад, неонацизм и т.д.)
        extremist_keywords = [
            'jihad', 'terror', 'bomb', 'kill', 'hate', 'нацизм', 'нацист', 
            'фашизм', 'фашист', 'расизм', 'расист', 'white power', 'арийский',
            'экстремизм', 'терроризм', 'ненависть', 'убийство', 'насилие'
        ]
        
        url_lower = url.lower()
        for keyword in extremist_keywords:
            if keyword in url_lower:
                self.status['extremist_blocked'] += 1
                logging.warning(f"☠️ ПОТЕНЦИАЛЬНЫЙ ЭКСТРЕМИСТСКИЙ КОНТЕНТ ЗАБЛОКИРОВАН: {url}")
                return True
        
        return False

    def is_blocked_domain(self, domain):
        """Проверка, является ли домен заблокированным (но с исключениями для разрешённых помоек)"""
        if not domain:
            return False
        
        # 1. Проверка на экстремистские материалы (приоритет)
        if self.is_extremist_content(domain, f"https://{domain}"):
            return True
        
        # 2. Проверка на разрешённые "помойки" (исключения из правил)
        if domain in self.allowed_community_sources or any(domain.endswith(f".{site}") for site in self.allowed_community_sources):
            logging.info(f"✅ РАЗРЕШЁННЫЙ КОМЬЮНИТИ-РЕСУРС: {domain} (исключение из правил)")
            return False
        
        # === ДОПОЛНЕНИЕ: ИСКЛЮЧЕНИЯ ДЛЯ ПРОГРАММИСТСКИХ САЙТОВ ===
        # Явные исключения для ключевых программистских ресурсов
        programming_exceptions = [
            "github.com", "stackoverflow.com", "gitlab.com", 
            "codeberg.org", "mdn.mozilla.org", "docs.python.org"
        ]
        
        if any(exception in domain for exception in programming_exceptions):
            logging.info(f"💻 РАЗРЕШЁННЫЙ ПРОГРАММИСТСКИЙ РЕСУРС: {domain} (исключение из правил)")
            return False
        
        # 3. Проверка на запрещённые .com домены
        if domain.endswith('.com'):
            if any(blocked in domain for blocked in self.blocked_com_domains):
                self.status['com_blocked'] += 1
                logging.warning(f"🗑️ ЗАПРЕЩЁННЫЙ .COM ДОМЕН ЗАБЛОКИРОВАН: {domain}")
                return True
        
        # 4. Проверка по списку других запрещенных доменов
        blocked_socials = ["facebook.com", "instagram.com", "twitter.com", "telegram.me", "tiktok.com", "youtube.com"]
        for blocked in blocked_socials:
            if blocked in domain:
                self.status['blocked_content_count'] += 1
                logging.warning(f"🚫 ЗАПРЕЩЁННАЯ СОЦСЕТЬ ЗАБЛОКИРОВАНА: {domain}")
                return True
        
        return False

    def get_domain_from_url(self, url):
        """Корректное извлечение домена из URL с защитой от запрещенного контента"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # МГНОВЕННАЯ БЛОКИРОВКА запрещенных доменов
            if self.is_blocked_domain(domain):
                return "BLOCKED_ILLEGAL_CONTENT"
            
            return domain
        except Exception as e:
            logging.error(f"Ошибка при парсинге URL {url}: {str(e)}")
            return None

    def is_trusted_source(self, url):
        """Проверка доверенных источников с разрешёнными комьюнти"""
        domain = self.get_domain_from_url(url)
        
        # Если домен заблокирован как нелегальный
        if domain == "BLOCKED_ILLEGAL_CONTENT":
            return False, None, 'illegal'
        
        if not domain:
            return False, None, None
        
        # Поиск по категориям доверенных источников (включая комьюнити и программистские ресурсы)
        for category, sites in self.source_categories.items():
            for site in sites:
                if domain == site or domain.endswith('.' + site):
                    return True, site, category
        
        # Все остальные домены считаются ненадежными
        logging.warning(f"⚠️ НЕДОВЕРЕННЫЙ ИСТОЧНИК: {domain}")
        return False, None, 'untrusted'

    # Конфигурация поисковых систем (Google, Яндекс, Bing) остаётся без изменений
    search_engines = {
        'google': {
            'url': 'https://www.google.com/search?q={}',
            'selectors': {
                'result_container': ['.g', '.tF2Cxc', '.MjjYud'],
                'title': ['h3', '.LC20lb', '.yKMVIe'],
                'url': ['a', '.yuRUbf a'],
                'snippet': ['.VwiC3b', '.IsZvec', '.lyLwlc']
            }
        },
        'yandex': {
            'url': 'https://yandex.ru/search/?text={}',
            'selectors': {
                'result_container': ['.serp-item', '.Organic', '.serp-item_link'],
                'title': ['.organic__url-text', '.Link_theme_normal', '.Link_link_theme_inner-path'],
                'url': ['.link', '.OrganicTitle-Link'],
                'snippet': ['.text', '.text__normal', '.OrganicText']
            }
        },
        'bing': {
            'url': 'https://www.bing.com/search?q={}',
            'selectors': {
                'result_container': ['.b_algo', '.sa_wr', '.b_algo_group'],
                'title': ['h2', '.b_title h2'],
                'url': ['cite', '.b_attribution cite', '.b_algo h2 a'],
                'snippet': ['.b_caption', '.b_snippet', '.b_algo p']
            }
        }
    }

    def search_engine_fallback(self, query, search_type='official', max_results=8):
        """Поиск с фильтрацией запрещенного контента, но с разрешёнными комьюнти"""
        results = []
        engines_tried = []
        
        engine_names = list(self.search_engines.keys())
        random.shuffle(engine_names)
        
        for engine_name in engine_names:
            if len(results) >= max_results:
                break
                
            engine_config = self.search_engines[engine_name]
            engines_tried.append(engine_name)
            
            try:
                # Формируем безопасный запрос с исключением запрещённых доменов
                safe_query = query
                
                # Исключаем известные запрещенные ресурсы
                for extremist in self.extremist_materials:
                    safe_query += f" -site:{extremist}"
                
                # Исключаем опасные соцсети
                blocked_socials = ["facebook.com", "instagram.com", "twitter.com", "telegram.me", "tiktok.com", "youtube.com"]
                for social in blocked_socials:
                    safe_query += f" -site:{social}"
                
                # Добавляем приоритет для разрешённых комьюнти при fallback
                if search_type == 'fallback':
                    community_filter = " OR ".join([f"site:{site}" for site in self.allowed_community_sources])
                    safe_query = f"({query}) ({community_filter})"
                
                search_url = engine_config['url'].format(safe_query)
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
                ]
                
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                }
                
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    engine_results = self.parse_search_results(soup, engine_config, engine_name, search_type)
                    results.extend(engine_results)
                    
                    if len(engine_names) > 1:
                        time.sleep(random.uniform(0.5, 1.5))
                        
            except Exception as e:
                logging.warning(f"⚠️ Ошибка при поиске в {engine_name}: {str(e)}")
                continue
        
        return results, engines_tried

    def parse_search_results(self, soup, engine_config, engine_name, search_type='official'):
        """Парсинг результатов с сохранением разрешённых комьюнти"""
        results = []
        
        # Получаем контейнеры с результатами
        result_containers = []
        for selector in engine_config['selectors']['result_container']:
            try:
                containers = soup.select(selector)
                if containers:
                    result_containers = containers
                    break
            except:
                continue
        
        if not result_containers:
            logging.warning(f"⚠️ Не найдены контейнеры результатов для {engine_name}")
            return results
        
        for container in result_containers[:15]:
            try:
                # Ищем заголовок
                title_element = None
                for selector in engine_config['selectors']['title']:
                    try:
                        title_element = container.select_one(selector)
                        if title_element and title_element.text.strip():
                            break
                    except:
                        continue
                
                # Ищем URL
                url_element = None
                for selector in engine_config['selectors']['url']:
                    try:
                        url_element = container.select_one(selector)
                        if url_element and url_element.get('href'):
                            break
                    except:
                        continue
                
                # Ищем сниппет
                snippet_element = None
                for selector in engine_config['selectors']['snippet']:
                    try:
                        snippet_element = container.select_one(selector)
                        if snippet_element and snippet_element.text.strip():
                            break
                    except:
                        continue
                
                if title_element and url_element:
                    title_text = title_element.text.strip()
                    url_href = url_element.get('href', '').strip()
                    
                    # Обработка относительных URL
                    if url_href.startswith('/'):
                        if 'google' in engine_name:
                            url_href = f"https://www.google.com{url_href}"
                        elif 'yandex' in engine_name:
                            url_href = f"https://yandex.ru{url_href}"
                    
                    snippet_text = snippet_element.text.strip() if snippet_element else "Описание отсутствует"
                    
                    # Проверка на экстремистский контент в URL
                    if self.is_extremist_content("", url_href):
                        continue
                    
                    # Проверка на доверенный источник
                    is_trusted, source_site, category = self.is_trusted_source(url_href)
                    
                    # Пропускаем только явно запрещённые источники
                    if not is_trusted and category == 'illegal':
                        continue
                    
                    result = {
                        'title': title_text,
                        'url': url_href,
                        'snippet': snippet_text[:300],
                        'source': source_site if source_site else engine_name,
                        'category': category if category else 'other',
                        'is_trusted': is_trusted,
                        'search_engine': engine_name,
                        'quality_reason': '✅ Разрешённый источник' if is_trusted else '⚠️ Общедоступный источник'
                    }
                    
                    results.append(result)
                    
                    if len(results) >= 15:
                        break
                    
            except Exception as e:
                continue
        
        return results

    def web_search(self, query, analysis=None, context=None):
        self.status['requests_count'] += 1
        self.status['last_query'] = query
        self.status['fallback_used'] = False
        
        initial_blocked_count = self.status['blocked_content_count']
        initial_extremist_count = self.status['extremist_blocked']
        initial_com_count = self.status['com_blocked']
        
        # Формируем приоритетный запрос для официальных источников
        trusted_sites = []
        for sites in self.source_categories.values():
            trusted_sites.extend(sites)
        
        # Создаём фильтр для официальных источников + разрешённых комьюнти + программистских ресурсов
        trusted_filter = " OR ".join([f"site:{site}" for site in trusted_sites])
        official_query = f"({query}) ({trusted_filter})"
        
        logging.info(f"🔍 ПОИСК ПО ОФИЦИАЛЬНЫМ ИСТОЧНИКАМ + РАЗРЕШЁННЫМ КОМЬЮНИТИ + ПРОГРАММИСТСКИМ РЕСУРСАМ")
        logging.info(f"✅ Разрешённые комьюнити: Пикабу, Хабр, VC.ru, Дзен, Рутуб")
        logging.info(f"💻 Разрешённые программистские ресурсы: GitHub, StackOverflow, GitLab, Хабр, SQL.ru")
        logging.warning(f"🚫 Запрещены: экстремистские материалы, Facebook, Instagram, Telegram, TikTok")
        
        try:
            # Сначала ищем по официальным источникам
            official_results, engines_used = self.search_engine_fallback(official_query, search_type='official', max_results=10)
            self.status['search_engines_used'] = engines_used
            
            # Если официальных результатов недостаточно (<3), добавляем комьюнити
            if len(official_results) < 3:
                logging.warning(f"⚠️ Недостаточно официальных результатов ({len(official_results)}/3), "
                              f"добавляю разрешённые комьюнити (Пикабу, Хабр, Дзен) и программистские ресурсы")
                self.status['fallback_used'] = True
                
                # Повторный поиск с акцентом на комьюнити
                community_results, _ = self.search_engine_fallback(query, search_type='fallback', max_results=8)
                
                # Объединяем результаты: сначала официальные, потом комьюнити
                final_results = official_results[:3] + community_results[:2]
            else:
                final_results = official_results[:5]
            
            # Формируем категоризацию для вывода
            categorized_results = {}
            for result in final_results:
                category = result['category']
                if category not in categorized_results:
                    categorized_results[category] = []
                categorized_results[category].append(result)
            
            # Статистика блокировок
            total_blocked = (self.status['blocked_content_count'] - initial_blocked_count) + \
                          (self.status['extremist_blocked'] - initial_extremist_count) + \
                          (self.status['com_blocked'] - initial_com_count)
            
            # Формируем итоговый контент
            content = f"✅ НАЙДЕНО {len(final_results)} ИСТОЧНИКОВ (заблокировано: {total_blocked})\n\n"
            
            # Группируем результаты по категориям для лучшей читаемости
            for category, results in categorized_results.items():
                content += f"\n{self.get_category_emoji(category)} {self.get_category_name(category)}:\n"
                for r in results:
                    content += f"📄 {r['title']}\n"
                    content += f"🌐 {r['url']}\n"
                    content += f"📝 {r['snippet']}\n\n"
            
            # Добавляем информацию о блокировках
            if total_blocked > 0:
                content += f"\n\n🛡️ СИСТЕМА БЕЗОПАСНОСТИ: Заблокировано {total_blocked} ресурсов:\n" \
                          f"- Экстремистских материалов: {self.status['extremist_blocked'] - initial_extremist_count}\n" \
                          f"- Запрещённых соцсетей: {self.status['blocked_content_count'] - initial_blocked_count}\n" \
                          f"- Опасных .com доменов: {self.status['com_blocked'] - initial_com_count}"
            
            # Добавляем предупреждение для комьюнити
            community_results = [r for r in final_results if r['category'] == 'community']
            if community_results:
                content += "\n\n💡 ИНФОРМАЦИОННОЕ СООБЩЕНИЕ: Некоторые результаты получены из разрешённых комьюнити " \
                          "(Пикабу, Хабр, Дзен). Эти источники проходят базовую фильтрацию, но могут содержать " \
                          "мнения пользователей, не совпадающие с официальной позицией."
            
            # Добавляем информацию о программистских ресурсах
            programming_results = [r for r in final_results if r['category'] == 'programming']
            if programming_results:
                content += "\n\n💻 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ: Найдены ресурсы для программистов и разработчиков. " \
                          "Эти источники содержат техническую документацию, примеры кода и решения проблем."
            
            return {
                'success': True,
                'query': query,
                'data': content,
                'results': final_results,
                'stats': {
                    'official_count': len([r for r in final_results if r['category'] not in ['community', 'programming']]),
                    'community_count': len(community_results),
                    'programming_count': len(programming_results),
                    'blocked_total': total_blocked,
                    'fallback_used': self.status['fallback_used'],
                    'search_source': 'official_with_community_and_programming'
                },
                'source': 'russian_official_and_community_and_programming'
            }
            
        except Exception as e:
            logging.error(f"❌ Критическая ошибка в веб-поиске: {str(e)}")
            return {
                'success': False,
                'error': f"Системная ошибка поиска: {str(e)}",
                'source': 'russian_official_and_community_and_programming'
            }

    def get_category_emoji(self, category):
        """Возвращает эмодзи для категории источника"""
        emojis = {
            'academic': '📚',
            'encyclopedia': '📖',
            'parliamentary': '🏛️',
            'government_media': '📰',
            'executive': '🏛️',
            'security_services': '🚨',
            'law_enforcement': '👮',
            'defense': '🛡️',
            'official_media': '🗞️',
            'federal_ministries': '📊',
            'social_services': '👥',
            'registry_services': '📋',
            'community': '💬',  # Эмодзи для разрешённых комьюнити
            'programming': '💻', # Эмодзи для программистских ресурсов
            'illegal': '☠️',
            'untrusted': '❌',
            'other': '🌐'
        }
        return emojis.get(category, '📄')

    def get_category_name(self, category):
        """Возвращает человекочитаемое название категории"""
        names = {
            'academic': 'АКАДЕМИЧЕСКИЙ ИСТОЧНИК',
            'encyclopedia': 'ЭНЦИКЛОПЕДИЯ',
            'parliamentary': 'ПАРЛАМЕНТСКИЙ РЕСУРС',
            'government_media': 'ПРАВИТЕЛЬСТВЕННОЕ СМИ',
            'executive': 'ИСПОЛНИТЕЛЬНАЯ ВЛАСТЬ',
            'security_services': 'СПЕЦСЛУЖБА',
            'law_enforcement': 'ПРАВООХРАНИТЕЛЬНЫЙ ОРГАН',
            'defense': 'ОБОРОННЫЙ РЕСУРС',
            'official_media': 'ОФИЦИАЛЬНОЕ СМИ РФ',
            'federal_ministries': 'ФЕДЕРАЛЬНОЕ МИНИСТЕРСТВО',
            'social_services': 'СОЦИАЛЬНЫЕ СЛУЖБЫ',
            'registry_services': 'РЕЕСТРОВЫЕ СЛУЖБЫ',
            'community': 'РАЗРЕШЁННОЕ СООБЩЕСТВО',
            'programming': 'ПРОГРАММИСТСКИЙ РЕСУРС', # Название для программистских сайтов
            'illegal': 'ЗАПРЕЩЕННЫЙ ИСТОЧНИК',
            'untrusted': 'НЕНАДЕЖНЫЙ ИСТОЧНИК',
            'other': 'ДРУГОЙ ИСТОЧНИК'
        }
        return names.get(category, category.upper())

def register(api_core):
    module = WebAccessModule(api_core)
    module.init()
    return module
