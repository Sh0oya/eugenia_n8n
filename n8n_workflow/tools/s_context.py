"""Reuse of an existing report (compared by repository link and version), then the personal context read from Notion."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
REQ = "$('Set - Parse and Validate Request').first().json"
EVIDENCE = "$('Aggregate - Repository Evidence').first().json.repositories"
MD = "$('Notion - Get Profile').first().json.markdown"
NORM = "(s => String(s || '').toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, ''))"
# The key that identifies an analysis: the repositories with their version, and the goal.
REUSE_KEY = "`${$json.repositories.map(r => `${r.key}@${r.tag}`).sort().join(' + ')} | ${" + REQ + ".goal.toLowerCase()}`"


def E(js):
    return expr("{{ " + js + " }}")


def rich(prop):
    return f"($json.properties?.['{prop}']?.rich_text || []).map(t => t.plain_text).join('')"


def build(w):
    # ---------- reuse ----------
    r = 12
    w.add("Data Table - Find Existing Analysis", *TABLE, table_get("analysis_history", [("reuseKey", E(REUSE_KEY)), ("status", "done")], limit=1), (1, r), alwaysOutputData=True,
          note="Same repositories, same versions and same goal: the existing report is found by this key, without any AI call.")
    w.add("IF - Already Analyzed", *IF, {"conditions": conditions(cond(E(f"!!$json.requestId && !{REQ}.force"))), "options": {}}, (2, r))
    w.add("Gmail - Send Existing Report", *GMAIL, gmail_params(E("`Rapport existant - ${$json.repositoriesKey}`"), E(
        "`<p>Ces dépôts ont déjà été analysés le <b>${DateTime.fromISO($json.createdAt).setLocale('fr').toFormat('dd/LL/yyyy')}</b> avec les mêmes versions (${$json.versions}) et le même objectif. Aucune nouvelle analyse n’a été lancée.</p>"
        "<p><b>TL;DR :</b> ${String($json.summary || '').replace(/&/g, '&amp;').replace(/</g, '&lt;')}</p>"
        "<p>Rapport complet : <a href=\"${$json.notionUrl}\">${$json.notionUrl}</a></p><p>Pour refaire l’analyse, renvoyer le formulaire avec « Refaire l’analyse » sur Oui.</p>`")),
          (3, r + 1.2), **cred("gmail"), **RETRY)
    w.link("Aggregate - Repository Evidence", "Data Table - Find Existing Analysis")
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
    inventory = "$json.inventory.filter(o => o.id && o.name)"
    w.add("Set - Gather Prompt Inputs", *SET, fields(
        ("request", "object", E(f"({{ id: {REQ}.requestId, mode: {EVIDENCE}.length > 1 ? 'compare' : 'single', goal: {REQ}.goal || 'none, judge from the profile', date: $now.toISODate(), receivedAt: {REQ}.receivedAt }})")),
        ("machine", "object", E(f"({block}).machine || {{}}")),
        ("profileRevision", "string", E(f"({block}).revision || ''")),
        ("profile", "array", E(f"String({MD} || '').replace(/```[\\s\\S]*?```/g, '').split(/\\n(?=#{{1,3}}\\s)/).map(s => s.trim()).filter(s => s.length > 20).map((s, i) => ({{ id: `profile-${{i + 1}}`, label: s.split('\\n')[0].replace(/^#+\\s*/, '').slice(0, 80), text: s.slice(0, 3000) }}))")),
        ("inventory", "array", E(inventory)),
        ("matches", "array", E(f"(n => {EVIDENCE}.flatMap(r => {inventory}.filter(o => n(o.name).length >= 3 && (n(o.name).includes(n(r.key.split('/')[1])) || n(r.key.split('/')[1]).includes(n(o.name)))).map(o => ({{ repository: r.key, tool: o.name, state: o.state, presence: o.presence, version: o.version, environment: o.environment }}))))({NORM})")),
        ("repositories", "array", E(EVIDENCE)),
        ("limits", "array", E(f"[...{EVIDENCE}.flatMap(r => r.limits || []),\n  (l => l.length ? `Inventory: tools without state or presence are treated as unknown: ${{l.join(', ')}}` : '')({inventory}.filter(o => !o.state || !o.presence).map(o => o.name)),\n"
                              f"  !Object.keys(({block}).machine || {{}}).length ? 'The machine block is missing in the Notion profile' : ''].filter(Boolean)"))),
        (4, c), note="Everything the AI may use, in one item: the request, the machine, the profile, the inventory and the GitHub evidence. The XML node turns it into the inputs of the prompt.")
    w.link("IF - Already Analyzed", "Notion - Get Profile", 1)
    w.chain("Notion - Get Profile", "Notion - Get Inventory", "Set - Format Inventory Items", "Aggregate - Inventory", "Set - Gather Prompt Inputs")
    w.group("## 4. Personal context from Notion\nThe profile (machine, activities, goals) and the inventory of tools are read once and given to the AI in full: the inventory is short enough to need no vector search. Tools that match a repository name are listed apart.",
            ["Notion - Get Profile", "Notion - Get Inventory", "Set - Format Inventory Items", "Aggregate - Inventory", "Set - Gather Prompt Inputs"])
