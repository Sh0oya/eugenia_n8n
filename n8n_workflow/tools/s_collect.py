"""GitHub evidence collection (one loop iteration per repository) and the three outcomes: ready, waiting, failed."""
from lib import *
from s_entry import REF_PATTERN as REF

LOOP = "Loop Over Items - Repositories"
LOOP_ITEM = f"$('{LOOP}').first(1).json"
SELECT = "Set - Select Reference"
SEL = f"$('{SELECT}').first().json"
CFG = "$('CONFIGURATION').first().json"
STABLE = "($json.releases || []).find(r => r.tag_name && !r.draft && !r.prerelease)"
MANUAL_REF = f"{LOOP_ITEM}.request.manualRefs[{LOOP_ITEM}.repository.key]"

RANK = (r"(/^readme(\.|$)/i.test(p) ? 0 : /^(docs?|documentation)\/(.*\/)?[^/]*(install|quickstart|getting[-_]?started|requirement|prerequisite)[^/]*\.(md|mdx|rst|txt)$/i.test(p) || /^install[^/]*\.(md|mdx|rst|txt)$/i.test(p) ? 1"
        r" : /^(pyproject\.toml|setup\.py|setup\.cfg|requirements[^/]*\.txt|environment[^/]*\.ya?ml|package\.json|cargo\.toml|cmakelists\.txt|dockerfile)$/i.test(p) ? 2"
        r" : /^(install|setup|build)[^/]*\.(sh|bat|ps1)$/i.test(p) ? 3 : 9)")
SECTION = r"/^#{1,4}\s.*(install|requirement|prerequisite|setup|hardware|compatib|platform|windows|wsl|gpu|cuda|driver|system|quick ?start|getting started)/i"


def gh(resource, operation, owner, repo, **extra):
    return {"authentication": "accessToken", "resource": resource, "operation": operation,
            "owner": {"__rl": True, "mode": "name", "value": owner}, "repository": {"__rl": True, "mode": "name", "value": repo}, **extra}


def http_github(url):
    return {"method": "GET", "url": url, "authentication": "predefinedCredentialType", "nodeCredentialType": "githubApi",
            "sendHeaders": True, "headerParameters": {"parameters": [{"name": "Accept", "value": "application/vnd.github+json"}, {"name": "X-GitHub-Api-Version", "value": "2022-11-28"}]},
            "options": {"response": {"response": {"fullResponse": True, "neverError": True, "responseFormat": "json"}}}}


def evidence(status, problem, source, **overrides):
    """Evidence item shape shared by every outcome of the loop."""
    base = [
        ("key", "string", expr(f"{{{{ {source}.repository.key }}}}")),
        ("owner", "string", expr(f"{{{{ {source}.repository.owner }}}}")),
        ("name", "string", expr(f"{{{{ {source}.repository.name }}}}")),
        ("url", "string", expr(f"{{{{ {source}.repository.url }}}}")),
        ("status", "string", status), ("problem", "string", problem),
        ("tag", "string", expr("{{ $json.tag || '' }}")), ("commit", "string", ""),
        ("manualReference", "boolean", expr("{{ !!$json.manualReference }}")),
        ("releaseUrl", "string", expr("{{ $json.releaseUrl || '' }}")), ("publishedAt", "string", expr("{{ $json.publishedAt || '' }}")),
        ("description", "string", expr("{{ $json.info?.description || '' }}")), ("topics", "array", expr("{{ $json.info?.topics || [] }}")),
        ("license", "string", expr("{{ $json.info?.license || '' }}")), ("homepage", "string", expr("{{ $json.info?.homepage || '' }}")),
        ("archived", "boolean", expr("{{ !!$json.info?.archived }}")),
        ("documents", "array", expr("{{ [] }}")), ("issues", "array", expr("{{ [] }}")), ("limits", "array", expr("{{ [] }}")),
        ("request", "object", expr(f"{{{{ {source}.request }}}}")),
    ]
    merged = [(n, t, overrides.get(n, v)) for n, t, v in base]
    return fields(*merged)


