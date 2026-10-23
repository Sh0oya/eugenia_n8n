"""Personal context (RAG): Notion profile and inventory are indexed in an in-memory vector store, then searched per repository."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
EVAL = "$('Set - Evaluate References').first().json"
BUILD = "$('Set - Build Context Documents').first().json"
MD = "$('Notion - Get Profile Markdown').first().json.markdown"
NORM = "(s => String(s || '').toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, ''))"
STORE_KEY = {"__rl": True, "mode": "id", "value": "can_my_pc_context"}
MODEL = expr(f"{{{{ `models/${{{CFG}.embeddingModel}}` }}}}")


def rich(prop):
    return f"($json.properties?.['{prop}']?.rich_text || []).map(t => t.plain_text).join('')"


def build(w):
    r = 12  # first row of this band
    notion_add(w, "Notion - Get Profile Markdown", {"resource": "block", "operation": "getMarkdown", "blockId": locator(expr(f"{{{{ {CFG}.notionProfilePageId }}}}")), "includeTranscript": False},
               (7, r), onError="continueRegularOutput", **RETRY)
    notion_add(w, "Notion - Get Inventory Items", {"resource": "databasePage", "operation": "getAll", "dataSourceId": locator(expr(f"{{{{ {CFG}.notionInventoryDataSourceId }}}}")),
                                                   "returnAll": True, "filterType": "none", "simple": False, "options": {}},
               (8, r), alwaysOutputData=True, executeOnce=True, onError="continueRegularOutput", **RETRY)
    w.add("Set - Format Inventory Items", *SET, fields(
        ("id", "string", expr("{{ $json.id || '' }}")), ("type", "string", "inventory"), ("url", "string", expr("{{ $json.url || '' }}")),
        ("name", "string", expr(f"{{{{ ($json.properties?.Nom?.title || []).map(t => t.plain_text).join('') }}}}")),
        ("state", "string", expr("{{ $json.properties?.Etat?.select?.name || '' }}")), ("presence", "string", expr("{{ $json.properties?.Presence?.select?.name || '' }}")),
        ("usage", "string", expr(f"{{{{ {rich('Usage')} }}}}")), ("feedback", "string", expr(f"{{{{ {rich('Retour')} }}}}")),
        ("abandonReason", "string", expr(f"{{{{ {rich('Raison Abandon')} }}}}")), ("environment", "string", expr(f"{{{{ {rich('Environnement')} }}}}")),
        ("version", "string", expr(f"{{{{ {rich('Version')} }}}}")), ("infoDate", "string", expr("{{ $json.properties?.['Date Info']?.date?.start || '' }}")),
        ("source", "string", expr(f"{{{{ {rich('Source')} }}}}")), ("uncertainties", "string", expr(f"{{{{ {rich('Incertitudes')} }}}}"))), (9, r))
    w.add("Aggregate - Inventory", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "inventory", "options": {}}, (10, r))
    w.add("Set - Build Context Documents", *SET, fields(
        ("machine", "object", expr(f"{{{{ (() => {{ try {{ return JSON.parse({MD}.match(/```json\\s*([\\s\\S]*?)```/)[1]).machine || {{}}; }} catch (e) {{ return {{}}; }} }})() }}}}")),
        ("profileRevision", "string", expr(f"{{{{ (() => {{ try {{ return JSON.parse({MD}.match(/```json\\s*([\\s\\S]*?)```/)[1]).revision || ''; }} catch (e) {{ return ''; }} }})() }}}}")),
        ("sections", "array", expr(f"{{{{ String({MD} || '').replace(/```[\\s\\S]*?```/g, '').split(/\\n(?=#{{1,3}}\\s)/).map(s => s.trim()).filter(s => s.length > 20).map((s, i) => ({{ id: `profile-${{i + 1}}`, type: 'profile', label: s.split('\\n')[0].replace(/^#+\\s*/, '').slice(0, 80), url: `https://www.notion.so/${{String({CFG}.notionProfilePageId).replace(/-/g, '')}}`, text: s.slice(0, 3000) }})) }}}}")),
        ("inventory", "array", expr("{{ $json.inventory.filter(o => o.id && o.name).map(o => ({ ...o, label: o.name, text: [`${o.name} (${o.state || 'unknown state'}, presence ${o.presence || '?'})`, o.usage && `usage: ${o.usage}`, o.feedback && `feedback: ${o.feedback}`, o.abandonReason && `abandoned: ${o.abandonReason}`, o.environment && `environment: ${o.environment}`, o.version && `version: ${o.version}`, o.infoDate && `date: ${o.infoDate}`, o.source && `source: ${o.source}`, o.uncertainties && `uncertainties: ${o.uncertainties}`].filter(Boolean).join(' - ') })) }}")),
        ("documents", "array", expr(f"{{{{ [...$json.sections, ...$json.inventory, ...({EVAL}.request.fictiveTool.name ? [{EVAL}.request.fictiveTool] : [])] }}}}")),
        ("contextErrors", "array", expr(f"{{{{ [\n  !String({MD} || '') ? 'Notion profile unreadable: check the page id and its sharing' : '',\n  !$('Notion - Get Inventory Items').first().json.id ? 'Notion inventory unreadable or empty: check the data source id and its sharing' : '',\n  !Object.keys(({BUILD}.machine) || {{}}).length ? 'JSON block \"machine\" is missing in the Notion profile' : ''\n].filter(Boolean) }}}}")),
        ("contextLimits", "array", expr("{{ (l => l.length ? [`Inventory: tools without state or presence are treated as unknown: ${l.join(', ')}`] : [])($json.inventory.filter(o => o.id && o.name && (!o.state || !o.presence)).map(o => o.name)) }}"))), (11, r),
        note="The documents to index are the profile sections, every inventory tool and the optional fictional test tool.")
    w.add("Split Out - Context Documents", *SPLIT_OUT, {"fieldToSplitOut": "documents", "options": {}}, (12, r))
    w.add("Simple Vector Store - Index Context", *VECTOR_STORE, {"mode": "insert", "memoryKey": STORE_KEY, "clearStore": True, "embeddingBatchSize": 100}, (13, r), **RETRY)
    w.add("Data Loader - Context Documents", *DATA_LOADER, {"dataType": "json", "jsonMode": "expressionData", "jsonData": "={{ $json.text }}", "textSplittingMode": "simple",
          "options": {"metadata": {"metadataValues": [{"name": "id", "value": "={{ $json.id }}"}, {"name": "type", "value": "={{ $json.type }}"},
                                                      {"name": "label", "value": "={{ $json.label }}"}, {"name": "url", "value": "={{ $json.url || '' }}"}]}}}, (13, r + 1.4))
    w.add("Embeddings Gemini - Documents", *EMBEDDINGS, {"modelName": MODEL}, (14, r + 1.4), **cred("gemini"))
    w.add("Set - Build Search Queries", *SET, fields(
        ("queries", "array", expr(f"{{{{ {EVAL}.repositories.map(r => [r.key, r.description, (r.topics || []).join(' '), {EVAL}.request.goal, (r.documents[0]?.text || '').slice(0, 1200)].filter(Boolean).join(' - ')) }}}}"))),
        (14, r), executeOnce=True, note="One search text per repository: its description, topics, the goal and the start of its README.")
    w.add("Split Out - Search Queries", *SPLIT_OUT, {"fieldToSplitOut": "queries", "options": {"destinationFieldName": "query"}}, (15, r))
    w.add("Simple Vector Store - Retrieve Passages", *VECTOR_STORE, {"mode": "load", "memoryKey": STORE_KEY, "prompt": "={{ $json.query }}", "topK": 6, "includeDocumentMetadata": True}, (16, r), **RETRY)
    w.add("Embeddings Gemini - Queries", *EMBEDDINGS, {"modelName": MODEL}, (16, r + 1.4), **cred("gemini"))
    w.add("Sort - Passages by Score", *SORT, {"type": "simple", "sortFieldsUi": {"sortField": [{"fieldName": "score", "order": "descending"}]}, "options": {}}, (17, r))
    w.add("Remove Duplicates - Passages", *REMOVE_DUP, {"compare": "selectedFields", "fieldsToCompare": "document.metadata.id", "options": {}}, (18, r))
    w.add("Set - Normalize Passages", *SET, fields(
        ("id", "string", expr("{{ $json.document.metadata.id }}")), ("type", "string", expr("{{ $json.document.metadata.type }}")),
        ("label", "string", expr("{{ $json.document.metadata.label }}")), ("url", "string", expr("{{ $json.document.metadata.url || '' }}")),
        ("score", "number", expr("{{ Math.round(($json.score || 0) * 1000) / 1000 }}")), ("text", "string", expr("{{ $json.document.pageContent }}")),
        ("inclusion", "string", "retrieved")), (19, r))
    w.add("Filter - Mandatory Documents", *FILTER, {"conditions": conditions(cond(expr(
        f"{{{{ (n => $json.type === 'fictional' || ($json.type === 'inventory' && n($json.name).length >= 3 && ({EVAL}.repositories.some(r => n(r.name).includes(n($json.name)) || n($json.name).includes(n(r.name))) || [].concat({BUILD}.machine.aPreserver || []).some(x => n(x).includes(n($json.name))))))({NORM}) }}}}"))), "options": {}},
        (13, r + 3), alwaysOutputData=True,
        note="Never left to chance: the tool that matches a repository name, any tool to preserve (LeRobot) and the fictional test tool are always given to the AI.")
    w.add("Set - Normalize Mandatory", *SET, fields(
        ("id", "string", expr("{{ $json.id || '' }}")), ("type", "string", expr("{{ $json.type || '' }}")), ("label", "string", expr("{{ $json.label || '' }}")),
        ("url", "string", expr("{{ $json.url || '' }}")), ("score", "number", expr("{{ 0 }}")), ("text", "string", expr("{{ $json.text || '' }}")),
        ("inclusion", "string", "mandatory")), (14, r + 3))
    w.add("Merge - Passages and Mandatory", *MERGE, {"mode": "append", "numberInputs": 2}, (20, r))
    w.add("Remove Duplicates - Context Items", *REMOVE_DUP, {"compare": "selectedFields", "fieldsToCompare": "id", "options": {}}, (21, r))
    w.add("Aggregate - Context Items", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "items", "options": {}}, (22, r))
    w.add("Set - Build Context", *SET, fields(
        ("request", "object", expr(f"{{{{ {EVAL}.request }}}}")), ("repositories", "array", expr(f"{{{{ {EVAL}.repositories }}}}")),
        ("machine", "object", expr(f"{{{{ {BUILD}.machine }}}}")), ("profileRevision", "string", expr(f"{{{{ {BUILD}.profileRevision }}}}")),
        ("passages", "array", expr("{{ $json.items.filter(p => p.id) }}")),
        ("matches", "array", expr(f"{{{{ (n => {EVAL}.repositories.flatMap(r => {BUILD}.inventory.filter(o => n(o.name).length >= 3 && (n(o.name).includes(n(r.name)) || n(r.name).includes(n(o.name)))).map(o => ({{ repository: r.key, tool: o.name, state: o.state, presence: o.presence, version: o.version, environment: o.environment }}))))({NORM}) }}}}")),
        ("inventoryCatalog", "array", expr(f"{{{{ {BUILD}.inventory.map(o => ({{ id: o.id, name: o.name, state: o.state, presence: o.presence, usage: String(o.usage || '').slice(0, 160) }})) }}}}")),
        ("retrievalMethod", "string", "vector search (Gemini embeddings, in-memory Simple Vector Store)"),
        ("contextErrors", "array", expr(f"{{{{ {BUILD}.contextErrors }}}}")), ("contextLimits", "array", expr(f"{{{{ {BUILD}.contextLimits }}}}"))), (23, r))

    w.link("Switch - Reference Outcome", "Notion - Get Profile Markdown", 0)
    w.chain("Notion - Get Profile Markdown", "Notion - Get Inventory Items", "Set - Format Inventory Items", "Aggregate - Inventory", "Set - Build Context Documents", "Split Out - Context Documents")
    w.link("Split Out - Context Documents", "Simple Vector Store - Index Context")
    w.link("Data Loader - Context Documents", "Simple Vector Store - Index Context", kind="ai_document")
    w.link("Embeddings Gemini - Documents", "Simple Vector Store - Index Context", kind="ai_embedding")
    w.chain("Simple Vector Store - Index Context", "Set - Build Search Queries", "Split Out - Search Queries", "Simple Vector Store - Retrieve Passages", "Sort - Passages by Score",
            "Remove Duplicates - Passages", "Set - Normalize Passages")
    w.link("Embeddings Gemini - Queries", "Simple Vector Store - Retrieve Passages", kind="ai_embedding")
    w.link("Set - Normalize Passages", "Merge - Passages and Mandatory", 0, 0)
    w.link("Split Out - Context Documents", "Filter - Mandatory Documents")
    w.chain("Filter - Mandatory Documents", "Set - Normalize Mandatory")
    w.link("Set - Normalize Mandatory", "Merge - Passages and Mandatory", 0, 1)
    w.chain("Merge - Passages and Mandatory", "Remove Duplicates - Context Items", "Aggregate - Context Items", "Set - Build Context")
    w.group("## 6. Personal context (RAG)\nThe Notion profile and inventory are indexed with Gemini embeddings in an in-memory vector store (template 6137 by Lucas Peyrin), then searched once per repository. The machine profile is always given in full and key tools are added even if the search misses them.",
            ["Notion - Get Profile Markdown", "Notion - Get Inventory Items", "Set - Format Inventory Items", "Aggregate - Inventory", "Set - Build Context Documents", "Split Out - Context Documents",
             "Simple Vector Store - Index Context", "Data Loader - Context Documents", "Embeddings Gemini - Documents", "Set - Build Search Queries", "Split Out - Search Queries",
             "Simple Vector Store - Retrieve Passages", "Embeddings Gemini - Queries", "Sort - Passages by Score", "Remove Duplicates - Passages", "Set - Normalize Passages",
             "Filter - Mandatory Documents", "Set - Normalize Mandatory", "Merge - Passages and Mandatory", "Remove Duplicates - Context Items", "Aggregate - Context Items", "Set - Build Context"])
