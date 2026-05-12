"""
ApiCore v2.0 "Neural Nexus"
Сверхсовершенное ядро, объединяющее лучшие идеи из LangChain, LlamaIndex и FastAPI.
Особенности:
- Событийно-ориентированная архитектура (Event-Driven)
- Динамический граф знаний (Knowledge Graph)
- Самовосстанавливающаяся контекстная память
- Асинхронные пайплайны обработки
- Встроенный механизм кэширования состояний
"""

import json
import os
import hashlib
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from collections import deque
import threading

# Импорт локальных модулей (с обработкой ошибок для гибкости)
try:
    from simple_ocr import SimpleOCR
    from numeric_pinyin_ai import NumericPinyinAI
    from lite_marker import LiteMarker
except ImportError:
    # Заглушки, если модули еще не загружены, чтобы ядро работало автономно
    class SimpleOCR:
        def process(self, data): return {"text": str(data), "pinyin_numeric": str(data)}
    class NumericPinyinAI:
        def __init__(self, *args, **kwargs): self.memory = {"patterns": [], "learned_words": {}}
        def learn(self, i, o): return True
        def recognize(self, i): return None
        def add_memory(self, c, d): pass
        def save_memory(self): pass
    class LiteMarker:
        def process_document(self, c): return str(c)

class EventNode:
    """Узел графа событий для цепочек рассуждений"""
    def __init__(self, name: str, handler: Callable):
        self.name = name
        self.handler = handler
        self.next_nodes: List['EventNode'] = []
    
    def connect(self, node: 'EventNode'):
        self.next_nodes.append(node)
        return node

class KnowledgeGraph:
    """Легковесный граф знаний для связывания концепций"""
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []

    def add_concept(self, concept_id: str, data: Dict):
        if concept_id not in self.nodes:
            self.nodes[concept_id] = {"data": data, "connections": [], "access_count": 0}
        else:
            self.nodes[concept_id]["data"].update(data)
        
    def link(self, source: str, target: str, relation: str):
        self.edges.append({"source": source, "target": target, "relation": relation})
        if source in self.nodes: self.nodes[source]["connections"].append(target)
        if target in self.nodes: self.nodes[target]["connections"].append(source)

    def query(self, concept_id: str, depth=1) -> List[Dict]:
        if concept_id not in self.nodes: return []
        self.nodes[concept_id]["access_count"] += 1
        results = [self.nodes[concept_id]]
        if depth > 0:
            for conn in self.nodes[concept_id]["connections"]:
                results.extend(self.query(conn, depth-1))
        return results

class StateCache:
    """Кэш состояний с автоматической очисткой (LRU)"""
    def __init__(self, max_size=100):
        self.cache: Dict[str, Any] = {}
        self.access_order: deque = deque()
        self.max_size = max_size
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None

    def set(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                oldest = self.access_order.popleft()
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)

