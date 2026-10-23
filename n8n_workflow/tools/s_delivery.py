"""Delivery: one rendering, Notion page, HTML e-mail with the JSON attached, history in a Data Table."""
from lib import *

R = "$('Code - Render Report').first().json"
D = f"{R}.diagnostic"
NOTION_PAGE = "$('Notion - Create Diagnostic Page').first().json"
FILL = "$('Set - Fill Email Template').first().json"
REPOSITORIES_KEY = f"{D}.repositories.map(r => r.repository).sort().join(' + ')"
VERSIONS = f"{D}.repositories.map(r => `${{r.repository}}@${{r.version}}`).join(' + ')"
CONTEXT_IDS = f"({D}.usedProfile.passages || []).map(p => p.id).join(',')"
REQUEST_MODE = f"({{ single: 'un', compare: 'comparer' }})[{D}.mode]"


def E(js):
    return expr("{{ " + js + " }}")


def build(w):
    d = 16
    w.add("Code - Render Report", *CODE, {"mode": "runOnceForAllItems", "jsCode": code("render-report.js")}, (13, d),
          note="Why Code: one rendering function writes the Markdown for Notion and the HTML e-mail from the same JSON, so both always say the same thing.")
    properties = [
        notion_property("Statut", "select", E(f"{D}.status === 'done' ? 'terminé' : 'échec'")),
        notion_property("Diagnostic Id", "rich_text", E(f"{D}.id")),
        notion_property("Mode", "select", E(REQUEST_MODE)),
        notion_property("Depots", "rich_text", E(REPOSITORIES_KEY)),
        notion_property("Cle", "rich_text", E(f"{D}.trace.reuseKey")),
        notion_property("Version", "rich_text", E(VERSIONS)),
        notion_property("TLDR", "rich_text", E("$json.tldr")),
        notion_property("Contexte Ids", "rich_text", E(CONTEXT_IDS)),
        notion_property("Profil Revision", "rich_text", E(f"{D}.usedProfile.profileRevision || ''")),
        notion_property("Moteur", "rich_text", E(f"`gemini / ${{{D}.trace.model}}`")),
    ]
    notion_add(w, "Notion - Create Diagnostic Page", notion_create(E("$json.title"), properties, E("$json.markdownForNotion")), (14, d),
               onError="continueRegularOutput", **RETRY, note="Creates the report page with its properties. If Notion fails, the e-mail still goes out and says so.")
    link = "`<a href=\"${u}\" style=\"color:#4f46e5;font-weight:600\">Ouvrir le rapport dans Notion ↗</a>`"
    missing = f"`<span style=\"color:#991b1b\">Page Notion non créée (${{String({NOTION_PAGE}.error?.message || {NOTION_PAGE}.error || 'erreur inconnue')}}) : le JSON joint contient le rapport complet.</span>`"
    w.add("Set - Fill Email Template", *SET, fields(
        ("emailHtml", "string", E(f"{R}.emailHtml.replace('__NOTION_BLOCK__', () => (u => u ? {link} : {missing})({NOTION_PAGE}.url))")),
        ("subject", "string", E(f"{R}.subject")),
        ("jsonText", "string", E(f"{R}.jsonText")),
        ("notionPageId", "string", E(f"{NOTION_PAGE}.id || ''")),
        ("notionUrl", "string", E(f"{NOTION_PAGE}.url || ''"))), (15, d))
    w.add("Convert to File - Diagnostic JSON", *CONVERT_FILE, {"operation": "toText", "sourceProperty": "jsonText", "binaryPropertyName": "data",
                                                                "options": {"fileName": E(f"`diagnostic-${{{D}.id}}.json`"), "encoding": "utf8"}}, (16, d),
          note="The complete diagnostic JSON becomes the attachment of the e-mail.")
    w.add("Gmail - Send Report", *GMAIL, gmail_params(E(f"{FILL}.subject"), E(f"{FILL}.emailHtml"), attachment=True), (17, d), **cred("gmail"), **RETRY)
    w.add("Data Table - Save Analysis", *TABLE, table_upsert("analysis_history", [("reuseKey", E(f"{D}.trace.reuseKey")), ("status", E(f"{D}.status"))], {
        "requestId": E(f"{D}.id"), "status": E(f"{D}.status"), "repositoriesKey": E(REPOSITORIES_KEY), "versions": E(VERSIONS),
        "reuseKey": E(f"{D}.trace.reuseKey"), "goal": E(f"{D}.goal || ''"), "summary": E(f"{R}.tldr"),
        "notionPageId": E(f"{FILL}.notionPageId"), "notionUrl": E(f"{FILL}.notionUrl"), "model": E(f"{D}.trace.model"),
        "deliveryStatus": E(f"{FILL}.notionUrl ? 'complete' : 'notion failed'"), "contextIds": E(CONTEXT_IDS),
        "note": E(f"{D}.status === 'done' ? '' : ({D}.unknowns || []).join(' ; ').slice(0, 900)")}), (18, d),
        note="History of every analysis. One row per repositories, versions and goal, and per status: a failed run never overwrites a finished report.")
    w.link("Code - Validate and Finalize Diagnostic", "Code - Render Report")
    w.chain("Code - Render Report", "Notion - Create Diagnostic Page", "Set - Fill Email Template", "Convert to File - Diagnostic JSON", "Gmail - Send Report", "Data Table - Save Analysis")
    w.group("## 6. Delivery and history\nThe report is rendered once, written to Notion and sent as an HTML e-mail with the diagnostic JSON attached. The analysis is then saved in the analysis_history Data Table, which is also what the reuse shortcut reads.",
            ["Code - Render Report", "Notion - Create Diagnostic Page", "Set - Fill Email Template", "Convert to File - Diagnostic JSON", "Gmail - Send Report", "Data Table - Save Analysis"])
