"""GitHub evidence: one loop iteration per repository, native GitHub nodes only."""
from lib import *

LOOP = "Loop Over Items - Repositories"
ITEM = f"$('{LOOP}').first(1).json"
CFG = "$('CONFIGURATION').first().json"
SEL = "$('Set - Select Latest Release').first().json"
STABLE = "($json.releases || []).find(r => r.tag_name && !r.draft && !r.prerelease)"
SECTION = r"/^#{1,4}\s.*(install|requirement|prerequisite|setup|hardware|compatib|platform|windows|wsl|gpu|cuda|driver|system|quick ?start|getting started)/i"


def E(js):
    return expr("{{ " + js + " }}")


def gh(resource, operation, owner, repo, **extra):
    return {"authentication": "accessToken", "resource": resource, "operation": operation,
            "owner": {"__rl": True, "mode": "name", "value": owner}, "repository": {"__rl": True, "mode": "name", "value": repo}, **extra}


def build(w):
    r = 8
    w.add("Split Out - Repositories", *SPLIT_OUT, {"fieldToSplitOut": "repositories", "include": "allOtherFields", "options": {"destinationFieldName": "repository"}}, (0, r))
    w.add(LOOP, *LOOP_NODE, {"batchSize": 1, "options": {}}, (1, r), note="One pass per repository, so each repository is read with the same nodes.")
    w.add("GitHub - Get Repository", *GITHUB, gh("repository", "get", "={{ $json.repository.owner }}", "={{ $json.repository.name }}"), (2, r), **cred("github"), **RETRY)
    w.add("GitHub - List Releases", *GITHUB, gh("release", "getAll", "={{ $json.owner.login }}", "={{ $json.name }}", returnAll=False, limit=30), (3, r),
          alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Aggregate - Releases", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "releases", "options": {}}, (4, r))
    w.add("Set - Select Latest Release", *SET, fields(
        ("repository", "object", E(f"{ITEM}.repository")),
        ("info", "object", E("(r => ({ description: r.description || '', topics: r.topics || [], license: r.license?.spdx_id || '', archived: !!r.archived }))($('GitHub - Get Repository').first().json)")),
        ("tag", "string", E(f"{STABLE}?.tag_name || ''")),
        ("releaseUrl", "string", E(f"{STABLE}?.html_url || ''")),
        ("publishedAt", "string", E(f"{STABLE}?.published_at || ''")),
        ("releaseNotes", "string", E(f"String({STABLE}?.body || '').slice(0, 3000)")),
        ("problem", "string", E("($json.releases || []).some(r => r.error) ? `GitHub unavailable while reading releases (${String(($json.releases || []).find(r => r.error)?.error || '').slice(0, 120)})` : 'No stable release published (drafts and pre-releases are ignored)'"))),
        (5, r), note="Latest stable release = newest release that is neither a draft nor a pre-release. Its tag is the version that is examined.")
    w.add("IF - Release Found", *IF, {"conditions": conditions(cond(E("!!$json.tag"))), "options": {}}, (6, r))
    w.add("Stop and Error - No Stable Release", *STOP_ERROR, {"errorMessage": E("`${$json.repository.key}: ${$json.problem}`")}, (6, r + 1.2),
          note="Without a stable release there is nothing reliable to examine: the run stops and the error handler sends the reason.")
    w.add("GitHub - Get README", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath="README.md",
                                             asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.tag }}}}"}),
          (7, r), onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Extract from File - Read README", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (8, r), onError="continueRegularOutput")
    w.add("GitHub - List Issues", *GITHUB, gh("repository", "getIssues", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", returnAll=False, limit=40,
                                              getRepositoryIssuesFilters={"state": "all", "sort": "updated", "direction": "desc"}),
          (9, r), alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Aggregate - Issues", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "issues", "options": {}}, (10, r))
    readme = (f"(t => t.length <= {CFG}.maxReadmeChars ? t : t.split(/\\n(?=#{{1,2}}\\s)/).reduce((acc, s, i) => i === 0 ? s.slice(0, {CFG}.maxReadmeChars * 0.35) : {SECTION}.test(s.split('\\n')[0]) ? `${{acc}}\\n[...]\\n${{s}}` : acc, '').slice(0, {CFG}.maxReadmeChars))"
              f"(String($('Extract from File - Read README').first().json.content || ''))")
    w.add("Set - Assemble Repository Evidence", *SET, fields(
        ("key", "string", E(f"{SEL}.repository.key")), ("url", "string", E(f"{SEL}.repository.url")),
        ("tag", "string", E(f"{SEL}.tag")), ("releaseUrl", "string", E(f"{SEL}.releaseUrl")), ("publishedAt", "string", E(f"{SEL}.publishedAt")),
        ("releaseNotes", "string", E(f"{SEL}.releaseNotes")),
        ("description", "string", E(f"{SEL}.info.description")), ("topics", "array", E(f"{SEL}.info.topics")),
        ("license", "string", E(f"{SEL}.info.license")), ("archived", "boolean", E(f"{SEL}.info.archived")),
        ("readme", "string", E(readme)),
        ("readmeUrl", "string", E(f"`${{{SEL}.repository.url}}/blob/${{{SEL}.tag}}/README.md`")),
        ("issues", "array", E(f"($json.issues || []).filter(i => i.title && !i.pull_request && /windows|wsl|install|gpu|intel|requirements|cuda|driver/i.test(i.title)).slice(0, {CFG}.maxIssues).map(i => ({{ title: i.title, url: i.html_url, state: i.state, updatedAt: i.updated_at, excerpt: String(i.body || '').slice(0, 600) }}))")),
        ("limits", "array", E(f"[\n  !String($('Extract from File - Read README').first().json.content || '') ? `${{{SEL}.repository.key}}: README.md could not be read at the examined version` : '',\n"
                              f"  String($('Extract from File - Read README').first().json.content || '').length > {CFG}.maxReadmeChars ? `${{{SEL}.repository.key}}: long README reduced to its introduction and installation sections` : '',\n"
                              f"  ($json.issues || []).some(i => i.error) ? `${{{SEL}.repository.key}}: issues could not be read` : ''\n].filter(Boolean)"))),
        (11, r), note="Everything the AI may use about one repository: version, release notes, README (reduced to what matters) and issues about installation.")
    w.add("Aggregate - Repository Evidence", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "repositories", "options": {}}, (1, r + 1.5))

    w.link("IF - Request Valid", "Split Out - Repositories", 0)
    w.chain("Split Out - Repositories", LOOP)
    w.link(LOOP, "Aggregate - Repository Evidence", 0)
    w.link(LOOP, "GitHub - Get Repository", 1)
    w.chain("GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "IF - Release Found")
    w.link("IF - Release Found", "GitHub - Get README", 0)
    w.link("IF - Release Found", "Stop and Error - No Stable Release", 1)
    w.chain("GitHub - Get README", "Extract from File - Read README", "GitHub - List Issues", "Aggregate - Issues", "Set - Assemble Repository Evidence")
    w.link("Set - Assemble Repository Evidence", LOOP)
    w.group("## 2. GitHub evidence, one repository at a time\nNative GitHub nodes read the repository, its releases, the README at the examined tag and the issues. The latest stable release gives the version. No stable release stops the run with a clear reason.",
            ["Split Out - Repositories", LOOP, "GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "IF - Release Found",
             "Stop and Error - No Stable Release", "GitHub - Get README", "Extract from File - Read README", "GitHub - List Issues", "Aggregate - Issues",
             "Set - Assemble Repository Evidence", "Aggregate - Repository Evidence"])
