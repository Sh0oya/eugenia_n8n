"""Setup, triggers, CONFIGURATION, routing and request validation."""
from lib import *

# One place for the Data Table schemas: the setup trigger creates them, the delivery and error nodes fill them.
TABLES = {
    "analysis_history": [("requestId", "string"), ("status", "string"), ("repositoriesKey", "string"), ("versions", "string"),
                         ("reuseKey", "string"), ("goal", "string"), ("summary", "string"), ("notionPageId", "string"),
                         ("notionUrl", "string"), ("model", "string"), ("deliveryStatus", "string"), ("contextIds", "string"),
                         ("note", "string")],
    "error_incidents": [("workflowName", "string"), ("nodeName", "string"), ("errorMessage", "string"),
                        ("executionId", "string"), ("executionUrl", "string")],
}

URL_PATTERN = r"/^https:\/\/(?:www\.)?github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?(?:[/?#].*)?$/i"
CFG = "$('CONFIGURATION').first().json"


def E(js):
    return expr("{{ " + js + " }}")


def build(w):
    # ---------- setup (run once) ----------
    w.add("Manual - Setup Data Tables", "n8n-nodes-base.manualTrigger", 1, {}, (8, 3),
          note="Run once on a new instance: creates the two Data Tables used by this workflow.")
    w.add("Data Table - Create Analysis History", *TABLE, table_create("analysis_history", TABLES["analysis_history"]), (9, 3))
    w.add("Data Table - Create Error Incidents", *TABLE, table_create("error_incidents", TABLES["error_incidents"]), (10, 3))
    w.chain("Manual - Setup Data Tables", "Data Table - Create Analysis History", "Data Table - Create Error Incidents")
    w.group("## Setup\nRun the manual trigger once on a new instance. The Data Tables are then filled by the delivery and by the error handler.",
            ["Manual - Setup Data Tables", "Data Table - Create Analysis History", "Data Table - Create Error Incidents"])

    # ---------- triggers and configuration ----------
    w.add("Form - Diagnostic Request", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "basicAuth",
        "formTitle": "Ça tourne sur mon PC ?",
        "formDescription": "Diagnostic d’un ou plusieurs dépôts GitHub publics pour mon PC. Rapport en français par e-mail et dans Notion.",
        "formFields": {"values": [
            {"fieldLabel": "URL GitHub", "fieldName": "githubUrls", "fieldType": "textarea", "requiredField": True,
             "placeholder": "Une URL de dépôt public par ligne (3 maximum). Plusieurs dépôts : comparaison."},
            {"fieldLabel": "Objectif", "fieldName": "goal", "fieldType": "textarea", "placeholder": "Facultatif : à quoi doit servir l’outil ? Sinon, le profil fait foi."},
            {"fieldLabel": "Refaire l’analyse", "fieldName": "forceNew", "fieldType": "dropdown", "requiredField": True,
             "fieldOptions": {"values": [{"option": "Non"}, {"option": "Oui"}]}},
        ]},
        "options": {"buttonLabel": "Analyser", "path": "can-my-pc-run-it", "ignoreBots": True, "useWorkflowTimezone": True, "appendAttribution": False,
                    "respondWithOptions": {"values": {"respondWith": "text", "formSubmittedText": "Demande reçue. Le rapport arrive par e-mail dans quelques minutes."}}},
    }, (0, 3), webhookId=sid("webhook", "form"), **cred("basic"))
    w.add("Error Trigger - Workflow Failed", "n8n-nodes-base.errorTrigger", 1, {}, (0, 5),
          note="This workflow is its own error workflow: set it in the workflow settings once it is published.")
    w.add("CONFIGURATION", *SET, fields(
        ("notificationEmail", "string", local("email", "you@example.com")),
        ("notionProfilePageId", "string", local("notionProfilePageId", "REPLACE_WITH_PROFILE_PAGE_ID")),
        ("notionInventoryDataSourceId", "string", local("notionInventoryDataSourceId", "REPLACE_WITH_INVENTORY_DATA_SOURCE_ID")),
        ("notionAnalysesDataSourceId", "string", local("notionAnalysesDataSourceId", "REPLACE_WITH_ANALYSES_DATA_SOURCE_ID")),
        ("diagnosticModel", "string", "gemini-flash-latest"),
        ("fallbackModel", "string", "gemini-flash-lite-latest"),
        ("maxOutputTokens", "number", 32768),
        ("maxRepositories", "number", 3),
        ("maxReadmeChars", "number", 9000),
        ("maxDependencyChars", "number", 5000),
        ("maxIssues", "number", 6),
        ("schemaVersion", "string", "3.0"),
        keep=True), (1, 4), note="Single place for every setting: e-mail, Notion identifiers, Gemini models and limits.")
    w.add("Switch - Route by Trigger", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(E("$json.githubUrls !== undefined"))), "renameOutput": True, "outputKey": "request"},
        {"conditions": conditions(cond(E("$json.execution !== undefined"))), "renameOutput": True, "outputKey": "failure"},
    ]}, "options": {}}, (2, 4))
    w.link("Form - Diagnostic Request", "CONFIGURATION")
    w.link("Error Trigger - Workflow Failed", "CONFIGURATION")
    w.link("CONFIGURATION", "Switch - Route by Trigger")

    # ---------- request parsing and validation ----------
    urls = "String($json.githubUrls || '').split(/[\\s,;]+/)"
    w.add("Set - Parse and Validate Request", *SET, fields(
        ("requestId", "string", E("`req-${$now.toFormat('yyyyLLdd-HHmmss')}-${Math.random().toString(36).slice(2, 6)}`")),
        ("receivedAt", "string", E("$now.toISO()")),
        ("goal", "string", E("String($json.goal || '').trim().slice(0, 1000)")),
        ("force", "boolean", E("String($json.forceNew || '').startsWith('Oui')")),
        ("repositories", "array", E(f"{urls}.map(u => u.match({URL_PATTERN})).filter(Boolean).map(m => ({{ owner: m[1], name: m[2], key: `${{m[1]}}/${{m[2]}}`.toLowerCase(), url: `https://github.com/${{m[1]}}/${{m[2]}}` }})).filter((r, i, all) => all.findIndex(x => x.key === r.key) === i)")),
        ("errors", "array", E(f"[\n  ...{urls}.filter(Boolean).filter(u => !{URL_PATTERN}.test(u)).map(u => `Not an https GitHub repository URL: ${{u}}`),\n"
                              f"  !String($json.githubUrls || '').trim() ? 'No GitHub URL given' : '',\n"
                              f"  new Set({urls}.map(u => u.match({URL_PATTERN})).filter(Boolean).map(m => `${{m[1]}}/${{m[2]}}`.toLowerCase())).size > {CFG}.maxRepositories ? `Too many repositories (${{{CFG}.maxRepositories}} at most)` : '',\n"
                              f"  [{CFG}.notionProfilePageId, {CFG}.notionInventoryDataSourceId, {CFG}.notionAnalysesDataSourceId].some(v => String(v).startsWith('REPLACE_')) ? 'Notion identifiers must be set in CONFIGURATION' : ''\n].filter(Boolean)"))),
        (3, 3), note="One deduplicated list of public GitHub repositories, the optional goal, and every problem found in the request.")
    w.add("IF - Request Valid", *IF, {"conditions": conditions(cond(E("$json.errors.length === 0"))), "options": {}}, (4, 3))
    w.add("Stop and Error - Invalid Request", *STOP_ERROR, {"errorMessage": E("`Invalid request: ${$json.errors.join(' ; ')}`")}, (5, 4),
          note="A refused request stops here, before any AI call. The error handler of this workflow sends the reason by e-mail.")
    w.link("Switch - Route by Trigger", "Set - Parse and Validate Request", 0)
    w.chain("Set - Parse and Validate Request", "IF - Request Valid")
    w.link("IF - Request Valid", "Stop and Error - Invalid Request", 1)
    w.group("## 1. Entry and request check\nThe form and the error trigger share one CONFIGURATION node, then a switch routes each run. A request is checked before anything else: GitHub URLs, batch size, Notion identifiers.",
            ["Form - Diagnostic Request", "Error Trigger - Workflow Failed", "CONFIGURATION", "Switch - Route by Trigger", "Set - Parse and Validate Request", "IF - Request Valid", "Stop and Error - Invalid Request"])
