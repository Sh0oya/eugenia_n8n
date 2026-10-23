"""Small builder used to generate the "Can My PC Run It" n8n workflow.

Conventions enforced here (course "Delivery" module + n8ncli lint):
- node names: Title Case, ASCII, English, "Tool - Action";
- Set variables: camelCase English words;
- sticky colors: blue = specs, gray = grouping, yellow = to do, red = bug, green = idea, purple = help;
- no expression of the form  'text' + $json.x  (the SDK parser rejects it): use template literals.
"""
import json
import os
import re
import uuid
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
CODE_DIR = TOOLS / "code"
PROMPT_DIR = TOOLS / "prompts"

BLUE, GRAY, YELLOW, RED, GREEN, PURPLE = 5, 7, 1, 3, 4, 6

# "portable" = no credential, placeholder identifiers (committed to GitHub).
# "instance" = real identifiers read from tools/instance.local.json (never committed).
PROFILE = os.environ.get("PROFILE", "portable")
LOCAL = {}
if PROFILE == "instance":
    LOCAL = json.loads((TOOLS / "instance.local.json").read_text(encoding="utf-8"))

COL = 240   # horizontal grid step
ROW = 200   # vertical grid step

BAD_CONCAT = re.compile(r"""['"`]\s*\+\s*\(?\s*\$(?:node|\(|\w+)""")
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")


def code(file_name):
    return (CODE_DIR / file_name).read_text(encoding="utf-8")


def prompt(file_name):
    return (PROMPT_DIR / file_name).read_text(encoding="utf-8")


def cred(kind):
    """Credential reference for a node (empty in the portable profile)."""
    known = LOCAL.get("credentials", {}).get(kind)
    if PROFILE != "instance" or not known:
        return {}
    return {"credentials": {known["type"]: {"id": known["id"], "name": known["name"]}}}


def local(key, placeholder):
    return LOCAL.get(key, placeholder) if PROFILE == "instance" else placeholder


def expr(text):
    """n8n expression. Rejects the concatenation pattern flagged by n8ncli lint."""
    found = BAD_CONCAT.search(text)
    if found:
        raise ValueError(f"Expression uses quote + $variable concatenation, use a template literal: ...{text[max(0, found.start() - 30):found.end() + 30]}...")
    # a "}}" inside an expression can end it early: every inner "}}" must be written "} }"
    for part in re.findall(r"\{\{(.*?)\}\}(?!\})", text, re.S):
        if "}}" in part:
            raise ValueError(f"Expression contains a }} sequence that can end it early: ...{part[part.index('}}') - 40:part.index('}}') + 10]}...")
    return "=" + text


def sid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "can-my-pc-run-it/" + "/".join(parts)))


def fields(*items, keep=False):
    """Set node 3.4 parameters. items = (name, type, value); names must be camelCase."""
    assignments = []
    for name, kind, value in items:
        if not CAMEL.match(name):
            raise ValueError(f"Variable name must be camelCase: {name}")
        assignments.append({"id": sid("field", name, str(value)[:40]), "name": name, "type": kind, "value": value})
    params = {"assignments": {"assignments": assignments}, "options": {}}
    if keep:
        params["includeOtherFields"] = True
    return params


def cond(left, operation="true", kind="boolean", right=None):
    c = {"id": sid("cond", left, operation, str(right)), "leftValue": left, "operator": {"type": kind, "operation": operation}}
    if right is None:
        c["operator"]["singleValue"] = True
    else:
        c["rightValue"] = right
    return c


def conditions(*items, combinator="and"):
    return {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2}, "conditions": list(items), "combinator": combinator}


def locator(value, mode="id"):
    return {"__rl": True, "mode": mode, "value": value}


