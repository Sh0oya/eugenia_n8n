"""GitHub evidence for the requested repository: native GitHub nodes only."""
from lib import *

REQ = "$('Set - Parse and Validate Request').first().json"
CFG = "$('CONFIGURATION').first().json"
SEL = "$('Set - Select Latest Release').first().json"
REPO = "$('GitHub - Get Repository').first().json"
STABLE = "($json.releases || []).find(r => r.tag_name && !r.draft && !r.prerelease)"
SECTION = r"/^#{1,4}\s.*(install|requirement|prerequisite|setup|hardware|compatib|platform|windows|wsl|gpu|cuda|driver|system|quick ?start|getting started)/i"
README = "String($('Extract from File - Read README').first().json.content || '')"
PROJECT = "String($('Extract from File - Read Project File').first().json.content || '')"


def E(js):
    return expr("{{ " + js + " }}")


def gh(resource, operation, owner, repo, **extra):
    return {"authentication": "accessToken", "resource": resource, "operation": operation,
            "owner": {"__rl": True, "mode": "name", "value": owner}, "repository": {"__rl": True, "mode": "name", "value": repo}, **extra}


def build(w):
    r = 8
    w.add("GitHub - Get Repository", *GITHUB, gh("repository", "get", "={{ $json.repository.owner }}", "={{ $json.repository.name }}"), (0, r), **cred("github"), **RETRY)
    w.add("GitHub - List Releases", *GITHUB, gh("release", "getAll", "={{ $json.owner.login }}", "={{ $json.name }}", returnAll=False, limit=30), (1, r),
          alwaysOutputData=True, **cred("github"), **RETRY,
          note="A repository without release gives one empty item. A real GitHub error stops the run and the error handler reports it.")
    w.add("Aggregate - Releases", *AGGREGATE, {"aggregate": "aggregateAllItemData", "destinationFieldName": "releases", "options": {}}, (2, r))
    w.add("Set - Select Latest Release", *SET, fields(
        ("repository", "object", E(REQ + ".repository")),
        ("info", "object", E(f"(r => ({{ description: r.description || '', topics: r.topics || [], license: r.license?.spdx_id || '', archived: !!r.archived }}))({REPO})")),
        ("tag", "string", E(f"{STABLE}?.tag_name || `${{{REPO}.default_branch}} (${{String({REPO}.pushed_at || '').slice(0, 10)}})`")),
        ("ref", "string", E(f"{STABLE}?.tag_name || {REPO}.default_branch")),
        ("releaseUrl", "string", E(f"{STABLE}?.html_url || ''")),
        ("publishedAt", "string", E(f"{STABLE}?.published_at || ''")),
        ("releaseNotes", "string", E(f"{CLEAN}(String({STABLE}?.body || '').slice(0, 3000))"))),
        (3, r), note="Examined version = newest release that is neither a draft nor a pre-release. Without one, the default branch at its last push date is examined and the report says so.")
    w.add("GitHub - Get README", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath="README.md",
                                             asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.ref }}}}"}),
          (4, r), onError="continueRegularOutput", **cred("github"), **RETRY)
    w.add("Extract from File - Read README", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (5, r), onError="continueRegularOutput")
    w.add("GitHub - Get Project File", *GITHUB, gh("file", "get", f"={{{{ {SEL}.repository.owner }}}}", f"={{{{ {SEL}.repository.name }}}}", filePath="pyproject.toml",
                                                   asBinaryProperty=True, binaryPropertyName="data", additionalParameters={"reference": f"={{{{ {SEL}.ref }}}}"}),
          (6, r), onError="continueRegularOutput", **cred("github"),
          note="Optional file at the examined version: declared dependencies and versions. A repository without it simply gives nothing; any other error is reported as a limit.")
    w.add("Extract from File - Read Project File", *EXTRACT_FILE, {"operation": "text", "binaryPropertyName": "data", "destinationKey": "content", "options": {}}, (7, r), onError="continueRegularOutput")
    # pyproject.toml without its comment lines, cut at maxDependencyChars: the cut is written in the text the AI reads and in the limits
    project_lines = "t.split('\\n').filter(l => l.trim() && !l.trim().startsWith('#')).join('\\n')"
    dependency_files = (f"(t => (c => c ? [{{ path: 'pyproject.toml', url: `${{{SEL}.repository.url}}/blob/${{{SEL}.ref}}/pyproject.toml`, "
                        f"text: {CLEAN}(c.length > {CFG}.maxDependencyChars ? `${{c.slice(0, {CFG}.maxDependencyChars)}}\\n[cut here: the rest of pyproject.toml was not read]` : c) }}] : [])({project_lines}))({PROJECT})")
    project_cut = f"(t => {project_lines}.length > {CFG}.maxDependencyChars)({PROJECT})"
    # A missing file is normal; any other error (rate limit, 5xx) must not look like a missing file.
    project_limit = (f"(e => e && !/not found|could not be found|404/i.test(String(e)) ? `${{{SEL}.repository.key}}: pyproject.toml could not be read (${{String(e).slice(0, 120)}})` : '')"
                     "($('GitHub - Get Project File').first().json.error)")
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
        ("limits", "array", E(f"[\n  !{README} ? `${{{SEL}.repository.key}}: README.md could not be read at the examined version (README.rst and other names are not read)` : '',\n"
                              f"  {README}.length > {CFG}.maxReadmeChars ? `${{{SEL}.repository.key}}: long README reduced to its introduction and installation sections` : '',\n"
                              f"  !{SEL}.releaseUrl ? `${{{SEL}.repository.key}}: no stable release published, the default branch was examined (${{{SEL}.tag}}) and can change` : '',\n"
                              f"  {project_limit},\n"
                              f"  {project_cut} ? `${{{SEL}.repository.key}}: pyproject.toml cut at ${{{CFG}.maxDependencyChars}} characters, the rest is unknown` : ''\n].filter(Boolean)"))),
        (8, r), note="Everything the AI may use about the repository: version, release notes, README (reduced to what matters) and pyproject.toml.")

    w.link("IF - Request Valid", "GitHub - Get Repository", 0)
    w.chain("GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "GitHub - Get README", "Extract from File - Read README",
            "GitHub - Get Project File", "Extract from File - Read Project File", "Set - Assemble Repository Evidence")
    w.group("## 2. GitHub evidence\nNative GitHub nodes read the repository, its releases, the README and pyproject.toml at the examined version. The latest stable release gives the version; a repository without one is examined on its default branch, and the report says so.",
            ["GitHub - Get Repository", "GitHub - List Releases", "Aggregate - Releases", "Set - Select Latest Release", "GitHub - Get README", "Extract from File - Read README",
             "GitHub - Get Project File", "Extract from File - Read Project File", "Set - Assemble Repository Evidence"])
