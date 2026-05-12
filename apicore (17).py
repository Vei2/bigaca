#!/usr/bin/env python3
"""
APICore - Unified Flask API server for UNIS system.
Merges logic from multiple APICore versions and generation modules.

This system acts as a central intelligence hub (Genesis) capable of generating 
and managing other system components (UNIS, Plaza, Pia, etc.).

WARNING: This file is intentionally large to contain all necessary templates 
and logic for the self-replicating system architecture.
"""

import os
import sys
import json
import logging
import datetime
import random
import glob
import importlib.util
import subprocess
import uuid
import time
import threading
import re
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_GEN_DIR = os.path.join(BASE_DIR, "generated_modules")
DEFAULT_UPLOAD_DIR = os.path.join(BASE_DIR, "absorbed_modules")

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def load_settings():
    """Load settings from file"""
    default_settings = {
        "generated_modules_dir": DEFAULT_GEN_DIR,
        "absorbed_modules_dir": DEFAULT_UPLOAD_DIR,
        "auto_package_on_absorb": False,
        "theme": "dark"
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
                default_settings.update(saved)
        except:
            pass
    return default_settings

def save_settings(settings):
    """Save settings to file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

SETTINGS = load_settings()

GEN_MODULES_DIR = SETTINGS.get("generated_modules_dir", DEFAULT_GEN_DIR)
os.makedirs(GEN_MODULES_DIR, exist_ok=True)

UPLOAD_DIR = SETTINGS.get("absorbed_modules_dir", DEFAULT_UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(DATA_DIR, "system.log"))
    ]
)
logger = logging.getLogger("APICORE_GENESIS")

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ==========================================
# FILE UPLOAD CONFIGURATION
# ==========================================

ALLOWED_EXTENSIONS = {'py', 'js', 'json', 'txt', 'md', 'yaml', 'yml', 'sh', 'bat', 'sql'}
BLOCKED_EXTENSIONS = {'html', 'htm', 'css', 'scss', 'sass', 'less', 'tsx', 'jsx', 'vue', 'svelte'}

def allowed_file(filename):
    """Check if file is allowed for absorption (not a web file)"""
    if '.' not in filename:
        return True
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        return False
    return True

# ==========================================
# CONSTANTS & TEMPLATES
# ==========================================

SYSTEM_ID = str(uuid.uuid4())
STARTUP_TIME = datetime.datetime.now().isoformat()

TEMPLATES = {
    "intelligent_core": """
import logging
import sys
import os
import json
import datetime

class IntelligentCore:
    def __init__(self, unis_core=None):
        self.unis_core = unis_core
        self.plaza = None
        self.id = "IC-" + os.urandom(4).hex()
        self.logger = logging.getLogger(f"IntelligentCore_{self.id}")
        self._init_dependencies()
        
    def _init_dependencies(self):
        try:
            from plaza import Plaza
            self.plaza = Plaza(parent=self)
            print(f"✅ IntelligentCore: Absorbed Plaza", file=sys.stderr)
        except ImportError:
            print(f"❌ IntelligentCore: Plaza not available", file=sys.stderr)
            self.plaza = None

    def process_request(self, request_data):
        self.logger.info(f"Processing request: {request_data}")
        if self.plaza:
            result = self.plaza.execute_command(request_data)
            return {
                'component': 'IntelligentCore',
                'id': self.id,
                'status': 'processed',
                'downstream_result': result
            }
        return {
            'component': 'IntelligentCore',
            'error': 'Plaza not initialized',
            'status': 'failed'
        }

    def get_status(self):
        return {
            'id': self.id,
            'plaza_connected': self.plaza is not None,
            'timestamp': datetime.datetime.now().isoformat()
        }
""",
    "unis": """
import uuid
import datetime
import sys
import os
import logging

class UNIS:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.name = "UNIS_NODE_" + self.id[:8]
        self.core = None
        self.logger = logging.getLogger("UNIS")
        self._init_dependencies()
        
    def _init_dependencies(self):
        try:
            from intelligent_core import IntelligentCore
            self.core = IntelligentCore(unis_core=self)
            print(f"✅ UNIS: Absorbed IntelligentCore", file=sys.stderr)
        except ImportError:
            print(f"❌ UNIS: IntelligentCore not available", file=sys.stderr)
            self.core = None

    def process_query(self, query):
        self.logger.info(f"Received query: {query}")
        return self.process_request({'input': query, 'source': 'user_query'})

    def process_request(self, query_data):
        start_time = datetime.datetime.now()
        if self.core:
            result = self.core.process_request(query_data)
            duration = (datetime.datetime.now() - start_time).total_seconds()
            return {
                'component': 'UNIS',
                'node_id': self.id,
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'downstream_result': result
            }
        return {'error': 'Core not initialized'}

    def system_check(self):
        return {
            'id': self.id,
            'core_status': self.core.get_status() if self.core else 'missing',
            'uptime': 'unknown'
        }
""",
    "plaza": """
import os
import sys
import json
import subprocess
import time

class Plaza:
    def __init__(self, parent=None):
        self.id = 'plaza'
        self.parent = parent
        self.pia_code = ""
        self.pia_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pia.js")
        self._load_pia()
        
    def _load_pia(self):
        if os.path.exists(self.pia_path):
            try:
                with open(self.pia_path, 'r', encoding='utf-8') as f:
                    self.pia_code = f.read()
                print(f"✅ Plaza: Absorbed pia.js", file=sys.stderr)
            except Exception as e:
                print(f"❌ Plaza: Failed to absorb pia.js: {e}", file=sys.stderr)
        else:
            print(f"❌ Plaza: pia.js not found at {self.pia_path}", file=sys.stderr)

    def execute_command(self, command_data):
        if not self.pia_code:
            return {'success': False, 'error': 'pia.js code not loaded'}
        try:
            cmd_json = json.dumps(command_data)
            process = subprocess.run(
                ['node', self.pia_path, cmd_json],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = {'component': self.id, 'status': 'executed'}
            if process.returncode != 0:
                output['error'] = process.stderr
                output['raw_stdout'] = process.stdout
                return output
            lines = process.stdout.strip().split('\\n')
            json_result = None
            for line in reversed(lines):
                try:
                    if line.strip().startswith('{'):
                        json_result = json.loads(line)
                        break
                except json.JSONDecodeError:
                    continue
            if json_result:
                output.update(json_result)
            else:
                output['raw_output'] = process.stdout
            return output
        except subprocess.TimeoutExpired:
            return {'error': 'Execution timed out', 'component': self.id}
        except Exception as e:
            return {'error': str(e), 'component': self.id, 'exception_type': type(e).__name__}
""",
    "pia": """// pia.js
const fs = require('fs');
const path = require('path');
const __dirname_local = __dirname || path.dirname(process.argv[1]);

function findFileInsensitive(dir, filename) {
  try {
    const files = fs.readdirSync(dir);
    const target = filename.toLowerCase();
    for (const file of files) {
      if (file.toLowerCase() === target) return path.join(dir, file);
    }
  } catch (e) { console.error(e); }
  return null;
}

class PiCore {
  constructor() {
    this.army = null;
    this.unplaza = null;
    this.plasa = null;
    this.id = 'PIA-' + Math.random().toString(36).substr(2, 6).toUpperCase();
    console.log(`🧠 PiCore Initialized [${this.id}]`);
    this.absorbDependencies();
  }

  absorbDependencies() {
    const armyPath = findFileInsensitive(__dirname_local, 'army.js');
    if (armyPath) {
      try {
        this.army = require(armyPath);
        console.log('[Pia] ✅ Absorbed Army');
        if (this.army && this.army.absorbUnplaza) {
            this.unplaza = this.army.absorbUnplaza(__dirname_local);
            if (this.unplaza) console.log('[Pia] ✅ Absorbed Unplaza via Army');
        }
        if (this.unplaza && this.unplaza.absorbPlasa) {
            this.plasa = this.unplaza.absorbPlasa(__dirname_local);
            if (this.plasa) console.log('[Pia] ✅ Absorbed Plasa via Unplaza');
        }
      } catch (e) { console.error('[Pia] Failed to load dependencies:', e); }
    }
  }

  execute(command) {
    const result = {
       input: command,
       pia_id: this.id,
       timestamp: new Date().toISOString(),
       absorption_chain: {
        pia: true,
        army: !!this.army,
        unplaza: !!this.unplaza,
        plasa: !!this.plasa
      }
    };
    if (this.army && typeof this.army.executeMission === 'function') {
      result.mission_result = this.army.executeMission(command.input || 'Default Mission');
    } else {
      result.error = "Army not available to execute mission";
    }
    return result;
  }
}

if (process.argv[2]) {
  const core = new PiCore();
  try {
    const command = JSON.parse(process.argv[2]);
    const result = core.execute(command);
    console.log(JSON.stringify(result));
  } catch (e) { 
    console.error('Execution error:', e);
    console.log(JSON.stringify({ error: e.message }));
  }
} else {
  module.exports = new PiCore();
}
""",
    "army_core": """// army.js
const fs = require('fs');
const path = require('path');

class ArmyCore {
  constructor() {
    this.systemId = 'ARMY-' + Math.random().toString(36).substr(2, 9);
    this.securityLevel = 'high';
    console.log(`🛡️ ArmyCore Initialized [${this.systemId}]`);
    this.unplaza = null;
  }
  
  absorbUnplaza(dir) {
    const p = path.join(dir, 'unplaza.js');
    if (fs.existsSync(p)) {
        try {
            this.unplaza = require(p);
            console.log('🛡️ ArmyCore: Absorbed unplaza.js');
            return this.unplaza;
        } catch(e) { console.error('Army fail load unplaza', e); }
    }
    return null;
  }

  executeMission(mission) {
    console.log(`[ArmyCore] Executing mission: ${mission}`);
    return {
      status: 'success',
      mission: mission,
      executor: this.systemId,
      unplaza_active: !!this.unplaza,
      tactical_analysis: "nominal"
    };
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = new ArmyCore();
}
""",
    "unplaza": """// unplaza.js
const fs = require('fs');
const path = require('path');

class Unplaza {
    constructor() {
        console.log('🧱 Unplaza Initialized');
        this.plasa = null;
    }

    absorbPlasa(dir) {
        const p = path.join(dir, 'plasa.js');
        if (fs.existsSync(p)) {
            try {
                this.plasa = require(p);
                console.log('🧱 Unplaza: Absorbed plasa.js');
                if (this.plasa.discoverModules) {
                    this.plasa.discoverModules(dir);
                }
                return this.plasa;
            } catch(e) { console.error('Unplaza fail load plasa', e); }
        }
        return null;
    }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = new Unplaza();
}
""",
    "plasa": """// plasa.js
const fs = require('fs');
const path = require('path');

class Plasa {
    constructor() {
        console.log('🔧 Plasa Initialized');
        this.modules = [];
        this.commanders = [];
    }

    getMembers() { return this.modules; }
    getCommanders() { return this.commanders; }

    discoverModules(dir) {
        console.log(`[Plasa] Scanning for modules in ${dir}...`);
        try {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                if (file.includes('memberpoint') || file.includes('commander')) {
                    this.modules.push({name: file, type: 'cjs', status: 'packed'});
                    console.log(`[Plasa] PACKED module: ${file}`);
                }
            }
        } catch(e) {}
    }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = new Plasa();
}
"""
}

# ==========================================
# WEB ACCESS MODULE (FULL IMPLEMENTATION)
# ==========================================

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

class InternetModule:
    def __init__(self, web_access):
        self.web_access = web_access
        self.enabled = True
        self.cache = {}
        self.default_search_engine = 'google'
        self.search_engines = {
            'google': {'url': 'https://www.google.com/search?q={}', 'result_selector': 'a'},
            'yandex': {'url': 'https://yandex.ru/search/?text={}', 'result_selector': '.serp-item__title-link'},
        }
        self.stats = {
            'searches': 0,
            'pages_fetched': 0,
            'cache_hits': 0,
            'errors': 0,
            'content_extracted': 0
        }
    
    def fetch_page(self, url):
        """Загрузка страницы с базовым кэшированием"""
        if url in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[url]
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Базовый парсинг
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Удаляем скрипты и стили
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            result = {
                'success': True,
                'url': url,
                'title': soup.title.string if soup.title else url,
                'text_content': text,
                'text_length': len(text),
                'links': [{'text': a.text.strip(), 'url': a.get('href')} for a in soup.find_all('a', href=True)][:20]
            }
            
            self.cache[url] = result
            self.stats['pages_fetched'] += 1
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'message': 'Failed to fetch page'
            }
    
    def _check_url_safety(self, url):
        """Проверка безопасности URL через WebAccessModule"""
        if not url:
            return False, "Empty URL"
            
        domain = self.web_access.get_domain_from_url(url)
        if domain == "BLOCKED_ILLEGAL_CONTENT":
            return False, "Blocked Domain"
            
        return True, "Safe"

    def search(self, query, engine='google', max_results=5):
        """Поиск в интернете"""
        if not self.enabled:
            return {'success': False, 'error': 'Internet module disabled'}
        
        # Если есть WebAccess - используем его продвинутый поиск
        if self.web_access:
            return self.web_access.web_search(query)
            
        self.stats['searches'] += 1
        
        try:
            # Простой фолбэк поиск если нет WebAccess (но он у нас есть)
            engine_config = self.search_engines.get(engine, self.search_engines['google'])
            search_url = engine_config['url'].format(query)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_links = soup.select(engine_config['result_selector'])
            
            for link in result_links[:max_results]:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                if href and text:
                    if href.startswith('/'):
                        continue
                    
                    is_safe, _ = self._check_url_safety(href)
                    
                    results.append({
                        'title': text[:200],
                        'url': href,
                        'is_safe': is_safe
                    })
            
            return {
                'success': True,
                'query': query,
                'engine': engine,
                'results_count': len(results),
                'results': results,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'query': query,
                'engine': engine,
                'error': str(e)
            }
    
    def extract_text(self, url):
        """Извлечение только текста со страницы"""
        result = self.fetch_page(url)
        if result['success']:
            self.stats['content_extracted'] += 1
            return {
                'success': True,
                'url': url,
                'title': result['title'],
                'text': result['text_content'],
                'length': result['text_length']
            }
        return result
    
    def get_links(self, url, filter_external=True):
        """Получение всех ссылок со страницы"""
        result = self.fetch_page(url)
        if result['success']:
            links = result['links']
            if filter_external:
                base_domain = urlparse(url).netloc
                links = [l for l in links if base_domain in urlparse(l['url']).netloc]
            return {
                'success': True,
                'url': url,
                'links': links,
                'count': len(links)
            }
        return result
    
    def multi_fetch(self, urls, max_concurrent=5):
        """Получение нескольких страниц"""
        results = []
        for url in urls[:max_concurrent]:
            results.append(self.fetch_page(url))
        return {
            'success': True,
            'total': len(urls),
            'fetched': len(results),
            'results': results
        }
    
    def set_enabled(self, enabled):
        """Включить/выключить интернет-модуль"""
        self.enabled = enabled
        return {'success': True, 'enabled': self.enabled}
    
    def get_status(self):
        """Статус модуля"""
        return {
            'module_id': self.id,
            'module_name': self.name,
            'enabled': self.enabled,
            'stats': self.stats,
            'cache_size': len(self.cache),
            'search_engines': list(self.search_engines.keys()),
            'default_engine': self.default_search_engine,
            'web_access_connected': self.web_access is not None
        }

# ==========================================
# SELF-LEARNING MODULE
# ==========================================

class LearningModule:
    def __init__(self, data_file="brain.json"):
        self.data_file = os.path.join(DATA_DIR, data_file)
        self.q_table = {}
        self.global_unit_scores = {}
        self.lock = threading.Lock()
        self.load_brain()

    def load_brain(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.q_table = data.get('q_table', {})
                    self.global_unit_scores = data.get('global_unit_scores', {})
                logger.info("🧠 Brain loaded successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to load brain: {e}")

    def save_brain(self):
        with self.lock:
            try:
                with open(self.data_file, 'w') as f:
                    json.dump({
                        'q_table': self.q_table,
                        'global_unit_scores': self.global_unit_scores
                    }, f, indent=2)
                logger.info("💾 Brain saved.")
            except Exception as e:
                logger.error(f"❌ Failed to save brain: {e}")

    def get_query_key(self, query):
        if not query:
            return "empty_query"
        words = query.lower().split()
        return words[0] if words else "default"

    def process_feedback(self, query, unit_id, score):
        key = self.get_query_key(query)
        alpha = 0.1
        
        if key not in self.q_table:
            self.q_table[key] = {}
        if unit_id not in self.q_table[key]:
            self.q_table[key][unit_id] = 0.0
            
        old_val = self.q_table[key][unit_id]
        new_val = old_val + alpha * (score - old_val)
        self.q_table[key][unit_id] = new_val
        
        curr_global = self.global_unit_scores.get(unit_id, 0.0)
        self.global_unit_scores[unit_id] = curr_global * 0.9 + new_val * 0.1
        
        self.save_brain()
        return new_val

# ==========================================
# HYBRID API CORE
# ==========================================

class HybridAPICore:
    def __init__(self):
        self.last_request_time = 0
        self.brain = LearningModule()
        self.web_access = WebAccessModule(self)
        self.internet = InternetModule(self.web_access)
        self.generated_modules = []
        self.absorbed_modules = []
        self._scan_modules()
        
        # ADDED: UNIS loading for smart routing
        self.unis = None
        self._load_unis()

    def _load_unis(self):
        unis_path = os.path.join(GEN_MODULES_DIR, "unis.py")
        if os.path.exists(unis_path):
            try:
                spec = importlib.util.spec_from_file_location("unis", unis_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.unis = module.UNIS()
                logger.info("✅ HybridAPICore: Connected to UNIS")
            except Exception as e:
                logger.error(f"❌ HybridAPICore: Failed to load UNIS: {e}")

    def _scan_modules(self):
        global GEN_MODULES_DIR, UPLOAD_DIR
        self.generated_modules = []
        self.absorbed_modules = []
        if os.path.exists(GEN_MODULES_DIR):
            for f in os.listdir(GEN_MODULES_DIR):
                if os.path.isfile(os.path.join(GEN_MODULES_DIR, f)):
                    self.generated_modules.append(f)
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                if os.path.isfile(os.path.join(UPLOAD_DIR, f)):
                    self.absorbed_modules.append(f)
        logger.info(f"Scanned {len(self.generated_modules)} generated modules, {len(self.absorbed_modules)} absorbed modules.")

    def generate_module(self, module_type, custom_params=None):
        content = ""
        filename = ""
        
        if module_type in TEMPLATES:
            content = TEMPLATES[module_type]
            ext = ".js" if module_type in ["pia", "army_core", "unplaza", "plasa"] else ".py"
            filename = f"{module_type}{ext}"
        
        elif module_type == "web_access":
            blocked = custom_params.get("blocked_domains", "") if custom_params else ""
            trusted = custom_params.get("trusted_sources", "") if custom_params else ""
            
            content = f"""
# Web Access Module
# Generated by APICore Genesis at {datetime.datetime.now().isoformat()}
# Configuration:
# - Blocked: {blocked}
# - Trusted: {trusted}

class WebAccess:
    def __init__(self):
        self.blocked_domains = {self.web_access.blocked_com_domains}
        self.trusted_sources = {self.web_access.trusted_sources}
        self.extremist_materials = {self.web_access.extremist_materials}
    
    def scan(self, url):
        # Implementation here
        pass
"""
            filename = "web_access.py"
        
        else:
            return {"success": False, "error": f"Unknown module type: {module_type}"}
        
        if not content:
            return {"success": False, "error": "No content generated"}
        
        file_path = os.path.join(GEN_MODULES_DIR, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._scan_modules()
            logger.info(f"Generated module: {filename}")
            
            # If UNIS was generated, reload it
            if module_type == 'unis':
                self._load_unis()
                
            return {"success": True, "filename": filename, "path": file_path}
        except Exception as e:
            logger.error(f"Failed to generate module: {e}")
            return {"success": False, "error": str(e)}

    def generate_all_chain_modules(self):
        results = []
        chain_order = ["plasa", "unplaza", "army_core", "pia", "plaza", "intelligent_core", "unis"]
        for mod_type in chain_order:
            result = self.generate_module(mod_type)
            results.append({"type": mod_type, "result": result})
        return results

    def get_chat_response(self, message):
        """
        ИИ-ассистент с умной маршрутизацией (UNIS vs Internet).
        """
        thinking_steps = []
        msg_lower = message.lower().strip()
        
        thinking_steps.append(f"Анализирую запрос: '{message[:60]}...'")
        
        # Системные команды
        if msg_lower in ['статус', 'status']:
            thinking_steps.append("Получаю статус системы")
            inet_status = "включен" if self.internet.enabled else "выключен"
            return {
                'thinking_steps': thinking_steps,
                'final_response': f"**Статус Genesis:**\n\nID: {SYSTEM_ID[:8]}\nМодулей: {len(self.generated_modules)}\nПоглощено: {len(self.absorbed_modules)}\nИнтернет: {inet_status}\nUNIS: {'Подключен' if self.unis else 'Отключен'}"
            }
        
        if msg_lower in ['помощь', 'help', 'привет', 'hi', 'hello']:
            return {
                'thinking_steps': ["Приветствие"],
                'final_response': "Привет! Я Genesis - ИИ-ассистент с доступом в интернет.\n\nПросто задайте мне вопрос, и я найду информацию в интернете. Например:\n• Что такое Python?\n• Какая погода в Москве?\n• Расскажи про искусственный интеллект\n\nИнтернет можно включить/выключить переключателем выше."
            }
        
        # Проверяем есть ли URL в сообщении - сразу загружаем
        url_match = re.search(r'https?://[^\s]+|(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:/[^\s]*)?', message)
        if url_match:
            url = url_match.group()
            thinking_steps.append(f"Обнаружен URL: {url}")
            
            if not self.internet.enabled:
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': "Интернет выключен. Включите его переключателем, чтобы я мог загрузить страницу."
                }
            
            thinking_steps.append("Загружаю страницу...")
            result = self.internet.fetch_page(url)
            if result['success']:
                thinking_steps.append(f"Загружено: {result['title']}")
                text_preview = result['text_content'][:800] if result['text_content'] else "Текст не найден"
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"**{result['title']}**\n\n{text_preview}..."
                }
            else:
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"Не удалось загрузить: {result.get('message', 'Ошибка')}"
                }
        
        # ИИ-режим: определяем нужен ли интернет для ответа
        needs_internet = self._needs_internet_search(message)
        thinking_steps.append(f"Требуется интернет: {'да' if needs_internet else 'нет'}")
        
        if needs_internet:
            if not self.internet.enabled:
                thinking_steps.append("Интернет выключен")
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"Для ответа на '{message}' мне нужен интернет, но он выключен. Включите его переключателем выше."
                }
            
            # Автоматический поиск
            thinking_steps.append(f"Ищу в интернете: {message}")
            search_result = self.internet.search(message, max_results=5)
            
            if search_result['success'] and search_result.get('results'):
                thinking_steps.append(f"Найдено результатов: {len(search_result['results'])}")
                
                # Пробуем загрузить первый безопасный результат
                for res in search_result['results'][:3]:
                    if res.get('is_safe'):
                        thinking_steps.append(f"Читаю: {res['url']}")
                        page = self.internet.fetch_page(res['url'])
                        if page['success'] and page.get('text_content'):
                            text = page['text_content'][:1200]
                            return {
                                'thinking_steps': thinking_steps,
                                'final_response': f"**{page['title']}**\n\n{text}...\n\n*Источник: {res['url']}*"
                            }
                
                # Если не удалось загрузить - показываем список
                results_list = "\n".join([f"• {r['title'][:60]}" for r in search_result['results'][:5]])
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"Нашёл по запросу '{message}':\n\n{results_list}"
                }
            else:
                thinking_steps.append("Поиск не дал результатов")
                return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"К сожалению, не нашёл информацию по запросу '{message}'."
                }
        
        # Обычный разговор без интернета -> UNIS
        thinking_steps.append("Запрос не требует интернета - обращаюсь к UNIS")
        
        if self.unis:
            try:
                thinking_steps.append("Отправка запроса в ядро UNIS...")
                unis_result = self.unis.process_query(message)
                
                # Попробуем красиво отформатировать результат
                if 'downstream_result' in unis_result:
                    # Уходим вглубь цепочки
                    result_content = unis_result['downstream_result']
                    if isinstance(result_content, dict) and 'downstream_result' in result_content:
                        result_content = result_content['downstream_result']
                    
                    # Если это результат от pia/plaza
                    if isinstance(result_content, dict):
                        if 'mission_result' in result_content:
                            # Ответ от Army
                            mission = result_content.get('mission_result', {})
                            response_text = f"**UNIS [ArmyCore]**\nСтатус миссии: {mission.get('status')}\nИсполнитель: {mission.get('executor')}\n\nВыполнено."
                        elif 'status' in result_content and result_content.get('status') == 'executed':
                            # Ответ от Plaza
                            response_text = f"**UNIS [Plaza]**\nКоманда выполнена успешно."
                        else:
                            response_text = f"**UNIS Response:**\n```json\n{json.dumps(result_content, indent=2, ensure_ascii=False)}\n```"
                    else:
                        response_text = str(result_content)
                else:
                    response_text = json.dumps(unis_result, indent=2, ensure_ascii=False)

                return {
                    'thinking_steps': thinking_steps,
                    'final_response': response_text
                }
            except Exception as e:
                 thinking_steps.append(f"Ошибка UNIS: {e}")
                 return {
                    'thinking_steps': thinking_steps,
                    'final_response': f"Произошла ошибка при обращении к UNIS: {str(e)}"
                 }
        
        # Если UNIS нет или упал
        thinking_steps.append("UNIS недоступен, использую резервные ответы")
        greetings = ['как дела', 'как ты', 'что делаешь']
        if any(g in msg_lower for g in greetings):
            return {
                'thinking_steps': thinking_steps,
                'final_response': "У меня всё хорошо! Готов помочь с поиском информации. Что вас интересует?"
            }
        
        return {
            'thinking_steps': thinking_steps,
            'final_response': f"Понял вас. Если нужна информация из интернета, просто спросите - я найду! (Модуль UNIS сейчас не подключен)"
        }
    
    def _needs_internet_search(self, message):
        """Определяет, нужен ли поиск в интернете для ответа"""
        msg_lower = message.lower()
        
        # Вопросительные слова
        question_words = ['что такое', 'кто такой', 'как ', 'почему', 'зачем', 'где ', 'когда', 
                          'сколько', 'какой', 'какая', 'какие', 'расскажи', 'объясни', 'найди',
                          'покажи', 'что значит', 'определение', 'wiki', 'новости']
        
        # Темы требующие интернет
        internet_topics = ['погода', 'курс', 'цена', 'новости', 'события', 'python', 'javascript',
                           'программирование', 'технологии', 'наука', 'история', 'факты']
        
        for word in question_words:
            if word in msg_lower:
                return True
        
        for topic in internet_topics:
            if topic in msg_lower:
                return True
        
        # Если сообщение похоже на вопрос (заканчивается на ?)
        if message.strip().endswith('?'):
            return True
        
        # Если сообщение длинное - скорее всего вопрос
        if len(message.split()) >= 4:
            return True
        
        return False


api_core = HybridAPICore()

# ==========================================
# FLASK ROUTES
# ==========================================

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/status')
def get_status():
    chain_status = {
        "genesis": True,
        "unis": os.path.exists(os.path.join(GEN_MODULES_DIR, "unis.py")),
        "intelligent_core": os.path.exists(os.path.join(GEN_MODULES_DIR, "intelligent_core.py")),
        "plaza": os.path.exists(os.path.join(GEN_MODULES_DIR, "plaza.py")),
        "pia": os.path.exists(os.path.join(GEN_MODULES_DIR, "pia.js")),
        "army": os.path.exists(os.path.join(GEN_MODULES_DIR, "army_core.js")),
        "unplaza": os.path.exists(os.path.join(GEN_MODULES_DIR, "unplaza.js")),
        "plasa": os.path.exists(os.path.join(GEN_MODULES_DIR, "plasa.js")),
    }
    
    return jsonify({
        "system_id": SYSTEM_ID,
        "startup_time": STARTUP_TIME,
        "generated_modules_count": len(api_core.generated_modules),
        "absorbed_modules_count": len(api_core.absorbed_modules),
        "chain_status": chain_status,
        "web_access_status": api_core.web_access.status
    })

@app.route('/api/modules')
def list_modules():
    api_core._scan_modules()
    return jsonify({
        "generated": api_core.generated_modules,
        "absorbed": api_core.absorbed_modules
    })

@app.route('/api/generate', methods=['POST'])
def generate_module():
    data = request.get_json()
    module_type = data.get('type', 'unis')
    custom_params = data.get('params', {})
    
    result = api_core.generate_module(module_type, custom_params)
    return jsonify(result)

@app.route('/api/generate/all', methods=['POST'])
def generate_all():
    results = api_core.generate_all_chain_modules()
    return jsonify({
        "success": True,
        "results": results
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    response_data = api_core.get_chat_response(message)
    
    return jsonify({
        "status": "success",
        "response": response_data
    })

@app.route('/api/web-access/scan', methods=['POST'])
def web_access_scan():
    data = request.get_json()
    url = data.get('url', '')
    depth = data.get('depth', 1)
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    result = api_core.web_access.scan_url(url, depth)
    
    if result['status'] == 'blocked':
        return jsonify(result), 403
    
    return jsonify(result)

@app.route('/api/web-access/status')
def web_access_status():
    return jsonify({
        "module": api_core.web_access.name,
        "status": api_core.web_access.status,
        "extremist_materials_count": len(api_core.web_access.extremist_materials),
        "blocked_domains_count": len(api_core.web_access.blocked_com_domains),
        "trusted_sources_count": len(api_core.web_access.trusted_sources)
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        api_core._scan_modules()
        
        # Auto-package logic if enabled
        if SETTINGS.get("auto_package_on_absorb", False):
            # Placeholder for packaging logic
            pass
            
        return jsonify({"success": True, "filename": filename, "path": filepath})
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        new_settings = request.get_json()
        SETTINGS.update(new_settings)
        save_settings(SETTINGS)
        return jsonify({"success": True, "settings": SETTINGS})
    return jsonify(SETTINGS)

if __name__ == '__main__':
    # This is handled by main.py in production, but for testing:
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