class Flow:
    def __init__(self, name, description, settings=None):
        self.name = name
        self.description = description
        self.nodes = []
        self.connections = {}
        self.extra_settings = settings or {}

    def add(self, name, type_, version, params, pos, note=None, **extra):
        if any(n["name"] == name for n in self.nodes):
            raise ValueError(f"Duplicate node name: {name}")
        node = {"parameters": params, "id": sid("node", name), "name": name, "type": type_, "typeVersion": version,
                "position": [int(pos[0] * COL), int(pos[1] * ROW)]}
        if note:
            node["notes"] = note
            node["notesInFlow"] = True
        node.update(extra)
        self.nodes.append(node)
        return name

    def link(self, source, target, out=0, inp=0, kind="main"):
        outputs = self.connections.setdefault(source, {}).setdefault(kind, [])
        while len(outputs) <= out:
            outputs.append([])
        outputs[out].append({"node": target, "type": kind, "index": inp})

    def chain(self, *names):
        for a, b in zip(names, names[1:]):
            self.link(a, b)

    def sticky(self, text, pos, width, height, color):
        count = len([n for n in self.nodes if n["type"].endswith("stickyNote")]) + 1
        self.nodes.append({"parameters": {"content": text, "width": width, "height": height, "color": color},
                           "id": sid("sticky", str(count), text[:30]), "name": f"Sticky Note {count}",
                           "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [int(pos[0]), int(pos[1])]})

    def group(self, text, names, color=GRAY, margin=40, top=150):
        by_name = {n["name"]: n for n in self.nodes}
        missing = [n for n in names if n not in by_name]
        if missing:
            raise ValueError(f"Unknown nodes in group: {missing}")
        xs = [by_name[n]["position"][0] for n in names]
        ys = [by_name[n]["position"][1] for n in names]
        self.sticky(text, (min(xs) - margin, min(ys) - top), max(xs) - min(xs) + 2 * margin + 180, max(ys) - min(ys) + top + margin + 120, color)

    def to_json(self, pin=None):
        names = {n["name"] for n in self.nodes}
        for source, kinds in self.connections.items():
            if source not in names:
                raise ValueError(f"Unknown connection source: {source}")
            for outputs in kinds.values():
                for targets in outputs:
                    for t in targets:
                        if t["node"] not in names:
                            raise ValueError(f"Unknown connection target: {t['node']}")
        settings = {"executionOrder": "v1", "timezone": "Europe/Paris", "saveManualExecutions": True,
                    "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all", "saveExecutionProgress": True,
                    "callerPolicy": "workflowsFromSameOwner", "availableInMCP": False}
        settings.update(self.extra_settings)
        settings["description"] = self.description
        return {"name": self.name, "nodes": self.nodes, "connections": self.connections, "settings": settings,
                "pinData": pin or {}, "active": False}


# ---- node type shortcuts: (type, version) ----
SET = ("n8n-nodes-base.set", 3.4)
IF = ("n8n-nodes-base.if", 2.2)
SWITCH = ("n8n-nodes-base.switch", 3.2)
CODE = ("n8n-nodes-base.code", 2)
HTTP = ("n8n-nodes-base.httpRequest", 4.2)
GITHUB = ("n8n-nodes-base.github", 1.1)
GMAIL = ("n8n-nodes-base.gmail", 2.1)
NOTION = ("n8n-nodes-base.notion", 3)
TABLE = ("n8n-nodes-base.dataTable", 1.1)
SPLIT_OUT = ("n8n-nodes-base.splitOut", 1)
AGGREGATE = ("n8n-nodes-base.aggregate", 1)
LIMIT = ("n8n-nodes-base.limit", 1)
FILTER = ("n8n-nodes-base.filter", 2.2)
SORT = ("n8n-nodes-base.sort", 1)
MERGE = ("n8n-nodes-base.merge", 3.2)
REMOVE_DUP = ("n8n-nodes-base.removeDuplicates", 1.1)
SUMMARIZE = ("n8n-nodes-base.summarize", 1.1)
CRYPTO = ("n8n-nodes-base.crypto", 2)
XML = ("n8n-nodes-base.xml", 1)
LOOP_NODE = ("n8n-nodes-base.splitInBatches", 3)
EXTRACT_FILE = ("n8n-nodes-base.extractFromFile", 1.1)
CONVERT_FILE = ("n8n-nodes-base.convertToFile", 1.1)
COMPARE = ("n8n-nodes-base.compareDatasets", 2.3)
WAIT = ("n8n-nodes-base.wait", 1.1)
STOP_ERROR = ("n8n-nodes-base.stopAndError", 1)
CHAIN = ("@n8n/n8n-nodes-langchain.chainLlm", 1.9)
GEMINI_CHAT = ("@n8n/n8n-nodes-langchain.lmChatGoogleGemini", 1.2)
GEMINI_NODE = ("@n8n/n8n-nodes-langchain.googleGemini", 1.2)
PARSER = ("@n8n/n8n-nodes-langchain.outputParserStructured", 1.3)
VECTOR_STORE = ("@n8n/n8n-nodes-langchain.vectorStoreInMemory", 1.3)
DATA_LOADER = ("@n8n/n8n-nodes-langchain.documentDefaultDataLoader", 1.1)
EMBEDDINGS = ("@n8n/n8n-nodes-langchain.embeddingsGoogleGemini", 1)

RETRY = {"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000}


def table_ref(name):
    return {"__rl": True, "mode": "name", "value": name}


def table_insert(name, columns):
    return {"resource": "row", "operation": "insert", "dataTableId": table_ref(name),
            "columns": {"mappingMode": "defineBelow", "value": columns, "matchingColumns": [], "schema": []}, "options": {}}


def table_get(name, filters=None, limit=None):
    params = {"resource": "row", "operation": "get", "dataTableId": table_ref(name), "returnAll": limit is None,
              "matchType": "allConditions", "options": {}}
    if limit:
        params["limit"] = limit
    if filters:
        params["filters"] = {"conditions": [{"keyName": k, "condition": "eq", "keyValue": v} for k, v in filters]}
    return params


def table_update(name, filters, columns):
    return {"resource": "row", "operation": "update", "dataTableId": table_ref(name), "matchType": "allConditions",
            "filters": {"conditions": [{"keyName": k, "condition": "eq", "keyValue": v} for k, v in filters]},
            "columns": {"mappingMode": "defineBelow", "value": columns, "matchingColumns": [], "schema": []}, "options": {}}


def table_upsert(name, filters, columns):
    return {"resource": "row", "operation": "upsert", "dataTableId": table_ref(name), "matchType": "allConditions",
            "filters": {"conditions": [{"keyName": k, "condition": "eq", "keyValue": v} for k, v in filters]},
            "columns": {"mappingMode": "defineBelow", "value": columns, "matchingColumns": [], "schema": []}, "options": {}}


def table_clear(name):
    return {"resource": "table", "operation": "clear", "dataTableId": table_ref(name)}


def table_create(name, columns):
    return {"resource": "table", "operation": "create", "tableName": name,
            "columns": {"column": [{"name": c, "type": t} for c, t in columns]}, "options": {"createIfNotExists": True}}


def gmail_params(subject, message, attachment=False):
    options = {"appendAttribution": False, "senderName": "Can My PC Run It"}
    if attachment:
        options["attachmentsUi"] = {"attachmentsBinary": [{"property": "data"}]}
    return {"sendTo": "={{ $('CONFIGURATION').first().json.notificationEmail }}", "subject": subject, "emailType": "html",
            "message": message, "options": options}


def notion_create(title, properties, markdown):
    return {"resource": "databasePage", "operation": "create",
            "dataSourceId": locator("={{ $('CONFIGURATION').first().json.notionAnalysesDataSourceId }}"),
            "title": title, "propertiesUi": {"propertyValues": properties}, "contentType": "markdown", "markdown": markdown,
            "simple": False, "options": {}}


def notion_update(page_id, properties):
    return {"resource": "databasePage", "operation": "update", "pageId": locator(page_id), "propertiesUi": {"propertyValues": properties},
            "simple": False, "options": {}}


def notion_property(key, kind, value, **extra):
    field = {"select": "selectValue", "rich_text": "textContent", "number": "numberValue", "url": "urlValue"}[kind]
    return {"key": f"{key}|{kind}", field: value, **extra}


def notion_add(flow, name, version_params, pos, note=None, **extra):
    """Notion v3 nodes always use the OAuth2 credential."""
    params = {"authentication": "oAuth2", **version_params}
    return flow.add(name, *NOTION, params, pos, note=note, **cred("notion"), **extra)
