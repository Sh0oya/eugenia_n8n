"""GitHub evidence: one loop iteration per repository, native GitHub nodes only."""
from lib import *

LOOP = "Loop Over Items - Repositories"
ITEM = f"$('{LOOP}').first(1).json"
CFG = "$('CONFIGURATION').first().json"
SEL = "$('Set - Select Latest Release').first().json"
REPO = "$('GitHub - Get Repository').first().json"
STABLE = "($json.releases || []).find(r => r.tag_name && !r.draft && !r.prerelease)"
SECTION = r"/^#{1,4}\s.*(install|requirement|prerequisite|setup|hardware|compatib|platform|windows|wsl|gpu|cuda|driver|system|quick ?start|getting started)/i"
README = "String($('Extract from File - Read README').first().json.content || '')"


def E(js):
    return expr("{{ " + js + " }}")


def gh(resource, operation, owner, repo, **extra):
    return {"authentication": "accessToken", "resource": resource, "operation": operation,
            "owner": {"__rl": True, "mode": "name", "value": owner}, "repository": {"__rl": True, "mode": "name", "value": repo}, **extra}


def dependency_limit(node, path):
    """A missing file is normal; any other error (rate limit, 5xx) must not look like a missing file."""
    return (f"(e => e && !/not found|could not be found|404/i.test(String(e)) ? `${{{SEL}.repository.key}}: {path} could not be read (${{String(e).slice(0, 120)}})` : '')"
            f"($('GitHub - Get {node}').first().json.error)")


