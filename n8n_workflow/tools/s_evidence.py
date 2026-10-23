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
    for node, path, col in (("Project File", "pyproject.toml", 9), ("Requirements File", "requirements.txt", 11)):
        w.add(f"GitHub - Get {node}", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath=path,
                                                  asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.tag }}}}"}),
              (col, r), onError="continueRegularOutput", **cred("github"),
              note="Optional file at the examined version: declared dependencies and versions. A repository without it simply gives nothing." if node == "Project File" else None)
        w.add(f"Extract from File - Read {node}", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (col + 1, r), onError="continueRegularOutput")
    w.add("GitHub - List Issues", *GITHUB, gh("repository", "getIssues", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", returnAll=False, limit=40,
                                              getRepositoryIssuesFilters={"state": "all", "sort": "updated", "direction": "desc"}),
          (13, r), alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Aggregate - Issues", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "issues", "options": {}}, (14, r))
    dependency = lambda node, path: f"[`{path}`, String($('Extract from File - Read {node}').first().json.content || '')]"  # noqa: E731
    dependency_files = (f"[{dependency('Project File', 'pyproject.toml')}, {dependency('Requirements File', 'requirements.txt')}].filter(f => f[1]).map(f => ({{ path: f[0], "
                        f"url: `${{{SEL}.repository.url}}/blob/${{{SEL}.tag}}/${{f[0]}}`, text: f[1].split('\\n').filter(l => l.trim() && !l.trim().startsWith('#')).join('\\n').slice(0, {CFG}.maxDependencyChars) }}))")
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
        ("dependencyFiles", "array", E(dependency_files)),
        ("issues", "array", E(f"($json.issues || []).filter(i => i.title && !i.pull_request && /windows|wsl|install|gpu|intel|requirements|cuda|driver/i.test(i.title)).slice(0, {CFG}.maxIssues).map(i => ({{ title: i.title, url: i.html_url, state: i.state, updatedAt: i.updated_at, excerpt: String(i.body || '').slice(0, 600) }}))")),
        ("limits", "array", E(f"[\n  !String($('Extract from File - Read README').first().json.content || '') ? `${{{SEL}.repository.key}}: README.md could not be read at the examined version` : '',\n"
                              f"  String($('Extract from File - Read README').first().json.content || '').length > {CFG}.maxReadmeChars ? `${{{SEL}.repository.key}}: long README reduced to its introduction and installation sections` : '',\n"
                              f"  ($json.issues || []).some(i => i.error) ? `${{{SEL}.repository.key}}: issues could not be read` : ''\n].filter(Boolean)"))),
        (15, r), note="Everything the AI may use about one repository: version, release notes, README (reduced to what matters), dependency files and issues about installation.")
    w.add("Aggregate - Repository Evidence", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "repositories", "options": {}}, (1, r + 1.5))

    w.link("IF - Request Valid", "Split Out - Repositories", 0)
    w.chain("Split Out - Repositories", LOOP)
    w.link(LOOP, "Aggregate - Repository Evidence", 0)
    w.link(LOOP, "GitHub - Get Repository", 1)
    w.chain("GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "IF - Release Found")
    w.link("IF - Release Found", "GitHub - Get README", 0)
    w.link("IF - Release Found", "Stop and Error - No Stable Release", 1)
    w.chain("GitHub - Get README", "Extract from File - Read README", "GitHub - Get Project File", "Extract from File - Read Project File", "GitHub - Get Requirements File",
            "Extract from File - Read Requirements File", "GitHub - List Issues", "Aggregate - Issues", "Set - Assemble Repository Evidence")
    w.link("Set - Assemble Repository Evidence", LOOP)
    w.group("## 2. GitHub evidence, one repository at a time\nNative GitHub nodes read the repository, its releases, the README and the dependency files at the examined tag, and the issues. The latest stable release gives the version. No stable release stops the run with a clear reason.",
            ["Split Out - Repositories", LOOP, "GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "IF - Release Found",
             "Stop and Error - No Stable Release", "GitHub - Get README", "Extract from File - Read README", "GitHub - Get Project File", "Extract from File - Read Project File",
             "GitHub - Get Requirements File", "Extract from File - Read Requirements File", "GitHub - List Issues", "Aggregate - Issues",
             "Set - Assemble Repository Evidence", "Aggregate - Repository Evidence"])
