"""Guardrails before any AI call: reuse of an unchanged report, monthly budget, missing context."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
HASH = "$('Crypto - Hash Reuse Key').first().json"
MEASURE = "$('Set - Measure Budget').first().json"


def build(w):
    r = 16
    w.add("Set - Build Reuse Key", *SET, fields(
        ("repositoriesKey", "string", expr("{{ $json.repositories.map(r => r.key).sort().join(' + ') }}")),
        ("versions", "string", expr("{{ $json.repositories.map(r => `${r.key}@${r.tag} (${String(r.commit).slice(0, 7)})`).join(' + ') }}")),
        ("reuseKeyInput", "string", expr(f"{{{{ JSON.stringify([{CFG}.schemaVersion, $json.request.mode, String($json.request.goal || '').toLowerCase(), $json.repositories.map(r => `${{r.key}}@${{r.commit}}`).sort(), $json.machine, $json.profileRevision, $json.passages.map(p => p.text), $json.inventoryCatalog]) }}}}")),
        keep=True), (7, r), note="Same versions, same request and same personal context give the same key: the existing report is returned without any AI call.")
    w.add("Crypto - Hash Reuse Key", *CRYPTO, {"action": "hash", "type": "SHA256", "value": "={{ $json.reuseKeyInput }}", "dataPropertyName": "reuseKey", "encoding": "hex"}, (8, r))
    w.add("Data Table - Find Reusable Analysis", *TABLE, table_get("analysis_history", [("reuseKey", expr("{{ $json.reuseKey }}")), ("status", "done")], limit=1), (9, r), alwaysOutputData=True)
    w.add("Data Table - Find Previous Analysis", *TABLE, table_get("analysis_history", [("repositoriesKey", expr(f"{{{{ {HASH}.repositoriesKey }}}}")), ("mode", expr(f"{{{{ {HASH}.request.mode }}}}")), ("status", "done")], limit=1),
          (10, r), alwaysOutputData=True)
    w.add("Data Table - Get Monthly Rows", *TABLE, table_get("analysis_history", [("month", expr("{{ $now.toFormat('yyyy-LL') }}"))]), (11, r), alwaysOutputData=True, executeOnce=True)
    w.add("Summarize - Monthly Usage", *SUMMARIZE, {"fieldsToSummarize": {"values": [{"aggregation": "sum", "field": "costEur"}, {"aggregation": "sum", "field": "aiCalls"}]}, "options": {"outputFormat": "singleItem"}}, (12, r))
    w.add("Set - Measure Budget", *SET, fields(
        ("request", "object", expr(f"{{{{ {HASH}.request }}}}")),
        ("repositoriesKey", "string", expr(f"{{{{ {HASH}.repositoriesKey }}}}")),
        ("versions", "string", expr(f"{{{{ {HASH}.versions }}}}")),
        ("reuseKey", "string", expr(f"{{{{ {HASH}.reuseKey }}}}")),
        ("existing", "object", expr("{{ $('Data Table - Find Reusable Analysis').first().json }}")),
        ("previous", "object", expr("{{ $('Data Table - Find Previous Analysis').first().json }}")),
        ("previousId", "string", expr(f"{{{{ {HASH}.request.replacesId || $('Data Table - Find Previous Analysis').first().json.requestId || '' }}}}")),
        ("monthlySpendEur", "number", expr("{{ Number($json.sum_costEur) || 0 }}")),
        ("monthlyAiCalls", "number", expr("{{ Number($json.sum_aiCalls) || 0 }}")),
        ("estimatedMaxCostEur", "number", expr(f"{{{{ Math.round((((JSON.stringify({HASH}).length / 3.5) * {CFG}.rateInputEurPerMillion + {CFG}.maxOutputTokens * {CFG}.rateOutputEurPerMillion) / 1000000 + ({CFG}.webSearchEnabled ? {CFG}.webSearchCostEur : 0)) * 10000) / 10000 }}}}"))), (13, r),
        note="The maximum cost of the next call is estimated before it is paid.")
    w.add("Set - Decide Next Step", *SET, fields(
        ("budgetReasons", "array", expr(f"{{{{ [\n  $json.monthlyAiCalls >= {CFG}.maxAnalysesPerMonth ? `The monthly limit of ${{{CFG}.maxAnalysesPerMonth}} AI analyses is reached` : '',\n  $json.monthlySpendEur + $json.estimatedMaxCostEur > {CFG}.monthlyBudgetEur ? `Budget too low: ${{$json.monthlySpendEur.toFixed(2)}} EUR spent plus up to ${{$json.estimatedMaxCostEur.toFixed(2)}} EUR for this analysis, above ${{{CFG}.monthlyBudgetEur}} EUR` : ''\n].filter(Boolean) }}}}")),
        ("decision", "string", expr(f"{{{{ {HASH}.contextErrors.length ? 'suspend' : $json.existing.requestId ? 'reuse' : ($json.monthlyAiCalls >= {CFG}.maxAnalysesPerMonth || $json.monthlySpendEur + $json.estimatedMaxCostEur > {CFG}.monthlyBudgetEur) ? 'suspend' : 'analyze' }}}}")),
        ("reasons", "array", expr(f"{{{{ [...{HASH}.contextErrors, ...($json.existing.requestId ? [] : [\n  $json.monthlyAiCalls >= {CFG}.maxAnalysesPerMonth ? `The monthly limit of ${{{CFG}.maxAnalysesPerMonth}} AI analyses is reached` : '',\n  $json.monthlySpendEur + $json.estimatedMaxCostEur > {CFG}.monthlyBudgetEur ? `Budget too low: ${{$json.monthlySpendEur.toFixed(2)}} EUR spent plus up to ${{$json.estimatedMaxCostEur.toFixed(2)}} EUR for this analysis, above ${{{CFG}.monthlyBudgetEur}} EUR` : ''\n].filter(Boolean))] }}}}")),
        keep=True), (14, r))
    w.add("Switch - Decision", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(expr("{{ $json.decision }}"), "equals", "string", "analyze")), "renameOutput": True, "outputKey": "analyze"},
        {"conditions": conditions(cond(expr("{{ $json.decision }}"), "equals", "string", "reuse")), "renameOutput": True, "outputKey": "reuse"},
        {"conditions": conditions(cond(expr("{{ $json.decision }}"), "equals", "string", "suspend")), "renameOutput": True, "outputKey": "suspend"},
    ]}, "options": {}}, (15, r))
    w.chain("Set - Build Context", "Set - Build Reuse Key", "Crypto - Hash Reuse Key", "Data Table - Find Reusable Analysis", "Data Table - Find Previous Analysis",
            "Data Table - Get Monthly Rows", "Summarize - Monthly Usage", "Set - Measure Budget", "Set - Decide Next Step", "Switch - Decision")

    # reuse: the unchanged report is sent again, no AI call
    w.add("Gmail - Send Existing Report", *GMAIL, gmail_params(expr("{{ `Rapport existant - ${$json.repositoriesKey}` }}"), expr(
        "{{ `<p>Ces dépôts ont déjà été analysés le <b>${DateTime.fromISO($json.existing.createdAt).setLocale('fr').toFormat('dd/LL/yyyy')}</b> avec les mêmes versions (${$json.versions}) et le même contexte personnel. Aucune nouvelle analyse IA.</p><p><b>TL;DR :</b> ${String($json.existing.summary || '').replace(/&/g, '&amp;').replace(/</g, '&lt;')}</p><p>Rapport complet et JSON : <a href=\"${$json.existing.notionUrl}\">${$json.existing.notionUrl}</a></p>` }}")),
          (16, r), **cred("gmail"), **RETRY)
    w.add("Data Table - Restore Review Status", *TABLE, table_update("analysis_history", [("requestId", expr("{{ $('Set - Decide Next Step').first().json.request.replacesId || 'none' }}"))], {"reviewState": ""}), (17, r),
          alwaysOutputData=True, note="A re-examination that finds nothing new takes the analysis out of the review queue.")
    w.add("Data Table - Log Reused Request", *TABLE, table_insert("analysis_history", {
        "requestId": expr("{{ $('Set - Decide Next Step').first().json.request.id }}"), "status": "reused", "mode": expr("{{ $('Set - Decide Next Step').first().json.request.mode }}"),
        "repositoriesKey": expr("{{ $('Set - Decide Next Step').first().json.repositoriesKey }}"), "reuseKey": expr("{{ $('Set - Decide Next Step').first().json.reuseKey }}"),
        "notionUrl": expr("{{ $('Set - Decide Next Step').first().json.existing.notionUrl }}"), "month": expr("{{ $now.toFormat('yyyy-LL') }}"), "costEur": 0, "aiCalls": 0}), (18, r))
    w.link("Switch - Decision", "Gmail - Send Existing Report", 1)
    w.chain("Gmail - Send Existing Report", "Data Table - Restore Review Status", "Data Table - Log Reused Request")

    # suspended: missing context or budget reached
    w.add("Gmail - Send Suspension Notice", *GMAIL, gmail_params(expr("{{ `Diagnostic suspendu - ${$json.repositoriesKey}` }}"), expr(
        f"{{{{ `<p>Le diagnostic <b>${{$json.request.id}}</b> n’a pas été lancé. Aucun appel IA payant.</p><ul>${{$json.reasons.map(x => `<li>${{x.replace(/&/g, '&amp;').replace(/</g, '&lt;')}}</li>`).join('')}}</ul><p><b>Reste à traiter :</b> ${{$json.request.mode}} - ${{$json.versions}}</p><p>Budget du mois : ${{$json.monthlySpendEur.toFixed(2)}} EUR sur ${{{CFG}.monthlyBudgetEur}} EUR ; ${{$json.monthlyAiCalls}}/${{{CFG}.maxAnalysesPerMonth}} analyses IA.</p>` }}}}")),
          (16, r + 1.5), **cred("gmail"), **RETRY)
    w.add("Data Table - Log Suspended Request", *TABLE, table_insert("analysis_history", {
        "requestId": expr("{{ $('Set - Decide Next Step').first().json.request.id }}"), "status": "suspended", "mode": expr("{{ $('Set - Decide Next Step').first().json.request.mode }}"),
        "repositoriesKey": expr("{{ $('Set - Decide Next Step').first().json.repositoriesKey }}"), "reuseKey": expr("{{ $('Set - Decide Next Step').first().json.reuseKey }}"),
        "requestJson": expr("{{ JSON.stringify({ mode: $('Set - Decide Next Step').first().json.request.mode, urls: $('Set - Decide Next Step').first().json.request.rawUrls, goal: $('Set - Decide Next Step').first().json.request.goal, manualRefs: $('Set - Decide Next Step').first().json.request.manualRefs }).slice(0, 4000) }}"),
        "note": expr("{{ $('Set - Decide Next Step').first().json.reasons.join(' ; ').slice(0, 900) }}"), "month": expr("{{ $now.toFormat('yyyy-LL') }}"), "costEur": 0, "aiCalls": 0}), (17, r + 1.5))
    w.link("Switch - Decision", "Gmail - Send Suspension Notice", 2)
    w.chain("Gmail - Send Suspension Notice", "Data Table - Log Suspended Request")

    w.group("## 7. Guardrails before any AI call\nA SHA-256 key of versions, request and personal context finds an identical report. The monthly spend and call count come from the analysis history Data Table, and the maximum cost of the next call is checked first. Missing context or a reached budget suspends with an explanation.",
            ["Set - Build Reuse Key", "Crypto - Hash Reuse Key", "Data Table - Find Reusable Analysis", "Data Table - Find Previous Analysis", "Data Table - Get Monthly Rows", "Summarize - Monthly Usage",
             "Set - Measure Budget", "Set - Decide Next Step", "Switch - Decision", "Gmail - Send Existing Report", "Data Table - Restore Review Status", "Data Table - Log Reused Request",
             "Gmail - Send Suspension Notice", "Data Table - Log Suspended Request"])