def build(w):
    r = 8
    w.add("Split Out - Repositories", *SPLIT_OUT, {"fieldToSplitOut": "repositories", "include": "allOtherFields", "options": {"destinationFieldName": "repository"}}, (0, r))
    w.add(LOOP, *LOOP_NODE, {"batchSize": 1, "options": {}}, (1, r), note="One pass per repository, so each repository is read with the same nodes.")
    w.add("GitHub - Get Repository", *GITHUB, gh("repository", "get", "={{ $json.repository.owner }}", "={{ $json.repository.name }}"), (2, r), **cred("github"), **RETRY)
    w.add("GitHub - List Releases", *GITHUB, gh("release", "getAll", "={{ $json.owner.login }}", "={{ $json.name }}", returnAll=False, limit=30), (3, r),
          alwaysOutputData=True, **cred("github"), **RETRY,
          note="A repository without release gives one empty item. A real GitHub error stops the run and the error handler reports it.")
    w.add("Aggregate - Releases", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "releases", "options": {}}, (4, r))
    w.add("Set - Select Latest Release", *SET, fields(
        ("repository", "object", E(f"{ITEM}.repository")),
        ("info", "object", E(f"(r => ({{ description: r.description || '', topics: r.topics || [], license: r.license?.spdx_id || '', archived: !!r.archived }}))({REPO})")),
        ("tag", "string", E(f"{STABLE}?.tag_name || `${{{REPO}.default_branch}} (${{String({REPO}.pushed_at || '').slice(0, 10)}})`")),
        ("ref", "string", E(f"{STABLE}?.tag_name || {REPO}.default_branch")),
        ("releaseUrl", "string", E(f"{STABLE}?.html_url || ''")),
        ("publishedAt", "string", E(f"{STABLE}?.published_at || ''")),
        ("releaseNotes", "string", E(f"{CLEAN}(String({STABLE}?.body || '').slice(0, 3000))"))),
        (5, r), note="Examined version = newest release that is neither a draft nor a pre-release. Without one, the default branch at its last push date is examined and the report says so.")
    w.add("GitHub - Get README", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath="README.md",
                                             asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.ref }}}}"}),
          (6, r), onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Extract from File - Read README", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (7, r), onError="continueRegularOutput")
    for node, path, col in (("Project File", "pyproject.toml", 8), ("Requirements File", "requirements.txt", 10)):
        w.add(f"GitHub - Get {node}", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath=path,
                                                  asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.ref }}}}"}),
              (col, r), onError="continueRegularOutput", **cred("github"),
              note="Optional file at the examined version: declared dependencies and versions. A repository without it simply gives nothing; any other error is reported as a limit." if node == "Project File" else None)
        w.add(f"Extract from File - Read {node}", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (col + 1, r), onError="continueRegularOutput")
    w.add("GitHub - List Issues", *GITHUB, gh("repository", "getIssues", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", returnAll=False, limit=40,
                                              getRepositoryIssuesFilters={"state": "all", "sort": "updated", "direction": "desc"}),
          (12, r), alwaysOutputData=True, onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Aggregate - Issues", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "issues", "options": {}}, (13, r))
    dependency = lambda node, path: f"[`{path}`, String($('Extract from File - Read {node}').first().json.content || '')]"  # noqa: E731
    dependency_files = (f"[{dependency('Project File', 'pyproject.toml')}, {dependency('Requirements File', 'requirements.txt')}].filter(f => f[1]).map(f => ({{ path: f[0], "
                        f"url: `${{{SEL}.repository.url}}/blob/${{{SEL}.ref}}/${{f[0]}}`, text: {CLEAN}(f[1].split('\\n').filter(l => l.trim() && !l.trim().startsWith('#')).join('\\n').slice(0, {CFG}.maxDependencyChars)) }}))")
    readme = (f"{CLEAN}((t => t.length <= {CFG}.maxReadmeChars ? t : t.split(/\\n(?=#{{1,2}}\\s)/).reduce((acc, s, i) => i === 0 ? s.slice(0, {CFG}.maxReadmeChars * 0.35) : {SECTION}.test(s.split('\\n')[0]) ? `${{acc}}\\n[...]\\n${{s}}` : acc, '').slice(0, {CFG}.maxReadmeChars))"
              f"({README}))")
    w.add("Set - Assemble Repository Evidence", *SET, fields(
        ("key", "string", E(f"{SEL}.repository.key")), ("url", "string", E(f"{SEL}.repository.url")),
        ("tag", "string", E(f"{SEL}.tag")), ("releaseUrl", "string", E(f"{SEL}.releaseUrl")), ("publishedAt", "string", E(f"{SEL}.publishedAt")),
        ("versionKind", "string", E(f"{SEL}.releaseUrl ? 'stable release' : 'default branch, no stable release'")),
        ("releaseNotes", "string", E(f"{SEL}.releaseNotes")),
        ("description", "string", E(f"{CLEAN}({SEL}.info.description)")), ("topics", "array", E(f"{SEL}.info.topics")),
        ("license", "string", E(f"{SEL}.info.license")), ("archived", "boolean", E(f"{SEL}.info.archived")),
        ("readme", "string", E(readme)),
        ("readmeUrl", "string", E(f"`${{{SEL}.repository.url}}/blob/${{{SEL}.ref}}/README.md`")),
        ("dependencyFiles", "array", E(dependency_files)),
        ("issues", "array", E(f"($json.issues || []).filter(i => i.title && !i.pull_request && /windows|wsl|install|gpu|intel|requirements|cuda|driver/i.test(i.title)).slice(0, {CFG}.maxIssues).map(i => ({{ title: {CLEAN}(i.title), url: i.html_url, state: i.state, updatedAt: i.updated_at, excerpt: {CLEAN}(String(i.body || '').slice(0, 600)) }}))")),
        ("limits", "array", E(f"[\n  !{README} ? `${{{SEL}.repository.key}}: README.md could not be read at the examined version (README.rst and other names are not read)` : '',\n"
                              f"  {README}.length > {CFG}.maxReadmeChars ? `${{{SEL}.repository.key}}: long README reduced to its introduction and installation sections` : '',\n"
                              f"  !{SEL}.releaseUrl ? `${{{SEL}.repository.key}}: no stable release published, the default branch was examined (${{{SEL}.tag}}) and can change` : '',\n"
                              f"  {dependency_limit('Project File', 'pyproject.toml')},\n  {dependency_limit('Requirements File', 'requirements.txt')},\n"
                              f"  ($json.issues || []).some(i => i.error) ? `${{{SEL}.repository.key}}: issues could not be read` : ''\n].filter(Boolean)"))),
        (14, r), note="Everything the AI may use about one repository: version, release notes, README (reduced to what matters), dependency files and issues about installation.")
    w.add("Aggregate - Repository Evidence", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "repositories", "options": {}}, (1, r + 1.5))

    w.link("IF - Request Valid", "Split Out - Repositories", 0)
    w.chain("Split Out - Repositories", LOOP)
    w.link(LOOP, "Aggregate - Repository Evidence", 0)
    w.link(LOOP, "GitHub - Get Repository", 1)
    w.chain("GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "GitHub - Get README", "Extract from File - Read README",
            "GitHub - Get Project File", "Extract from File - Read Project File", "GitHub - Get Requirements File", "Extract from File - Read Requirements File",
            "GitHub - List Issues", "Aggregate - Issues", "Set - Assemble Repository Evidence")
    w.link("Set - Assemble Repository Evidence", LOOP)
    w.group("## 2. GitHub evidence, one repository at a time\nNative GitHub nodes read the repository, its releases, the README and the dependency files at the examined version, and the issues. The latest stable release gives the version; a repository without one is examined on its default branch, and the report says so.",
            ["Split Out - Repositories", LOOP, "GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release",
             "GitHub - Get README", "Extract from File - Read README", "GitHub - Get Project File", "Extract from File - Read Project File",
             "GitHub - Get Requirements File", "Extract from File - Read Requirements File", "GitHub - List Issues", "Aggregate - Issues",
             "Set - Assemble Repository Evidence", "Aggregate - Repository Evidence"])
