"""Entry points, CONFIGURATION, routing and request validation."""
from lib import *

# One place for the Data Table schemas: the setup trigger creates them, the nodes below fill them.
TABLES = {
    "analysis_history": [("requestId", "string"), ("status", "string"), ("mode", "string"), ("repositoriesKey", "string"),
                         ("versions", "string"), ("reuseKey", "string"), ("goal", "string"), ("summary", "string"),
                         ("notionPageId", "string"), ("notionUrl", "string"), ("costEur", "number"), ("aiCalls", "number"),
                         ("model", "string"), ("month", "string"), ("deliveryStatus", "string"), ("contextIds", "string"),
                         ("requestJson", "string"), ("previousRequestId", "string"), ("reviewState", "string"), ("profileRevision", "string"), ("note", "string")],
    "delivery_queue": [("requestId", "string"), ("channel", "string"), ("errorMessage", "string"), ("payloadJson", "string"),
                       ("notionPageId", "string"), ("notionUrl", "string"), ("status", "string")],
    "error_incidents": [("workflowName", "string"), ("nodeName", "string"), ("errorMessage", "string"),
                        ("executionId", "string"), ("executionUrl", "string"), ("aiAnalysis", "string")],
    "inventory_snapshot": [("toolId", "string"), ("name", "string"), ("state", "string"), ("presence", "string"),
                           ("version", "string"), ("environment", "string")],
}

URL_PATTERN = r"/^https:\/\/(?:www\.)?github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?(?:[/?#].*)?$/i"
REF_PATTERN = r"/^([\w.-]+\/[\w.-]+)\s*=\s*(\S+)$/"
CFG = "$('CONFIGURATION').first().json"


