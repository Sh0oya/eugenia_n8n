"""Delivery: one rendering, Notion page, HTML e-mail with the JSON attached, dead letter queue, replay, history in the Data Tables."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
R = "$('Code - Render Report').first().json"
D = f"{R}.diagnostic"
FILL = "$('Set - Fill Email Template').first().json"
SUMMARY = "$('Set - Delivery Summary').first().json"
REPOSITORIES_KEY = f"{D}.repositories.map(r => r.repository).sort().join(' + ')"
VERSIONS = f"{D}.repositories.map(r => `${{r.repository}}@${{r.version}} (${{String(r.commit).slice(0, 7)}})`).join(' + ')"
CONTEXT_IDS = f"({D}.usedProfile.passages || []).map(p => p.id).join(',')"
REQUEST_JSON = (f"JSON.stringify({{ mode: {D}.mode, urls: {D}.repositories.map(r => r.url), goal: {D}.goal || '', "
                f"manualRefs: Object.fromEntries({D}.repositories.filter(r => r.manualReference).map(r => [r.repository, r.version])) }})")
MONTH = f"DateTime.fromISO({D}.date).setZone('Europe/Paris').toFormat('yyyy-LL')"


def E(js):
    return expr("{{ " + js + " }}")


def queue_row(channel, error):
    return table_insert("delivery_queue", {
        "requestId": E(f"{D}.id"), "channel": channel, "errorMessage": error,
        "payloadJson": E(f"JSON.stringify({{ diagnostic: {D} }})"),
        "notionPageId": E(f"{FILL}.notionPageId") if channel == "email" else "", "notionUrl": E(f"{FILL}.notionUrl") if channel == "email" else "",
        "status": "to replay"})


def build(w):
    d = 27
    e = d + 3.5

    # ---------- replay entry ----------
    w.add("Data Table - Get Queued Deliveries", *TABLE, table_get("delivery_queue", [("status", "to replay")]), (3, 6),
          note="Replay: the diagnostic is restored from the queue, so no new AI call is made.")
    w.add("Set - Restore Delivery", *SET, fields(
        ("diagnostic", "object", E("JSON.parse($json.payloadJson).diagnostic")),
        ("replayRowId", "number", E("$json.id")),
        ("existingPageId", "string", E("$json.notionPageId || ''")),
        ("existingPageUrl", "string", E("$json.notionUrl || ''"))), (4, 6))
    w.link("Switch - Route by Trigger", "Data Table - Get Queued Deliveries", 3)
    w.chain("Data Table - Get Queued Deliveries", "Set - Restore Delivery", "Code - Render Report")
    w.group("## Replay of failed deliveries\nThe Manual trigger reads the dead letter queue (Data Table delivery_queue) and sends the stored diagnostic through the same delivery nodes. The Notion page that already exists is reused.",
            ["Data Table - Get Queued Deliveries", "Set - Restore Delivery"])

    # ---------- rendering and Notion ----------
    w.add("Code - Render Report", *CODE, {"mode": "runOnceForAllItems", "jsCode": code("render-report.js")}, (7, d),
          note="Why Code: one rendering function writes the Markdown for Notion and the HTML e-mail from the same JSON, so both always say the same thing.")
    w.add("IF - Notion Page Exists", *IF, {"conditions": conditions(cond(E("!!$json.existingPageId"))), "options": {}}, (8, d))
    w.add("Set - Reuse Notion Page", *SET, fields(("notionPageId", "string", E("$json.existingPageId")), ("notionUrl", "string", E("$json.existingPageUrl")), ("notionError", "string", "")), (9, d - 0.9))
    properties = [
        notion_property("Statut", "select", E(f"{D}.status === 'done' ? 'terminé' : 'échec'")),
        notion_property("Diagnostic Id", "rich_text", E(f"{D}.id")),
        notion_property("Mode", "select", E(f"({{ single: 'un', separate: 'plusieurs', compare: 'comparer' }})[{D}.mode]")),
        notion_property("Depots", "rich_text", E(REPOSITORIES_KEY)),
        notion_property("Cle", "rich_text", E(f"{D}.trace.reuseKey")),
        notion_property("Version", "rich_text", E(VERSIONS)),
        notion_property("TLDR", "rich_text", E("$json.tldr")),
        notion_property("Cout EUR", "number", E(f"{D}.trace.estimatedCostEur")),
        notion_property("Livraison", "select", "en cours"),
        notion_property("Contexte Ids", "rich_text", E(CONTEXT_IDS)),
        notion_property("Profil Revision", "rich_text", E(f"{D}.usedProfile.profileRevision || ''")),
        notion_property("Moteur", "rich_text", E(f"`gemini / ${{{D}.trace.model}}`")),
        notion_property("Demande JSON", "rich_text", E(f"{REQUEST_JSON}.slice(0, 1900)")),
        notion_property("Precedent", "url", E(f"{D}.previousAnalysisUrl || ''"), ignoreIfEmpty=True),
    ]
    notion_add(w, "Notion - Create Diagnostic Page", notion_create(E("$json.title"), properties, E("$json.markdownForNotion")), (9, d + 0.3),
               onError="continueErrorOutput", **RETRY, note="Creates the report page with its properties. If Notion fails, the diagnostic is queued and the e-mail still goes out.")
    w.add("Set - Keep Notion Link", *SET, fields(("notionPageId", "string", E("$json.id")), ("notionUrl", "string", E("$json.url")), ("notionError", "string", "")), (10, d))
    w.add("Data Table - Queue Notion Failure", *TABLE, queue_row("notion", E("String($json.error?.message || $json.error || 'Notion error').slice(0, 500)")), (10, d + 1.2))
    w.add("Set - Note Missing Link", *SET, fields(
        ("notionPageId", "string", ""), ("notionUrl", "string", ""),
        ("notionError", "string", E("String($('Notion - Create Diagnostic Page').first(1).json.error?.message || 'Notion error')"))), (11, d + 1.2))
    block = ("`<a href=\"${$json.notionUrl}\" style=\"color:#4f46e5;font-weight:600\">Ouvrir le rapport dans Notion ↗</a>`")
    missing = "`<span style=\"color:#991b1b\">Page Notion non créée (${$json.notionError}) : le diagnostic est en file de rejeu.</span>`"
    w.add("Set - Fill Email Template", *SET, fields(
        ("emailHtml", "string", E(f"{R}.emailHtml.replace('__NOTION_BLOCK__', () => $json.notionUrl ? {block} : {missing})")),
        ("subject", "string", E(f"{R}.subject")),
        ("notionPageId", "string", E("$json.notionPageId")), ("notionUrl", "string", E("$json.notionUrl")), ("notionError", "string", E("$json.notionError"))), (12, d))
    w.add("Set - Isolate Diagnostic", *SET, {"mode": "raw", "jsonOutput": E(f"JSON.stringify({D})"), "options": {}}, (13, d),
          note="Only the diagnostic JSON goes into the attachment.")
    w.add("Convert to File - Diagnostic JSON", *CONVERT_FILE, {"operation": "toJson", "mode": "each", "binaryPropertyName": "data",
                                                                "options": {"fileName": E(f"`diagnostic-${{{D}.id}}.json`"), "format": True}}, (14, d))
    w.add("Gmail - Send Report", *GMAIL, gmail_params(E(f"{FILL}.subject"), E(f"{FILL}.emailHtml"), attachment=True), (15, d),
          onError="continueErrorOutput", **cred("gmail"), **RETRY)
    w.add("Set - Mark Email Sent", *SET, fields(("emailOk", "boolean", E("true")), ("emailError", "string", "")), (16, d - 0.8))
    w.add("Set - Mark Email Failed", *SET, fields(("emailOk", "boolean", E("false")), ("emailError", "string", E("String($json.error?.message || $json.error || 'Gmail error').slice(0, 500)"))), (16, d + 0.8))
    w.add("Data Table - Queue Email Failure", *TABLE, queue_row("email", E("$json.emailError")), (17, d + 0.8))
    w.link("Code - Validate and Finalize Diagnostic", "Code - Render Report")
    w.link("Code - Render Report", "IF - Notion Page Exists")
    w.link("IF - Notion Page Exists", "Set - Reuse Notion Page", 0)
    w.link("IF - Notion Page Exists", "Notion - Create Diagnostic Page", 1)
    w.link("Notion - Create Diagnostic Page", "Set - Keep Notion Link", 0)
    w.link("Notion - Create Diagnostic Page", "Data Table - Queue Notion Failure", 1)
    w.chain("Data Table - Queue Notion Failure", "Set - Note Missing Link")
    for source in ("Set - Reuse Notion Page", "Set - Keep Notion Link", "Set - Note Missing Link"):
        w.link(source, "Set - Fill Email Template")
    w.chain("Set - Fill Email Template", "Set - Isolate Diagnostic", "Convert to File - Diagnostic JSON", "Gmail - Send Report")
    w.link("Gmail - Send Report", "Set - Mark Email Sent", 0)
    w.link("Gmail - Send Report", "Set - Mark Email Failed", 1)
    w.chain("Set - Mark Email Failed", "Data Table - Queue Email Failure")
    w.group("## 9. Delivery\nThe report is rendered once, then written to Notion and sent as an HTML e-mail with the diagnostic JSON attached. A Notion or Gmail failure is kept in the delivery_queue Data Table (dead letter queue) and can be replayed without any new AI call.",
            ["Code - Render Report", "IF - Notion Page Exists", "Set - Reuse Notion Page", "Notion - Create Diagnostic Page", "Set - Keep Notion Link", "Data Table - Queue Notion Failure", "Set - Note Missing Link",
             "Set - Fill Email Template", "Set - Isolate Diagnostic", "Convert to File - Diagnostic JSON", "Gmail - Send Report", "Set - Mark Email Sent", "Set - Mark Email Failed", "Data Table - Queue Email Failure"])

    # ---------- summary and history ----------
    w.add("Set - Delivery Summary", *SET, fields(
        ("notionPageId", "string", E(f"{FILL}.notionPageId")), ("notionUrl", "string", E(f"{FILL}.notionUrl")),
        ("emailOk", "boolean", E("$('Set - Mark Email Sent').isExecuted")),
        ("complete", "boolean", E(f"!!{FILL}.notionPageId && $('Set - Mark Email Sent').isExecuted")),
        ("deliveryStatus", "string", E(f"!{FILL}.notionPageId ? 'notion failed' : $('Set - Mark Email Sent').isExecuted ? 'complete' : 'email failed'")),
        ("message", "string", E(f"`Incomplete delivery of ${{{D}.id}}: ${{[{FILL}.notionPageId ? '' : `Notion (${{{FILL}.notionError}})`, $('Set - Mark Email Sent').isExecuted ? '' : `e-mail (${{$('Set - Mark Email Failed').first().json.emailError}})`].filter(Boolean).join(' and ')}} failed. The diagnostic is kept in the delivery_queue Data Table: run the Manual replay trigger, no new AI call.`"))), (7, e))
    w.add("Data Table - Save Analysis", *TABLE, table_upsert("analysis_history", [("requestId", E(f"{D}.id"))], {
        "requestId": E(f"{D}.id"), "status": E(f"{D}.status"), "mode": E(f"{D}.mode"), "repositoriesKey": E(REPOSITORIES_KEY), "versions": E(VERSIONS),
        "reuseKey": E(f"{D}.trace.reuseKey"), "goal": E(f"{D}.goal || ''"), "summary": E(f"{R}.tldr"),
        "notionPageId": E(f"{SUMMARY}.notionPageId"), "notionUrl": E(f"{SUMMARY}.notionUrl"),
        "costEur": E(f"{D}.trace.estimatedCostEur"), "aiCalls": 1, "model": E(f"{D}.trace.model"), "month": E(MONTH),
        "deliveryStatus": E(f"{SUMMARY}.deliveryStatus"), "contextIds": E(CONTEXT_IDS), "requestJson": E(REQUEST_JSON),
        "previousRequestId": E(f"{D}.previousAnalysisId || ''"), "reviewState": "", "profileRevision": E(f"{D}.usedProfile.profileRevision || ''"),
        "note": E(f"{D}.status === 'done' ? '' : ({D}.unknowns || []).join(' ; ').slice(0, 900)")}), (8, e),
        note="History of every analysis: cost, calls, delivery status and the context used. The monthly budget and the re-examination queue read this table.")
    w.add("IF - Is Replay", *IF, {"conditions": conditions(cond(E(f"{R}.replayRowId !== null"))), "options": {}}, (9, e))
    w.add("Data Table - Mark Queue Row Replayed", *TABLE, table_update("delivery_queue", [("id", E(f"{R}.replayRowId"))], {"status": E(f"{SUMMARY}.complete ? 'replayed' : 'to replay'")}), (10, e - 0.9))
    w.add("IF - Notion Page Created", *IF, {"conditions": conditions(cond(E(f"!!{SUMMARY}.notionPageId"))), "options": {}}, (11, e))
    notion_add(w, "Notion - Mark Delivery Status", notion_update(E(f"{SUMMARY}.notionPageId"), [notion_property("Livraison", "select", E(f"{SUMMARY}.emailOk ? 'complète' : 'e-mail en échec'"))]),
               (12, e - 0.9), onError="continueRegularOutput", **RETRY)
    w.add("IF - Previous Analysis to Archive", *IF, {"conditions": conditions(cond(E(f"!!{D}.previousAnalysisId && {D}.status === 'done'"))), "options": {}}, (13, e - 0.9))
    w.add("Data Table - Mark Previous Superseded", *TABLE, table_update("analysis_history", [("requestId", E(f"{D}.previousAnalysisId")), ("status", "done")], {"status": "superseded", "reviewState": ""}), (14, e - 1.8),
          alwaysOutputData=True, note="The replaced analysis stays in the history, it is never deleted.")
    notion_add(w, "Notion - Archive Previous Analysis", notion_update(E("$json.notionPageId"), [notion_property("Statut", "select", "historique"), notion_property("Remplacee Par", "url", E(f"{SUMMARY}.notionUrl"))]),
               (15, e - 1.8), onError="continueRegularOutput", **RETRY)
    w.add("IF - Delivery Complete", *IF, {"conditions": conditions(cond(E(f"{SUMMARY}.complete"))), "options": {}}, (16, e))
    w.add("Stop and Error - Incomplete Delivery", *STOP_ERROR, {"errorMessage": E(f"{SUMMARY}.message")}, (17, e + 0.9),
          note="An incomplete delivery is never silent: the execution fails and the error handler of this workflow sends the alert.")
    w.link("Set - Mark Email Sent", "Set - Delivery Summary")
    w.link("Data Table - Queue Email Failure", "Set - Delivery Summary")
    w.chain("Set - Delivery Summary", "Data Table - Save Analysis", "IF - Is Replay")
    w.link("IF - Is Replay", "Data Table - Mark Queue Row Replayed", 0)
    w.link("IF - Is Replay", "IF - Notion Page Created", 1)
    w.link("Data Table - Mark Queue Row Replayed", "IF - Notion Page Created")
    w.link("IF - Notion Page Created", "Notion - Mark Delivery Status", 0)
    w.link("IF - Notion Page Created", "IF - Delivery Complete", 1)
    w.chain("Notion - Mark Delivery Status", "IF - Previous Analysis to Archive")
    w.link("IF - Previous Analysis to Archive", "Data Table - Mark Previous Superseded", 0)
    w.link("IF - Previous Analysis to Archive", "IF - Delivery Complete", 1)
    w.chain("Data Table - Mark Previous Superseded", "Notion - Archive Previous Analysis", "IF - Delivery Complete")
    w.link("IF - Delivery Complete", "Stop and Error - Incomplete Delivery", 1)
    w.group("## 10. History and delivery status\nEvery analysis is saved in the analysis_history Data Table (upsert on the request id). The Notion page gets its delivery status, a replaced analysis moves to history, and an incomplete delivery ends in an error.",
            ["Set - Delivery Summary", "Data Table - Save Analysis", "IF - Is Replay", "Data Table - Mark Queue Row Replayed", "IF - Notion Page Created", "Notion - Mark Delivery Status",
             "IF - Previous Analysis to Archive", "Data Table - Mark Previous Superseded", "Notion - Archive Previous Analysis", "IF - Delivery Complete", "Stop and Error - Incomplete Delivery"])