def build(w):
    w.add("Split Out - Repositories", *SPLIT_OUT, {"fieldToSplitOut": "repositories", "include": "allOtherFields", "options": {"destinationFieldName": "repository"}}, (7, 3))
    w.add("Limit - Repositories in Dev", *LIMIT, {"maxItems": expr(f"{{{{ {CFG}.env === 'production' ? 100 : {CFG}.devRepositoryLimit }}}}")}, (8, 3),
          note="In dev, only the first repositories are processed so that tests stay cheap.")
    w.add(LOOP, *LOOP_NODE, {"batchSize": 1, "options": {}}, (9, 3))
    w.link("IF - Request Valid", "Split Out - Repositories", 0)
    w.chain("Split Out - Repositories", "Limit - Repositories in Dev", LOOP)

    # --- loop body: one repository at a time ---
    w.add("GitHub - Get Repository", *GITHUB, gh("repository", "get", "={{ $json.repository.owner }}", "={{ $json.repository.name }}"), (10, 3),
          onError="continueErrorOutput", **cred("github"), **RETRY)
    w.add("Set - Mark Repository Unreachable", *SET, fields(
        ("key", "string", expr(f"{{{{ {LOOP_ITEM}.repository.key }}}}")), ("owner", "string", expr(f"{{{{ {LOOP_ITEM}.repository.owner }}}}")),
        ("name", "string", expr(f"{{{{ {LOOP_ITEM}.repository.name }}}}")), ("url", "string", expr(f"{{{{ {LOOP_ITEM}.repository.url }}}}")),
        ("status", "string", "failed"), ("problem", "string", "Repository not found, private, or GitHub unavailable"),
        ("tag", "string", ""), ("commit", "string", ""), ("manualReference", "boolean", expr("{{ false }}")), ("releaseUrl", "string", ""),
        ("publishedAt", "string", ""), ("description", "string", ""), ("topics", "array", expr("{{ [] }}")), ("license", "string", ""),
        ("homepage", "string", ""), ("archived", "boolean", expr("{{ false }}")), ("documents", "array", expr("{{ [] }}")),
        ("issues", "array", expr("{{ [] }}")), ("limits", "array", expr("{{ [] }}")), ("request", "object", expr(f"{{{{ {LOOP_ITEM}.request }}}}"))), (10, 4))
    w.add("GitHub - List Releases", *GITHUB, gh("release", "getAll", "={{ $json.owner.login }}", "={{ $json.name }}", returnAll=False, limit=30), (11, 3),
          alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Aggregate - Releases", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "releases", "options": {}}, (12, 3))
    w.add(SELECT, *SET, fields(
        ("repository", "object", expr(f"{{{{ {LOOP_ITEM}.repository }}}}")),
        ("request", "object", expr(f"{{{{ {LOOP_ITEM}.request }}}}")),
        ("info", "object", expr("{{ (r => ({ description: r.description || '', topics: r.topics || [], license: r.license?.spdx_id || '', homepage: r.homepage || '', archived: !!r.archived }))($('GitHub - Get Repository').first().json) }}")),
        ("tag", "string", expr(f"{{{{ {STABLE}?.tag_name || {MANUAL_REF} || '' }}}}")),
        ("manualReference", "boolean", expr(f"{{{{ !{STABLE}?.tag_name }}}}")),
        ("releaseUrl", "string", expr(f"{{{{ {STABLE}?.html_url || '' }}}}")),
        ("publishedAt", "string", expr(f"{{{{ {STABLE}?.published_at || '' }}}}")),
        ("apiError", "string", expr("{{ String(($json.releases || []).find(r => r.error)?.error || '') }}")),
        ("status", "string", expr(f"{{{{ ($json.releases || []).some(r => r.error) ? 'failed' : ({STABLE}?.tag_name || {MANUAL_REF}) ? 'ready' : 'waiting' }}}}")),
        ("problem", "string", expr(f"{{{{ ($json.releases || []).some(r => r.error) ? `GitHub unavailable while reading releases (${{String(($json.releases || []).find(r => r.error)?.error || '').slice(0, 120)}})` : ({STABLE}?.tag_name || {MANUAL_REF}) ? '' : 'No stable release published' }}}}"))),
        (13, 3), note="Latest stable release = newest release that is neither a draft nor a pre-release. Without one, the reference chosen by the user is used, otherwise the request waits.")
    w.add("IF - Reference Found", *IF, {"conditions": conditions(cond(expr("{{ $json.status === 'ready' }}"))), "options": {}}, (14, 3))
    w.add("Set - Complete Pending Evidence", *SET, evidence("={{ $json.status }}", "={{ $json.problem }}", "$json"), (14, 4))

    w.add("HTTP Request - Resolve Commit", *HTTP, http_github(expr("{{ `https://api.github.com/repos/${$json.repository.owner}/${$json.repository.name}/commits/${encodeURIComponent($json.tag)}` }}")), (15, 3),
          note="The GitHub node has no commit operation, so the tag is resolved to its commit with the GitHub credential.", **cred("github"), **RETRY)
    w.add("HTTP Request - List Files", *HTTP, http_github(expr(f"{{{{ `https://api.github.com/repos/${{{SEL}.repository.owner}}/${{{SEL}.repository.name}}/git/trees/${{$json.body?.commit?.tree?.sha || 'unknown'}}?recursive=1` }}}}")), (16, 3),
          note="The GitHub node cannot list a whole tree: one recursive call finds the installation documents.", **cred("github"), **RETRY)
    w.add("Set - Choose Documents", *SET, fields(
        ("commitSha", "string", expr("{{ $('HTTP Request - Resolve Commit').first().json.body?.sha || '' }}")),
        ("treeTruncated", "boolean", expr("{{ !!$json.body?.truncated }}")),
        ("documentPaths", "array", expr(f"{{{{ (l => l.length ? l : ['README.md'])((($json.body?.tree) || []).filter(f => f.type === 'blob').map(f => f.path).map(p => ({{ path: p, rank: {RANK} }})).filter(f => f.rank < 9).sort((a, b) => a.rank - b.rank || a.path.length - b.path.length).slice(0, {CFG}.maxDocuments).map(f => f.path)) }}}}"))),
        (17, 3), note="Picks at most the configured number of files: README first, then installation guides, then dependency and build files.")
    w.add("Split Out - Document Paths", *SPLIT_OUT, {"fieldToSplitOut": "documentPaths", "options": {"destinationFieldName": "path"}}, (18, 3))
    w.add("GitHub - Get Document", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath="={{ $json.path }}",
                                              asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.tag }}}}"}),
          (19, 3), onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Extract from File - Read Document", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (20, 3),
          onError="continueRegularOutput")
    w.add("Set - Trim Document", *SET, fields(
        ("path", "string", expr("{{ $json.path }}")),
        ("status", "string", expr("{{ typeof $json.content === 'string' && $json.content.length ? 'ok' : 'missing' }}")),
        ("url", "string", expr(f"{{{{ `https://github.com/${{{SEL}.repository.owner}}/${{{SEL}.repository.name}}/blob/${{$('Set - Choose Documents').first().json.commitSha}}/${{$json.path}}` }}}}")),
        ("originalSize", "number", expr("{{ String($json.content || '').length }}")),
        ("truncated", "boolean", expr(f"{{{{ String($json.content || '').length > {CFG}.maxDocumentChars }}}}")),
        ("text", "string", expr(f"{{{{ (t => t.length <= {CFG}.maxDocumentChars || !/\\.(md|mdx|rst)$/i.test($json.path) ? t.slice(0, {CFG}.maxDocumentChars) : t.split(/\\n(?=#{{1,2}}\\s)/).reduce((acc, s, i) => i === 0 ? s.slice(0, {CFG}.maxDocumentChars * 0.35) : {SECTION}.test(s.split('\\n')[0]) ? `${{acc}}\\n[...]\\n${{s}}` : acc, '').slice(0, {CFG}.maxDocumentChars))(String($json.content || '')) }}}}"))),
        (21, 3), note="Long Markdown files keep their introduction and the installation sections instead of the first characters only.")
    w.add("Aggregate - Documents", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "documents", "options": {}}, (22, 3))
    w.add("GitHub - List Issues", *GITHUB, gh("repository", "getIssues", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", returnAll=False, limit=40,
                                              getRepositoryIssuesFilters={"state": "all", "sort": "updated", "direction": "desc"}),
          (23, 3), alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Filter - Relevant Issues", *FILTER, {"conditions": conditions(cond(expr("{{ !$json.pull_request && /windows|wsl|install|gpu|intel|requirements|cuda|driver/i.test($json.title || '') }}"))), "options": {}}, (24, 3), alwaysOutputData=True)
    w.add("Limit - Issues", *LIMIT, {"maxItems": expr(f"{{{{ {CFG}.maxIssues }}}}")}, (25, 3))
    w.add("Aggregate - Issues", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "issues", "options": {}}, (26, 3))
    w.add("Set - Assemble Repository Evidence", *SET, fields(
        ("key", "string", expr(f"{{{{ {SEL}.repository.key }}}}")), ("owner", "string", expr(f"{{{{ {SEL}.repository.owner }}}}")),
        ("name", "string", expr(f"{{{{ {SEL}.repository.name }}}}")), ("url", "string", expr(f"{{{{ {SEL}.repository.url }}}}")),
        ("status", "string", expr("{{ $('Set - Choose Documents').first().json.commitSha ? 'ready' : 'failed' }}")),
        ("problem", "string", expr("{{ $('Set - Choose Documents').first().json.commitSha ? '' : 'The tag or its commit could not be found' }}")),
        ("tag", "string", expr(f"{{{{ {SEL}.tag }}}}")), ("commit", "string", expr("{{ $('Set - Choose Documents').first().json.commitSha }}")),
        ("manualReference", "boolean", expr(f"{{{{ {SEL}.manualReference }}}}")), ("releaseUrl", "string", expr(f"{{{{ {SEL}.releaseUrl }}}}")),
        ("publishedAt", "string", expr(f"{{{{ {SEL}.publishedAt }}}}")), ("description", "string", expr(f"{{{{ {SEL}.info.description }}}}")),
        ("topics", "array", expr(f"{{{{ {SEL}.info.topics }}}}")), ("license", "string", expr(f"{{{{ {SEL}.info.license }}}}")),
        ("homepage", "string", expr(f"{{{{ {SEL}.info.homepage }}}}")), ("archived", "boolean", expr(f"{{{{ {SEL}.info.archived }}}}")),
        ("documents", "array", expr("{{ $('Aggregate - Documents').first().json.documents.filter(d => d.status === 'ok') }}")),
        ("issues", "array", expr("{{ ($json.issues || []).filter(i => i.title).map(i => ({ title: i.title, url: i.html_url, state: i.state, updatedAt: i.updated_at, labels: (i.labels || []).map(l => l.name), excerpt: String(i.body || '').slice(0, 800) })) }}")),
        ("limits", "array", expr(f"{{{{ [\n  $('Set - Choose Documents').first().json.treeTruncated ? `${{{SEL}.repository.key}}: file tree truncated by GitHub, some documents may be missing` : '',\n  $('Aggregate - Documents').first().json.documents.some(d => d.truncated) ? `${{{SEL}.repository.key}}: long documents reduced to the introduction and the installation sections` : '',\n  ($json.issues || []).some(i => i.error) ? `${{{SEL}.repository.key}}: issues could not be read` : ''\n].filter(Boolean) }}}}")),
        ("request", "object", expr(f"{{{{ {SEL}.request }}}}"))), (27, 3))

    w.link(LOOP, "Aggregate - Repository Evidence", 0)
    w.link(LOOP, "GitHub - Get Repository", 1)
    w.link("GitHub - Get Repository", "GitHub - List Releases", 0)
    w.link("GitHub - Get Repository", "Set - Mark Repository Unreachable", 1)
    w.link("Set - Mark Repository Unreachable", LOOP)
    w.chain("GitHub - List Releases", "Aggregate - Releases", SELECT, "IF - Reference Found")
    w.link("IF - Reference Found", "HTTP Request - Resolve Commit", 0)
    w.link("IF - Reference Found", "Set - Complete Pending Evidence", 1)
    w.link("Set - Complete Pending Evidence", LOOP)
    w.chain("HTTP Request - Resolve Commit", "HTTP Request - List Files", "Set - Choose Documents", "Split Out - Document Paths", "GitHub - Get Document",
            "Extract from File - Read Document", "Set - Trim Document", "Aggregate - Documents", "GitHub - List Issues", "Filter - Relevant Issues",
            "Limit - Issues", "Aggregate - Issues", "Set - Assemble Repository Evidence")
    w.link("Set - Assemble Repository Evidence", LOOP)

    # --- outcome of the whole batch ---
    w.add("Aggregate - Repository Evidence", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "repositories", "options": {}}, (10, 6))
    w.add("Set - Evaluate References", *SET, fields(
        ("request", "object", expr("{{ $json.repositories[0].request }}")),
        ("repositories", "array", expr("{{ $json.repositories }}")),
        ("outcome", "string", expr("{{ $json.repositories.some(r => r.status === 'failed') ? 'failed' : $json.repositories.some(r => r.status === 'waiting') ? 'waiting' : 'ready' }}")),
        ("problems", "array", expr("{{ $json.repositories.filter(r => r.status !== 'ready').map(r => ({ key: r.key, problem: r.problem, tagsUrl: `${r.url}/tags` })) }}"))), (11, 6))
    w.add("Switch - Reference Outcome", *SWITCH, {"rules": {"values": [
        {"conditions": conditions(cond(expr("{{ $json.outcome }}"), "equals", "string", "ready")), "renameOutput": True, "outputKey": "ready"},
        {"conditions": conditions(cond(expr("{{ $json.outcome }}"), "equals", "string", "waiting")), "renameOutput": True, "outputKey": "waiting"},
        {"conditions": conditions(cond(expr("{{ $json.outcome }}"), "equals", "string", "failed")), "renameOutput": True, "outputKey": "failed"},
    ]}, "options": {}}, (12, 6))
    w.chain("Aggregate - Repository Evidence", "Set - Evaluate References", "Switch - Reference Outcome")

    w.group("## 3. GitHub evidence, one repository at a time\nLoop Over Items processes one repository per pass, so a failure stays confined to its repository. Latest stable release, commit, installation documents read at that commit, and recent issues. Nothing from the repositories is ever executed.",
            ["Split Out - Repositories", "Limit - Repositories in Dev", LOOP, "GitHub - Get Repository", "Set - Mark Repository Unreachable", "GitHub - List Releases", "Aggregate - Releases",
             SELECT, "IF - Reference Found", "Set - Complete Pending Evidence", "HTTP Request - Resolve Commit", "HTTP Request - List Files", "Set - Choose Documents", "Split Out - Document Paths",
             "GitHub - Get Document", "Extract from File - Read Document", "Set - Trim Document", "Aggregate - Documents", "GitHub - List Issues", "Filter - Relevant Issues", "Limit - Issues",
             "Aggregate - Issues", "Set - Assemble Repository Evidence"])
    w.group("## 4. Outcome of the batch\nReady: continue. Waiting: no stable release, the user is asked. Failed: the cause and the step are reported.",
            ["Aggregate - Repository Evidence", "Set - Evaluate References", "Switch - Reference Outcome"])

    # ---------- waiting: ask, wait, resume or cancel (no AI call while waiting) ----------
    w.add("Data Table - Log Waiting Request", *TABLE, table_insert("analysis_history", {
        "requestId": expr("{{ $json.request.id }}"), "status": "waiting", "mode": expr("{{ $json.request.mode }}"),
        "repositoriesKey": expr("{{ $json.repositories.map(r => r.key).sort().join(' + ') }}"),
        "requestJson": expr("{{ JSON.stringify({ mode: $json.request.mode, urls: $json.request.rawUrls, goal: $json.request.goal, manualRefs: $json.request.manualRefs }).slice(0, 4000) }}"),
        "note": expr("{{ $json.problems.map(p => `${p.key}: ${p.problem}`).join(' ; ').slice(0, 900) }}"),
        "month": expr("{{ $now.toFormat('yyyy-LL') }}"), "costEur": 0, "aiCalls": 0}), (13, 7))
    w.add("Gmail - Ask for Reference", *GMAIL, gmail_params("Diagnostic en attente - référence à choisir", expr(
        "{{ `<p>Le diagnostic <b>${$('Set - Evaluate References').first().json.request.id}</b> attend ta décision : pas de release stable publiée.</p><ul>${$('Set - Evaluate References').first().json.problems.map(p => `<li><b>${p.key}</b> - ${p.problem} - <a href=\"${p.tagsUrl}\">tags disponibles</a></li>`).join('')}</ul><p><a href=\"${$execution.resumeFormUrl}\">Choisir une référence ou annuler</a> (lien valable ${$('CONFIGURATION').first().json.waitDays} jours). Aucun appel IA pendant l’attente.</p>` }}")),
          (14, 7), **cred("gmail"), **RETRY)
    w.add("Wait - Reference Reply", *WAIT, {
        "resume": "form", "incomingAuthentication": "basicAuth", "formTitle": "Ça tourne sur mon PC ? - référence à choisir",
        "formDescription": expr("{{ $('Set - Evaluate References').first().json.problems.map(p => `${p.key} : ${p.problem}`).join(' - ') }}"),
        "formFields": {"values": [
            {"fieldLabel": "Décision", "fieldType": "dropdown", "requiredField": True, "fieldOptions": {"values": [{"option": "Poursuivre avec ces références"}, {"option": "Annuler la demande"}]}},
            {"fieldLabel": "Références", "fieldType": "textarea", "placeholder": "propriétaire/dépôt=tag, une ligne par dépôt"}]},
        "limitWaitTime": True, "limitType": "afterTimeInterval", "resumeAmount": expr(f"{{{{ {CFG}.waitDays }}}}"), "resumeUnit": "days",
        "options": {"appendAttribution": False, "respondWithOptions": {"values": {"respondWith": "text", "formSubmittedText": "Réponse enregistrée. Si tu poursuis, le rapport arrive par e-mail."}}},
    }, (15, 7), webhookId=sid("webhook", "wait"), **cred("basic"), note="The execution sleeps here for the configured number of days; no AI call is made while it waits.")
    w.add("Set - Apply Reply", *SET, fields(
        ("decision", "string", expr("{{ $json['Décision'] === 'Poursuivre avec ces références' && String($json['Références'] || '').trim() ? 'continue' : 'cancel' }}")),
        ("request", "object", expr("{{ ({ ...$('Set - Evaluate References').first().json.request, origin: 'resume', manualRefs: { ...$('Set - Evaluate References').first().json.request.manualRefs, ...Object.fromEntries(String($json['Références'] || '').split(/\\r?\\n/).map(l => l.trim().match(" + REF + ")).filter(Boolean).map(m => [m[1].toLowerCase(), m[2]])) } }) }}")),
        ("repositories", "array", expr("{{ $('Set - Evaluate References').first().json.repositories.map(r => ({ owner: r.owner, name: r.name, key: r.key, url: r.url })) }}"))), (16, 7))
    w.add("Data Table - Close Waiting Request", *TABLE, table_update("analysis_history", [("requestId", expr("{{ $json.request.id }}")), ("status", "waiting")],
                                                                   {"status": expr("{{ $json.decision === 'continue' ? 'resumed' : 'cancelled' }}")}), (17, 7))
    w.add("IF - Continue After Reply", *IF, {"conditions": conditions(cond(expr("{{ $('Set - Apply Reply').first().json.decision === 'continue' }}"))), "options": {}}, (18, 7))
    w.link("Switch - Reference Outcome", "Data Table - Log Waiting Request", 1)
    w.chain("Data Table - Log Waiting Request", "Gmail - Ask for Reference", "Wait - Reference Reply", "Set - Apply Reply", "Data Table - Close Waiting Request", "IF - Continue After Reply")
    w.link("IF - Continue After Reply", "Split Out - Repositories", 0)
    w.group("## 5. Waiting for a reference\nNo stable release: an e-mail with a form lets the user choose a tag or cancel. The Wait node keeps the request alive for the configured number of days and the flow loops back to the evidence step when the user continues.",
            ["Data Table - Log Waiting Request", "Gmail - Ask for Reference", "Wait - Reference Reply", "Set - Apply Reply", "Data Table - Close Waiting Request", "IF - Continue After Reply"])

    # ---------- failed ----------
    w.add("Data Table - Log Failed Request", *TABLE, table_insert("analysis_history", {
        "requestId": expr("{{ $json.request.id }}"), "status": "failed", "mode": expr("{{ $json.request.mode }}"),
        "repositoriesKey": expr("{{ $json.repositories.map(r => r.key).sort().join(' + ') }}"),
        "note": expr("{{ $json.problems.map(p => `${p.key}: ${p.problem}`).join(' ; ').slice(0, 900) }}"),
        "month": expr("{{ $now.toFormat('yyyy-LL') }}"), "costEur": 0, "aiCalls": 0}), (13, 9))
    w.add("Gmail - Send Failure Notice", *GMAIL, gmail_params(expr("{{ `Diagnostic impossible - ${$('Set - Evaluate References').first().json.repositories.map(r => r.key).join(' + ')}` }}"), expr(
        "{{ `<p>Le diagnostic <b>${$('Set - Evaluate References').first().json.request.id}</b> s’est arrêté. Aucun appel IA n’a été fait.</p><ul>${$('Set - Evaluate References').first().json.problems.map(p => `<li><b>${p.key}</b> - ${p.problem}</li>`).join('')}</ul>` }}")),
          (14, 9), **cred("gmail"), **RETRY)
    w.link("Switch - Reference Outcome", "Data Table - Log Failed Request", 2)
    w.chain("Data Table - Log Failed Request", "Gmail - Send Failure Notice")
    w.group("## Failed batch\nUnreachable repository, quota or missing tag: the cause is logged and sent, never a fake success.", ["Data Table - Log Failed Request", "Gmail - Send Failure Notice"])
