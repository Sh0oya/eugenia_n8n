"""Daily inventory monitoring: snapshot comparison, analyses to re-examine, one re-examination per day."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
CMP = "$('Compare Datasets - Detect Changes')"
LIST = "$('Set - List Changes').first().json"


def E(js):
    return expr("{{ " + js + " }}")


def rich(prop):
    return f"($json.properties?.['{prop}']?.rich_text || []).map(t => t.plain_text).join('')"


def build(w):
    m = 35
    notion_add(w, "Notion - Get Current Inventory", {"resource": "databasePage", "operation": "getAll", "dataSourceId": locator(expr(f"{{{{ {CFG}.notionInventoryDataSourceId }}}}")),
                                                     "returnAll": True, "filterType": "none", "simple": False, "options": {}},
               (3, m), alwaysOutputData=True, executeOnce=True, onError="continueRegularOutput", **RETRY)
    w.add("Set - Format Snapshot Items", *SET, fields(
        ("toolId", "string", E("$json.id || ''")),
        ("name", "string", E("($json.properties?.Nom?.title || []).map(t => t.plain_text).join('')")),
        ("state", "string", E("$json.properties?.Etat?.select?.name || ''")),
        ("presence", "string", E("$json.properties?.Presence?.select?.name || ''")),
        ("version", "string", E(rich("Version"))),
        ("environment", "string", E(rich("Environnement")))), (4, m))
    w.add("Data Table - Get Last Snapshot", *TABLE, table_get("inventory_snapshot"), (4, m + 1.3), alwaysOutputData=True, executeOnce=True)
    w.add("Compare Datasets - Detect Changes", *COMPARE, {"mergeByFields": {"values": [{"field1": "toolId", "field2": "toolId"}]}, "options": {"skipFields": "id,createdAt,updatedAt"}}, (5, m),
          note="Compares today's Notion inventory with yesterday's snapshot on state, presence, version and environment (template 5999 by Lucas Peyrin).")
    w.add("Merge - Compare Outputs", *MERGE, {"mode": "append", "numberInputs": 4}, (6, m), note="Synchronization point: the next nodes run once, after the comparison is complete.")
    w.add("Data Table - Get Analyses to Watch", *TABLE, table_get("analysis_history", [("status", "done")]), (7, m), alwaysOutputData=True, executeOnce=True)
    w.add("Aggregate - Analyses", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "analyses", "options": {}}, (8, m))
    notion_add(w, "Notion - Get Profile for Monitoring", {"resource": "block", "operation": "getMarkdown", "blockId": locator(expr(f"{{{{ {CFG}.notionProfilePageId }}}}")), "includeTranscript": False},
               (9, m), executeOnce=True, onError="continueRegularOutput", **RETRY)
    w.add("Set - List Changes", *SET, fields(
        ("readable", "boolean", E("$('Set - Format Snapshot Items').all().some(i => i.json.toolId)")),
        ("snapshotEmpty", "boolean", E("$('Data Table - Get Last Snapshot').all().filter(i => i.json.toolId).length === 0")),
        ("changes", "array", E(f"$('Set - Format Snapshot Items').all().some(i => i.json.toolId) ? [\n  ...{CMP}.all(0).map(i => ({{ toolId: i.json.toolId, name: i.json.name, nature: 'added' }})),\n"
                               f"  ...{CMP}.all(2).map(i => ({{ toolId: i.json.keys?.toolId, name: i.json.same?.name || i.json.different?.name?.inputs?.input1 || '', nature: `changed: ${{Object.keys(i.json.different || {{}}).join(', ')}}` }})),\n"
                               f"  ...{CMP}.all(3).map(i => ({{ toolId: i.json.toolId, name: i.json.name, nature: 'removed' }}))\n].filter(c => c.toolId) : []")),
        ("profileRevision", "string", E("(() => { try { return JSON.parse(($json.markdown || '').match(/```json\\s*([\\s\\S]*?)```/)[1]).revision || ''; } catch (e) { return ''; } })()")),
        ("analyses", "array", E("$('Aggregate - Analyses').first().json.analyses.filter(a => a.requestId).map(a => ({ requestId: a.requestId, notionPageId: a.notionPageId, notionUrl: a.notionUrl, createdAt: a.createdAt, reviewState: a.reviewState || '', "
                                 "repositoriesKey: a.repositoriesKey, profileRevision: a.profileRevision || '', contextIds: String(a.contextIds || '').split(',').filter(Boolean), "
                                 "request: (() => { try { return JSON.parse(a.requestJson); } catch (e) { return {}; } })() }))"))), (10, m))
    w.add("Set - Find Analyses to Review", *SET, fields(
        ("touched", "array", E("$json.snapshotEmpty ? [] : $json.analyses.filter(a => a.reviewState !== 'to review').map(a => ({ ...a, reasons: [\n"
                               "  ...$json.changes.filter(c => a.contextIds.includes(c.toolId)).map(c => `${c.name} ${c.nature}`),\n"
                               "  $json.profileRevision && a.profileRevision && a.profileRevision !== $json.profileRevision ? `profile revised (${a.profileRevision} to ${$json.profileRevision})` : ''\n"
                               "].filter(Boolean) })).filter(a => a.reasons.length)")),
        ("withoutAnalysis", "array", E("$json.snapshotEmpty ? [] : $json.changes.filter(c => !$json.analyses.some(a => a.contextIds.includes(c.toolId)))")),
        keep=True), (11, m), note="An analysis is touched when it used a changed tool, or when the profile revision changed. The first run only stores the snapshot.")
    w.add("Set - Plan Review Queue", *SET, fields(
        ("queue", "array", E("[...$json.analyses.filter(a => a.reviewState === 'to review'), ...$json.touched].sort((x, y) => String(x.createdAt).localeCompare(String(y.createdAt)))")),
        ("toRelaunch", "object", E("([...$json.analyses.filter(a => a.reviewState === 'to review'), ...$json.touched].sort((x, y) => String(x.createdAt).localeCompare(String(y.createdAt))).find(a => a.request?.urls?.length)) || {}")),
        ("action", "string", E(f"!$json.readable ? 'unreadable' : (q => q.length > {CFG}.reviewQueueLimit ? 'reduce' : q.some(a => a.request?.urls?.length) ? 'relaunch' : $json.withoutAnalysis.length ? 'inform' : 'none')([...$json.analyses.filter(a => a.reviewState === 'to review'), ...$json.touched])")),
        keep=True), (12, m), note="At most one re-examination per day, and the budget is checked again by the guardrails. A queue above the configured limit asks for a reduction instead.")
    w.add("Set - Write Message", *SET, fields(
        ("emailSubject", "string", E("$json.action === 'reduce' ? `Réexamens : lot trop volumineux (${$json.queue.length})` : $json.action === 'relaunch' ? `Réexamens planifiés (${$json.queue.length})` : 'Changements d’inventaire détectés'")),
        ("emailHtml", "string", E(f"`<p>${{$json.queue.length}} analyse(s) à réexaminer après des changements déclarés dans Notion.</p><ul>${{$json.queue.map(a => `<li><a href=\"${{a.notionUrl}}\">${{a.repositoriesKey}}</a> — ${{(a.reasons || ['déjà en file']).join(' ; ')}}</li>`).join('')}}</ul>"
                                  f"${{$json.action === 'reduce' ? `<p><b>Le lot dépasse ${{{CFG}.reviewQueueLimit}} analyses : aucun réexamen lancé.</b> Réduire la file (statut « historique » ou « annulé » dans Notion) ; le contrôle de demain reprendra.</p>` : $json.action === 'relaunch' ? `<p>Relancée aujourd’hui : ${{$json.toRelaunch.repositoriesKey}}. Les suivantes partent une par jour, dans la limite du budget.</p>` : ''}}"
                                  f"${{$json.withoutAnalysis.length ? `<p>Changements sans analyse liée (pas de réexamen automatique) : ${{$json.withoutAnalysis.map(c => `${{c.name}} ${{c.nature}}`).join(', ')}}. Renvoyer le formulaire si un dépôt est concerné.</p>` : ''}}`")),
        keep=True), (13, m))

    # branch A: flag the touched analyses
    w.add("Split Out - Touched Analyses", *SPLIT_OUT, {"fieldToSplitOut": "touched", "options": {}}, (14, m - 1.6))
    w.add("Data Table - Mark to Review", *TABLE, table_update("analysis_history", [("requestId", E("$json.requestId"))], {"reviewState": "to review"}), (15, m - 1.6))
    notion_add(w, "Notion - Mark to Review", notion_update(E("$json.notionPageId"), [notion_property("Statut", "select", "à réexaminer")]), (16, m - 1.6), onError="continueRegularOutput", **RETRY)

    # branch B: store today's snapshot (only when the inventory could be read)
    w.add("IF - Inventory Readable", *IF, {"conditions": conditions(cond(E("$json.readable"))), "options": {}}, (14, m))
    w.add("Data Table - Clear Snapshot", *TABLE, table_clear("inventory_snapshot"), (15, m), executeOnce=True)
    w.add("Set - Collect Snapshot Items", *SET, fields(("items", "array", E("$('Set - Format Snapshot Items').all().map(i => i.json).filter(f => f.toolId)"))), (16, m), executeOnce=True)
    w.add("Split Out - Snapshot Items", *SPLIT_OUT, {"fieldToSplitOut": "items", "options": {}}, (17, m))
    w.add("Data Table - Save Snapshot Item", *TABLE, table_insert("inventory_snapshot", {k: E(f"$json.{k}") for k in ["toolId", "name", "state", "presence", "version", "environment"]}), (18, m),
          note="Yesterday's snapshot is replaced by today's inventory, ready for tomorrow's comparison.")

    # branch C: act
    w.add("Switch - Review Action", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(E("$json.action"), "equals", "string", "reduce")), "renameOutput": True, "outputKey": "reduce"},
        {"conditions": conditions(cond(E("$json.action"), "equals", "string", "relaunch")), "renameOutput": True, "outputKey": "relaunch"},
        {"conditions": conditions(cond(E("$json.action"), "equals", "string", "inform")), "renameOutput": True, "outputKey": "inform"},
        {"conditions": conditions(cond(E("$json.action"), "equals", "string", "unreadable")), "renameOutput": True, "outputKey": "unreadable"},
    ]}, "options": {}}, (14, m + 1.8))
    w.add("Gmail - Ask to Reduce Queue", *GMAIL, gmail_params(E("$json.emailSubject"), E("$json.emailHtml")), (15, m + 1.2), **cred("gmail"), **RETRY)
    w.add("Set - Prepare Review Run", *SET, fields(
        ("mode", "string", E("$json.toRelaunch.request.mode")),
        ("githubUrls", "string", E("$json.toRelaunch.request.urls.join('\\n')")),
        ("goal", "string", E("$json.toRelaunch.request.goal || ''")),
        ("chosenReferences", "string", E("Object.entries($json.toRelaunch.request.manualRefs || {}).map(([k, v]) => `${k}=${v}`).join('\\n')")),
        ("origin", "string", "re-examination"),
        ("replacesId", "string", E("$json.toRelaunch.requestId")),
        ("previousUrl", "string", E("$json.toRelaunch.notionUrl || ''")),
        ("emailSubject", "string", E("$json.emailSubject")), ("emailHtml", "string", E("$json.emailHtml"))), (15, m + 1.8),
          note="Feeds the same request pipeline as the form: nothing is duplicated. The previous analysis is replaced only if the new one is delivered.")
    w.add("Gmail - Inform about Changes", *GMAIL, gmail_params(E("$('Set - Write Message').first().json.emailSubject"), E("$('Set - Write Message').first().json.emailHtml")), (16, m + 2.6), **cred("gmail"), **RETRY)
    w.add("Stop and Error - Inventory Unreadable", *STOP_ERROR, {"errorMessage": "The Notion inventory could not be read: check the data source id and the sharing with the integration. Yesterday's snapshot was kept."}, (15, m + 3.4))

    w.link("Switch - Route by Trigger", "Notion - Get Current Inventory", 1)
    w.link("Switch - Route by Trigger", "Data Table - Get Last Snapshot", 1)
    w.chain("Notion - Get Current Inventory", "Set - Format Snapshot Items")
    w.link("Set - Format Snapshot Items", "Compare Datasets - Detect Changes", 0, 0)
    w.link("Data Table - Get Last Snapshot", "Compare Datasets - Detect Changes", 0, 1)
    for output in range(4):
        w.link("Compare Datasets - Detect Changes", "Merge - Compare Outputs", output, output)
    w.chain("Merge - Compare Outputs", "Data Table - Get Analyses to Watch", "Aggregate - Analyses", "Notion - Get Profile for Monitoring", "Set - List Changes",
            "Set - Find Analyses to Review", "Set - Plan Review Queue", "Set - Write Message")
    w.link("Set - Write Message", "Split Out - Touched Analyses")
    w.chain("Split Out - Touched Analyses", "Data Table - Mark to Review", "Notion - Mark to Review")
    w.link("Set - Write Message", "IF - Inventory Readable")
    w.link("IF - Inventory Readable", "Data Table - Clear Snapshot", 0)
    w.chain("Data Table - Clear Snapshot", "Set - Collect Snapshot Items", "Split Out - Snapshot Items", "Data Table - Save Snapshot Item")
    w.link("Set - Write Message", "Switch - Review Action")
    w.link("Switch - Review Action", "Gmail - Ask to Reduce Queue", 0)
    w.link("Switch - Review Action", "Set - Prepare Review Run", 1)
    w.link("Set - Prepare Review Run", "Set - Parse Request")
    w.link("Switch - Review Action", "Gmail - Inform about Changes", 2)
    w.link("Switch - Review Action", "Stop and Error - Inventory Unreadable", 3)
    w.group("## 11. Daily inventory monitoring\nEvery morning the Notion inventory is compared with yesterday's snapshot (Compare Datasets). An analysis that used a changed tool, or a profile with a new revision, goes to the review queue. One re-examination is relaunched per day through the normal request pipeline, a queue that is too long asks for a reduction.",
            ["Notion - Get Current Inventory", "Set - Format Snapshot Items", "Data Table - Get Last Snapshot", "Compare Datasets - Detect Changes", "Merge - Compare Outputs", "Data Table - Get Analyses to Watch",
             "Aggregate - Analyses", "Notion - Get Profile for Monitoring", "Set - List Changes", "Set - Find Analyses to Review", "Set - Plan Review Queue", "Set - Write Message", "Split Out - Touched Analyses",
             "Data Table - Mark to Review", "Notion - Mark to Review", "IF - Inventory Readable", "Data Table - Clear Snapshot", "Set - Collect Snapshot Items", "Split Out - Snapshot Items",
             "Data Table - Save Snapshot Item", "Switch - Review Action", "Gmail - Ask to Reduce Queue", "Set - Prepare Review Run", "Gmail - Inform about Changes", "Stop and Error - Inventory Unreadable"])
