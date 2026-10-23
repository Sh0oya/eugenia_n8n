"""Triggers, CONFIGURATION, routing and request validation."""
from lib import *

RESERVED = "orgs|users|topics|features|sponsors|marketplace|collections|settings|apps|about|pricing|login|search|explore|trending|notifications"
URL_PATTERN = r"/^https:\/\/(?:www\.)?github\.com\/(?!(?:" + RESERVED + r")\/)([\w.-]+)\/([\w.-]*?[\w-])(?:\.git)?\/?(?:[/?#].*)?$/i"
CFG = "$('CONFIGURATION').first().json"


def E(js):
    return expr("{{ " + js + " }}")


def build(w):
    # ---------- triggers and configuration ----------
    w.add("Form - Diagnostic Request", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "basicAuth",
        "formTitle": "Ça tourne sur mon PC ?",
        "formDescription": "Diagnostic d’un dépôt GitHub public pour mon PC. Rapport en français par e-mail et dans Notion.",
        "formFields": {"values": [
            {"fieldLabel": "URL GitHub", "fieldName": "githubUrl", "fieldType": "text", "requiredField": True,
             "placeholder": "L’URL d’un dépôt public, par exemple https://github.com/huggingface/lerobot"},
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
        ("env", "string", "production"),
        ("limitItems", "number", 3),
        ("notificationEmail", "string", local("email", "you@example.com")),
        ("notionProfilePageId", "string", local("notionProfilePageId", "REPLACE_WITH_PROFILE_PAGE_ID")),
        ("notionInventoryDataSourceId", "string", local("notionInventoryDataSourceId", "REPLACE_WITH_INVENTORY_DATA_SOURCE_ID")),
        ("notionAnalysesDataSourceId", "string", local("notionAnalysesDataSourceId", "REPLACE_WITH_ANALYSES_DATA_SOURCE_ID")),
        ("diagnosticModel", "string", "gemini-flash-latest"),
        ("fallbackModel", "string", "gemini-flash-lite-latest"),
        ("maxOutputTokens", "number", 32768),
        ("maxReadmeChars", "number", 9000),
        ("maxDependencyChars", "number", 5000),
        ("schemaVersion", "string", "4.0"),
        keep=True), (1, 4), note="Single place for every setting: environment (production, or test with an item limit), e-mail, Notion identifiers, Gemini models and limits.")
    w.add("Switch - Route by Trigger", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(E("$json.githubUrl !== undefined"))), "renameOutput": True, "outputKey": "request"},
        {"conditions": conditions(cond(E("$json.execution !== undefined"))), "renameOutput": True, "outputKey": "failure"},
    ]}, "options": {}}, (2, 4))
    w.link("Form - Diagnostic Request", "CONFIGURATION")
    w.link("Error Trigger - Workflow Failed", "CONFIGURATION")
    w.link("CONFIGURATION", "Switch - Route by Trigger")

    # ---------- request parsing and validation ----------
    urls = "String($json.githubUrl || '').split(/[\\s,;]+/).filter(Boolean)"
    w.add("Set - Parse and Validate Request", *SET, fields(
        ("requestId", "string", E("`req-${$now.toFormat('yyyyLLdd-HHmmss')}-${Math.random().toString(36).slice(2, 6)}`")),
        ("receivedAt", "string", E("$now.toISO()")),
        ("goal", "string", E(f"{CLEAN}(String($json.goal || '').trim().slice(0, 1000))")),
        ("force", "boolean", E("String($json.forceNew || '').startsWith('Oui')")),
        ("repository", "object", E(f"(m => m ? ({{ owner: m[1], name: m[2], key: `${{m[1]}}/${{m[2]}}`.toLowerCase(), url: `https://github.com/${{m[1]}}/${{m[2]}}` }}) : {{}})({urls}.length === 1 ? {urls}[0].match({URL_PATTERN}) : null)")),
        ("errors", "array", E(f"[\n  !String($json.githubUrl || '').trim() ? 'No GitHub URL given' : '',\n"
                              f"  {urls}.length > 1 ? `One repository per request (${{{urls}.length}} links given)` : '',\n"
                              f"  {urls}.length === 1 && !{URL_PATTERN}.test({urls}[0]) ? `Not an https GitHub repository URL: ${{{urls}[0]}}` : '',\n"
                              f"  [{CFG}.notionProfilePageId, {CFG}.notionInventoryDataSourceId, {CFG}.notionAnalysesDataSourceId].some(v => String(v).startsWith('REPLACE_')) ? 'Notion identifiers must be set in CONFIGURATION' : ''\n].filter(Boolean)"))),
        (3, 3), note="The repository to examine, the optional goal, and every problem found in the request.")
    w.add("IF - Request Valid", *IF, {"conditions": conditions(cond(E("$json.errors.length === 0"))), "options": {}}, (4, 3))
    w.add("Stop and Error - Invalid Request", *STOP_ERROR, {"errorMessage": E("`Invalid request: ${$json.errors.join(' ; ')}`")}, (5, 4),
          note="A refused request stops here, before any AI call. The error handler of this workflow sends the reason by e-mail.")
    w.link("Switch - Route by Trigger", "Set - Parse and Validate Request", 0)
    w.chain("Set - Parse and Validate Request", "IF - Request Valid")
    w.link("IF - Request Valid", "Stop and Error - Invalid Request", 1)
    w.group("## 1. Entry and request check\nThe form and the error trigger share one CONFIGURATION node, then a switch routes each run. A request is checked before anything else: one GitHub repository URL, Notion identifiers.",
            ["Form - Diagnostic Request", "Error Trigger - Workflow Failed", "CONFIGURATION", "Switch - Route by Trigger", "Set - Parse and Validate Request", "IF - Request Valid", "Stop and Error - Invalid Request"])