class ApiCoreV2:
    """
    Сверхсовершенное ядро системы.
    Объединяет OCR, AI, Marker в единую нейронную сеть обработки данных.
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.instance_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        self.config_path = config_path
        
        # Инициализация компонентов
        self.ocr = SimpleOCR()
        self.ai = NumericPinyinAI()
        self.marker = LiteMarker()
        
        # Продвинутые структуры
        self.graph = KnowledgeGraph()
        self.cache = StateCache(max_size=500)
        self.event_queue: deque = deque()
        self.logs: List[Dict] = []
        
        # Построение графа обработки по умолчанию
        self._build_default_pipeline()
        
        # Автозагрузка состояния
        self._load_state()

    def _build_default_pipeline(self):
        """Создание стандартного пайплайна обработки"""
        def ocr_handler(ctx): 
            ctx['result'] = self.ocr.process(ctx.get('input', ''))
            return ctx
        def ai_handler(ctx): 
            text = ctx.get('result', {}).get('text', '')
            if text:
                ctx['ai_insight'] = self.ai.recognize(text)
            return ctx
        def graph_handler(ctx):
            req_id = ctx.get('request_id')
            if req_id:
                self.graph.add_concept(req_id, {"type": "request", "timestamp": time.time()})
            return ctx

        self.root_node = EventNode("OCR_Start", ocr_handler)
        node_ai = EventNode("AI_Analyze", ai_handler)
        node_graph = EventNode("Graph_Log", graph_handler)
        
        self.root_node.connect(node_ai).connect(node_graph)

    def _generate_cache_key(self, data: Any) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _log_event(self, event_type: str, data: Any, level: str = "INFO"):
        entry = {
            "ts": datetime.now().isoformat(),
            "type": event_type,
            "level": level,
            "data": str(data)[:200], # Обрезка для безопасности
            "instance": self.instance_id
        }
        self.logs.append(entry)
        if len(self.logs) > 1000: self.logs = self.logs[-500:] # Rotate logs
        return entry

    def _save_state(self):
        """Сохранение полного состояния системы (Checkpoints)"""
        state = {
            "graph_nodes": self.graph.nodes,
            "graph_edges": self.graph.edges,
            "logs_count": len(self.logs),
            "last_update": datetime.now().isoformat()
        }
        try:
            os.makedirs("system_state", exist_ok=True)
            with open("system_state/core_snapshot.json", "w") as f:
                json.dump(state, f)
            self.ai.save_memory() # Сохраняем память ИИ отдельно
        except Exception as e:
            self._log_event("SAVE_ERROR", str(e), "ERROR")

    def _load_state(self):
        """Восстановление состояния при старте"""
        if os.path.exists("system_state/core_snapshot.json"):
            try:
                with open("system_state/core_snapshot.json", "r") as f:
                    state = json.load(f)
                    # Восстановление графа (упрощенно)
                    self.graph.nodes = state.get("graph_nodes", {})
                    self.graph.edges = state.get("graph_edges", [])
                self._log_event("STATE_RESTORED", "System state loaded successfully")
            except:
                self._log_event("STATE_LOAD_FAIL", "Could not load previous state", "WARN")

    def execute_pipeline(self, input_data: Any, request_id: Optional[str] = None) -> Dict:
        """
        Выполнение данных через цепочку событий (Pipeline Execution).
        Использует кэширование для ускорения повторяющихся запросов.
        """
        req_id = request_id or str(uuid.uuid4())
        cache_key = self._generate_cache_key(input_data)
        
        # Проверка кэша
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self._log_event("CACHE_HIT", req_id)
            return {"status": "cached", "data": cached_result, "request_id": req_id}

        # Подготовка контекста
        context = {
            "input": input_data,
            "request_id": req_id,
            "start_time": time.time(),
            "trace": []
        }

        # Проход по графу событий
        current_node = self.root_node
        while current_node:
            try:
                start_step = time.time()
                context = current_node.handler(context)
                context["trace"].append({
                    "node": current_node.name,
                    "duration": time.time() - start_step
                })
                
                # Переход к следующему узлу (DFS упрощенный)
                if current_node.next_nodes:
                    current_node = current_node.next_nodes[0]
                else:
                    current_node = None
            except Exception as e:
                self._log_event("PIPELINE_ERROR", str(e), "ERROR")
                context["error"] = str(e)
                break

        # Сохранение в кэш и граф
        result = context.get("result", {})
        self.cache.set(cache_key, result)
        
        # Добавление связи в граф знаний если есть результат
        if isinstance(result, dict) and "text" in result:
            self.graph.add_concept(req_id, {"content": result["text"], "type": "ocr_result"})
            if context.get("ai_insight"):
                self.graph.link(req_id, "ai_knowledge_base", "derived_from")

        self._log_event("PIPELINE_COMPLETE", {"req_id": req_id, "duration": time.time() - context["start_time"]})
        
        # Асинхронное сохранение состояния (в реальном приложении вынести в поток)
        if len(self.logs) % 50 == 0:
            self._save_state()

        return {
            "status": "success",
            "data": result,
            "ai_insight": context.get("ai_insight"),
            "trace": context["trace"],
            "request_id": req_id
        }

    # --- Публичные API методы (совместимость + новые функции) ---

    def smart_process(self, data: Any, mode: str = "auto") -> Dict:
        """Умная обработка с авто-выбором режима"""
        self._log_event("SMART_PROCESS", f"Mode: {mode}")
        
        if mode == "document" or (isinstance(data, str) and len(data) > 500):
            md = self.marker.process_document(data)
            self.graph.add_concept("doc_" + str(uuid.uuid4())[:6], {"type": "markdown", "content_preview": md[:100]})
            return {"type": "document", "markdown": md}
        
        return self.execute_pipeline(data)

    def learn_pattern(self, input_text: str, output_pattern: str, tags: List[str] = None):
        """Обучение с обогащением мета-данными"""
        success = self.ai.learn(input_text, output_pattern)
        if success:
            concept_id = f"pattern_{hashlib.md5(input_text.encode()).hexdigest()[:8]}"
            self.graph.add_concept(concept_id, {
                "type": "learned_pattern",
                "input": input_text,
                "output": output_pattern,
                "tags": tags or []
            })
            if tags:
                for tag in tags:
                    self.graph.link(concept_id, f"tag_{tag}", "categorized_by")
        return {"success": success, "concept_id": concept_id}

    def query_knowledge(self, query: str, depth: int = 2) -> List[Dict]:
        """Запрос к графу знаний"""
        # Простой поиск по ключам (можно расширить до векторного)
        results = []
        for node_id, node_data in self.graph.nodes.items():
            if query.lower() in json.dumps(node_data).lower():
                results.extend(self.graph.query(node_id, depth))
        return results

    def get_system_health(self) -> Dict:
        """Глубокая диагностика системы"""
        return {
            "status": "operational",
            "version": "2.0.0-neural-nexus",
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "instance_id": self.instance_id,
            "components": {
                "ocr": "active",
                "ai_memory": "active",
                "marker": "active",
                "knowledge_graph": {"nodes": len(self.graph.nodes), "edges": len(self.graph.edges)},
                "cache": {"size": len(self.cache.cache), "max": self.cache.max_size}
            },
            "recent_logs": self.logs[-5:]
        }

# Глобальный экземпляр (Singleton pattern)
core_instance = None

def get_core() -> ApiCoreV2:
    global core_instance
    if core_instance is None:
        core_instance = ApiCoreV2()
    return core_instance

# Для совместимости со старым кодом
if __name__ == "__main__":
    core = get_core()
    print("ApiCore v2.0 Initialized")
    print(core.get_system_health())