def build(w):
    # ---------- setup (run once) ----------
    w.add("Manual - Setup Data Tables", "n8n-nodes-base.manualTrigger", 1, {}, (0, 0),
          note="Run once on a new instance: creates the four Data Tables used by this workflow.")
    previous = "Manual - Setup Data Tables"
    for i, (table, columns) in enumerate(TABLES.items(), start=1):
        name = "Data Table - Create " + {"analysis_history": "Analysis History", "delivery_queue": "Delivery Queue",
                                           "error_incidents": "Error Incidents", "inventory_snapshot": "Inventory Snapshot"}[table]
        w.add(name, *TABLE, table_create(table, columns), (i, 0))
        w.link(previous, name)
        previous = name
    w.group("## Setup\nRun **Manual - Setup Data Tables** once on a new instance. The Data Tables are then filled by the analysis, the delivery queue, the error handler and the daily inventory check.",
            ["Manual - Setup Data Tables", "Data Table - Create Analysis History", "Data Table - Create Delivery Queue", "Data Table - Create Error Incidents", "Data Table - Create Inventory Snapshot"])

    # ---------- triggers ----------
    w.add("Form - Diagnostic Request", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "basicAuth",
        "formTitle": "Ça tourne sur mon PC ?",
        "formDescription": "Diagnostic d’un ou plusieurs dépôts GitHub publics pour mon PC. Rapport en français par e-mail et dans Notion.",
        "formFields": {"values": [
            {"fieldLabel": "Mode", "fieldName": "mode", "fieldType": "dropdown", "requiredField": True,
             "fieldOptions": {"values": [{"option": "Analyser un dépôt"}, {"option": "Analyser plusieurs dépôts séparément"}, {"option": "Comparer plusieurs dépôts"}]}},
            {"fieldLabel": "URL GitHub", "fieldName": "githubUrls", "fieldType": "textarea", "requiredField": True, "placeholder": "Une URL de dépôt public par ligne (3 maximum)"},
            {"fieldLabel": "Objectif", "fieldName": "goal", "fieldType": "textarea", "placeholder": "Facultatif : à quoi doit servir l’outil ? Sinon, le profil fait foi."},
            {"fieldLabel": "Références choisies", "fieldName": "chosenReferences", "fieldType": "textarea", "placeholder": "Seulement si on te le demande : propriétaire/dépôt=tag, une ligne par dépôt"},
            {"fieldLabel": "Fiche fictive (test)", "fieldName": "fictiveTool", "fieldType": "textarea", "placeholder": "Test uniquement : Nom | état | usage. Jamais ajoutée à l’inventaire."},
        ]},
        "options": {"buttonLabel": "Analyser", "path": "can-my-pc-run-it", "ignoreBots": True, "useWorkflowTimezone": True, "appendAttribution": False,
                    "respondWithOptions": {"values": {"respondWith": "text", "formSubmittedText": "Demande reçue. Le rapport arrive par e-mail dans quelques minutes."}}},
    }, (0, 3), webhookId=sid("webhook", "form"), **cred("basic"))
    w.add("Schedule - Daily Inventory Check", "n8n-nodes-base.scheduleTrigger", 1.2,
          {"rule": {"interval": [{"field": "days", "triggerAtHour": 8, "triggerAtMinute": 0}]}}, (0, 4))
    w.add("Manual - Replay Failed Deliveries", "n8n-nodes-base.manualTrigger", 1, {}, (0, 5),
          note="Replays the reports that Notion or Gmail could not deliver. No new AI call is made.")
    w.add("Error Trigger - Workflow Failed", "n8n-nodes-base.errorTrigger", 1, {}, (0, 6),
          note="This workflow is its own error workflow: set it in Settings, Error workflow.")

    # ---------- configuration and routing ----------
    w.add("CONFIGURATION", *SET, fields(
        ("env", "string", "dev"),
        ("notificationEmail", "string", local("email", "you@example.com")),
        ("notionProfilePageId", "string", local("notionProfilePageId", "REPLACE_WITH_PROFILE_PAGE_ID")),
        ("notionInventoryDataSourceId", "string", local("notionInventoryDataSourceId", "REPLACE_WITH_INVENTORY_DATA_SOURCE_ID")),
        ("notionAnalysesDataSourceId", "string", local("notionAnalysesDataSourceId", "REPLACE_WITH_ANALYSES_DATA_SOURCE_ID")),
        ("diagnosticModel", "string", "gemini-flash-latest"),
        ("fallbackModel", "string", "gemini-flash-lite-latest"),
        ("embeddingModel", "string", "gemini-embedding-001"),
        ("maxOutputTokens", "number", 32768),
        ("webSearchEnabled", "boolean", False),
        ("webSearchCostEur", "number", 0.03),
        ("rateInputEurPerMillion", "number", 0),
        ("rateOutputEurPerMillion", "number", 0),
        ("monthlyBudgetEur", "number", 5),
        ("maxAnalysesPerMonth", "number", 12),
        ("maxRepositories", "number", 3),
        ("devRepositoryLimit", "number", 2),
        ("maxDocuments", "number", 5),
        ("maxDocumentChars", "number", 6000),
        ("maxIssues", "number", 6),
        ("waitDays", "number", 7),
        ("reviewQueueLimit", "number", 5),
        ("schemaVersion", "string", "2.0"),
        keep=True), (1, 4),
        note="Single place for every setting. env = dev limits each request to 2 repositories; set production to lift the limit.")
    w.add("Switch - Route by Trigger", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(expr("{{ $json.githubUrls !== undefined }}"))), "renameOutput": True, "outputKey": "request"},
        {"conditions": conditions(cond(expr("{{ $json.timestamp !== undefined && $json.githubUrls === undefined }}"))), "renameOutput": True, "outputKey": "inventory"},
        {"conditions": conditions(cond(expr("{{ $json.execution !== undefined }}"))), "renameOutput": True, "outputKey": "failure"},
        {"conditions": conditions(cond(expr("{{ $json.githubUrls === undefined && $json.timestamp === undefined && $json.execution === undefined }}"))), "renameOutput": True, "outputKey": "replay"},
    ]}, "options": {}}, (2, 4))
    for trigger in ("Form - Diagnostic Request", "Schedule - Daily Inventory Check", "Manual - Replay Failed Deliveries", "Error Trigger - Workflow Failed"):
        w.link(trigger, "CONFIGURATION")
    w.link("CONFIGURATION", "Switch - Route by Trigger")
    w.group("## 1. Entry points and CONFIGURATION\nFour triggers share one configuration node, then one switch routes each run: a diagnostic request, the daily inventory check, a delivery replay or a failure.",
            ["Form - Diagnostic Request", "Schedule - Daily Inventory Check", "Manual - Replay Failed Deliveries", "Error Trigger - Workflow Failed", "CONFIGURATION", "Switch - Route by Trigger"])

    # ---------- request parsing and validation ----------
    w.add("Set - Parse Request", *SET, fields(
        ("requestId", "string", expr("{{ `req-${$now.toFormat('yyyyLLdd-HHmmss')}-${Math.random().toString(36).slice(2, 6)}` }}")),
        ("receivedAt", "string", expr("{{ $now.toISO() }}")),
        ("origin", "string", expr("{{ $json.origin || 'form' }}")),
        ("mode", "string", expr("{{ ({ 'Analyser un dépôt': 'single', 'Analyser plusieurs dépôts séparément': 'separate', 'Comparer plusieurs dépôts': 'compare' })[String($json.mode || '').trim()] || (['single', 'separate', 'compare'].includes($json.mode) ? $json.mode : '') }}")),
        ("goal", "string", expr("{{ String($json.goal || '').trim().slice(0, 1000) }}")),
        ("repositories", "array", expr("{{ String($json.githubUrls || '').split(/[\\s,;]+/).map(u => u.match(" + URL_PATTERN + ")).filter(Boolean).map(m => ({ owner: m[1], name: m[2], key: `${m[1]}/${m[2]}`.toLowerCase(), url: `https://github.com/${m[1]}/${m[2]}` })).filter((r, i, all) => all.findIndex(x => x.key === r.key) === i) }}")),
        ("invalidUrls", "array", expr("{{ String($json.githubUrls || '').split(/[\\s,;]+/).filter(Boolean).filter(u => !" + URL_PATTERN + ".test(u)) }}")),
        ("manualRefs", "object", expr("{{ Object.fromEntries(String($json.chosenReferences || '').split(/\\r?\\n/).map(l => l.trim().match(" + REF_PATTERN + ")).filter(Boolean).map(m => [m[1].toLowerCase(), m[2]])) }}")),
        ("invalidRefs", "array", expr("{{ String($json.chosenReferences || '').split(/\\r?\\n/).map(l => l.trim()).filter(l => l && !" + REF_PATTERN + ".test(l)) }}")),
        ("fictiveRaw", "string", expr("{{ String($json.fictiveTool || '').trim() }}")),
        ("fictiveTool", "object", expr("{{ (p => p[0] ? { id: 'fictional-tool', type: 'fictional', name: p[0], state: p[1] || 'installed', presence: 'fictional', usage: p.slice(2).join(' | '), label: `${p[0]} (FICTIONAL TEST TOOL)`, text: `FICTIONAL TEST TOOL - ${p[0]} (${p[1] || 'installed'}) - usage: ${p.slice(2).join(' | ')}` } : {})(String($json.fictiveTool || '').split('|').map(s => s.trim())) }}")),
        ("replacesId", "string", expr("{{ $json.replacesId || '' }}")),
        ("previousUrl", "string", expr("{{ $json.previousUrl || '' }}")),
    ), (3, 3), note="Normalizes the form: one deduplicated list of public GitHub repositories, the mode, the optional goal and the chosen references.")
    w.add("Set - Validate Request", *SET, fields(
        ("errors", "array", expr("{{ [\n  ...$json.invalidUrls.map(u => `Not an https GitHub repository URL: ${u}`),\n  ...$json.invalidRefs.map(l => `Unreadable reference (expected owner/repo=tag): ${l}`),\n  !$json.mode ? 'Unknown mode' : '',\n  !$json.repositories.length ? 'No valid GitHub repository' : '',\n  $json.mode === 'single' && $json.repositories.length > 1 ? 'The single mode expects one distinct repository' : '',\n  $json.mode && $json.mode !== 'single' && $json.repositories.length === 1 ? 'This mode expects at least two distinct repositories: choose the single mode' : '',\n  $json.repositories.length > $('CONFIGURATION').first().json.maxRepositories ? `Batch too large: ${$json.repositories.length} repositories for ${$('CONFIGURATION').first().json.maxRepositories} at most` : '',\n  ...Object.keys($json.manualRefs).filter(k => !$json.repositories.some(r => r.key === k)).map(k => `Reference given for a repository outside the batch: ${k}`),\n  $json.fictiveRaw && !$json.fictiveTool.name ? 'Fictional tool: the name is required (format: Name | state | usage)' : '',\n  [$('CONFIGURATION').first().json.notionProfilePageId, $('CONFIGURATION').first().json.notionInventoryDataSourceId, $('CONFIGURATION').first().json.notionAnalysesDataSourceId].some(v => String(v).startsWith('REPLACE_')) ? 'Notion identifiers must be set in CONFIGURATION' : ''\n].filter(Boolean) }}")),
        ("request", "object", expr("{{ ({ id: $json.requestId, mode: $json.mode, goal: $json.goal, origin: $json.origin, receivedAt: $json.receivedAt, manualRefs: $json.manualRefs, fictiveTool: $json.fictiveTool, replacesId: $json.replacesId, previousUrl: $json.previousUrl, rawUrls: $json.repositories.map(r => r.url) }) }}")),
        keep=True), (4, 3))
    w.add("IF - Request Valid", *IF, {"conditions": conditions(cond(expr("{{ $json.errors.length === 0 }}"))), "options": {}}, (5, 3))
    w.add("Gmail - Send Request Refusal", *GMAIL, gmail_params("Demande de diagnostic refusée",
          expr("{{ `<p>La demande n’a pas été lancée. Aucun appel IA n’a été fait.</p><ul>${$json.errors.map(e => `<li>${e.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</li>`).join('')}</ul><p>Corriger puis renvoyer le formulaire.</p>` }}")),
          (5, 4), **cred("gmail"), **RETRY)
    w.add("Data Table - Log Refused Request", *TABLE, table_insert("analysis_history", {
        "requestId": expr("{{ $('Set - Validate Request').first().json.requestId }}"), "status": "refused",
        "mode": expr("{{ $('Set - Validate Request').first().json.mode }}"),
        "note": expr("{{ $('Set - Validate Request').first().json.errors.join(' ; ').slice(0, 900) }}"),
        "month": expr("{{ $now.toFormat('yyyy-LL') }}"), "costEur": 0, "aiCalls": 0}), (6, 4))
    w.link("Switch - Route by Trigger", "Set - Parse Request", 0)
    w.chain("Set - Parse Request", "Set - Validate Request", "IF - Request Valid")
    w.link("IF - Request Valid", "Gmail - Send Request Refusal", 1)
    w.link("Gmail - Send Request Refusal", "Data Table - Log Refused Request")
    w.group("## 2. Request parsing and validation\nDuplicate URLs are merged, the mode and the batch size are checked, and a refused request is answered by e-mail and logged. No AI call happens before this point.",
            ["Set - Parse Request", "Set - Validate Request", "IF - Request Valid", "Gmail - Send Request Refusal", "Data Table - Log Refused Request"])
