"""Reuse of an existing report (compared by repository link and version), then the personal context read from Notion."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
REQ = "$('Set - Parse and Validate Request').first().json"
EVIDENCE = "$('Set - Assemble Repository Evidence').first().json"
MD = "$('Notion - Get Profile').first().json.markdown"
NORM = "(s => String(s || '').toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, ''))"
# The key that identifies an analysis: the repository with its version, and the goal.
REUSE_KEY = "`${$json.key}@${$json.tag} | ${" + REQ + ".goal.toLowerCase()}`"


def E(js):
    return expr("{{ " + js + " }}")


def rich(prop):
    return f"($json.properties?.['{prop}']?.rich_text || []).map(t => t.plain_text).join('')"


def build(w):
    # ---------- reuse ----------
    r = 12
    w.add("Data Table - Find Existing Analysis", *TABLE, table_get("analysis_history", [("reuseKey", E(REUSE_KEY)), ("status", "done"), ("deliveryStatus", "complete")], limit=1), (1, r), alwaysOutputData=True,
          note="Same repository, same version and same goal: the existing report is found by this key, without any AI call. Only a report delivered in full (Notion page created, nothing unreadable) is reused.")
    w.add("IF - Already Analyzed", *IF, {"conditions": conditions(cond(E(f"!!$json.requestId && !{REQ}.force"))), "options": {}}, (2, r))
    w.add("Gmail - Send Existing Report", *GMAIL, gmail_params(E("`Rapport existant - ${$json.repositoriesKey}`"), E(
        "`<p>Ce dépôt a déjà été analysé le <b>${DateTime.fromISO($json.updatedAt || $json.createdAt).setLocale('fr').toFormat('dd/LL/yyyy')}</b> avec la même version (${$json.versions}) et le même objectif. Aucune nouvelle analyse n’a été lancée.</p>"
        "<p><b>TL;DR :</b> ${String($json.summary || '').replace(/&/g, '&amp;').replace(/</g, '&lt;')}</p>"
        "<p>Rapport complet : <a href=\"${$json.notionUrl}\">${$json.notionUrl}</a></p><p>Pour refaire l’analyse, renvoyer le formulaire avec « Refaire l’analyse » sur Oui.</p>`")),
          (3, r + 1.2), **cred("gmail"), **RETRY)
    w.link("Set - Assemble Repository Evidence", "Data Table - Find Existing Analysis")
    w.link("Data Table - Find Existing Analysis", "IF - Already Analyzed")
    w.link("IF - Already Analyzed", "Gmail - Send Existing Report", 0)
    w.group("## 3. Reuse of an existing report\nThe analyses are compared by repository link and version, plus the goal. An identical request returns the existing report in seconds. The form option to redo the analysis skips this shortcut.",
            ["Data Table - Find Existing Analysis", "IF - Already Analyzed", "Gmail - Send Existing Report"])

    # ---------- personal context ----------
    c = 16
    notion_add(w, "Notion - Get Profile", {"resource": "block", "operation": "getMarkdown", "blockId": locator(E(f"{CFG}.notionProfilePageId")), "includeTranscript": False}, (0, c), **RETRY)
    notion_add(w, "Notion - Get Inventory", {"resource": "databasePage", "operation": "getAll", "dataSourceId": locator(E(f"{CFG}.notionInventoryDataSourceId")),
                                             "returnAll": True, "filterType": "none", "simple": False, "options": {}}, (1, c), alwaysOutputData=True, executeOnce=True, **RETRY)
    w.add("Set - Format Inventory Items", *SET, fields(
        ("id", "string", E("$json.id || ''")),
        ("name", "string", E("($json.properties?.Nom?.title || []).map(t => t.plain_text).join('')")),
        ("state", "string", E("$json.properties?.Etat?.select?.name || ''")),
        ("presence", "string", E("$json.properties?.Presence?.select?.name || ''")),
        ("usage", "string", E(rich("Usage"))), ("feedback", "string", E(rich("Retour"))),
        ("abandonReason", "string", E(rich("Raison Abandon"))), ("environment", "string", E(rich("Environnement"))),
        ("version", "string", E(rich("Version"))), ("infoDate", "string", E("$json.properties?.['Date Info']?.date?.start || ''")),
        ("uncertainties", "string", E(rich("Incertitudes")))), (2, c))
    w.add("Aggregate - Inventory", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "inventory", "options": {}}, (3, c))
    block = f"(() => {{ try {{ return JSON.parse({MD}.match(/```json\\s*([\\s\\S]*?)```/)[1]); }} catch (e) {{ return {{}}; }} }})()"
    inventory = "$('Aggregate - Inventory').first().json.inventory.filter(o => o.id && o.name)"
    # The user's verdicts on earlier analyses (Notion property Decision), latest per repository, single-repository pages only.
    text = "(p, name) => (p.properties?.[name]?.rich_text || []).map(t => t.plain_text).join('')"
    decisions = (f"($json.decisionPages || []).filter(p => p.properties?.Decision?.select?.name && !({text})(p, 'Depots').includes(' + '))"
                 f".sort((a, b) => String(b.last_edited_time).localeCompare(String(a.last_edited_time)))"
                 f".filter((p, i, all) => all.findIndex(q => ({text})(q, 'Depots') === ({text})(p, 'Depots')) === i)"
                 f".map((p, i) => ({{ id: `decision-${{i + 1}}`, repository: ({text})(p, 'Depots'), analysedVersion: ({text})(p, 'Version').split('@')[1] || '', decision: p.properties.Decision.select.name, decidedAt: String(p.last_edited_time).slice(0, 10), url: p.url }}))")
    notion_add(w, "Notion - Get Decisions", {"resource": "databasePage", "operation": "getAll", "dataSourceId": locator(E(f"{CFG}.notionAnalysesDataSourceId")),
                                             "returnAll": True, "filterType": "none", "simple": False, "options": {}}, (4, c), alwaysOutputData=True, executeOnce=True, **RETRY,
               note="Reads the Analyses database to find the pages where the user chose Installed, Ignored or Uninstalled in the Decision property.")
    w.add("Limit - Analyses Pages", *LIMIT, {"maxItems": E(f"{CFG}.env === 'production' ? 999999 : {CFG}.limitItems"), "keep": "firstItems"}, (5, c),
          note="Test mode: when CONFIGURATION.env is not production, only the first few pages of the Analyses database are kept (item limit in CONFIGURATION). In production nothing is cut.")
    w.add("Aggregate - Decisions", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "decisionPages", "options": {}}, (6, c))
    w.add("Set - Gather Prompt Inputs", *SET, fields(
        ("request", "object", E(f"({{ id: {REQ}.requestId, goal: {REQ}.goal || 'none, judge from the profile', date: $now.toISODate(), receivedAt: {REQ}.receivedAt }})")),
        ("machine", "object", E(f"({block}).machine || {{}}")),
        ("profileRevision", "string", E(f"({block}).revision || ''")),
        ("profile", "array", E(f"String({MD} || '').replace(/```[\\s\\S]*?```/g, '').split(/\\n(?=#{{1,3}}\\s)/).map(s => s.trim()).filter(s => s.length > 20).map((s, i) => ({{ id: `profile-${{i + 1}}`, label: {CLEAN}(s.split('\\n')[0].replace(/^#+\\s*/, '').slice(0, 80)), text: {CLEAN}(s.slice(0, 3000)) }}))")),
        ("inventory", "array", E(inventory)),
        ("decisions", "array", E(decisions)),
        ("matches", "array", E(f"(n => (r => {inventory}.filter(o => n(o.name) && (n(o.name) === n(r.key.split('/')[1]) || n(o.name) === n(r.key))).map(o => ({{ repository: r.key, tool: o.name, state: o.state, presence: o.presence, version: o.version, environment: o.environment }})))({EVIDENCE}))({NORM})")),
        ("repository", "object", E(f"Object.fromEntries(Object.entries({EVIDENCE}).filter(e => e[0] !== 'limits'))")),
        ("limits", "array", E(f"[...({EVIDENCE}.limits || []),\n  (l => l.length ? `Inventory: tools without state or presence are treated as unknown: ${{l.join(', ')}}` : '')({inventory}.filter(o => !o.state || !o.presence).map(o => o.name)),\n"
                              f"  !Object.keys(({block}).machine || {{}}).length ? 'The machine block is missing in the Notion profile' : ''].filter(Boolean)"))),
        (7, c), note="Everything the AI may use, in one item: the request, the machine, the profile, the inventory, the user decisions and the GitHub evidence. The XML node turns it into the inputs of the prompt.")
    w.link("IF - Already Analyzed", "Notion - Get Profile", 1)
    w.chain("Notion - Get Profile", "Notion - Get Inventory", "Set - Format Inventory Items", "Aggregate - Inventory", "Notion - Get Decisions", "Limit - Analyses Pages", "Aggregate - Decisions", "Set - Gather Prompt Inputs")
    w.group("## 4. Personal context from Notion\nThe profile (machine, activities, goals) and the inventory of tools are read once and given to the AI in full: the inventory is short enough to need no vector search. Tools that match a repository name are listed apart.",
            ["Notion - Get Profile", "Notion - Get Inventory", "Set - Format Inventory Items", "Aggregate - Inventory", "Notion - Get Decisions", "Limit - Analyses Pages", "Aggregate - Decisions", "Set - Gather Prompt Inputs"])
