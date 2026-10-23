// Expressions of the workflow that decide something: request check, tool matching, version selection, cleaning, reuse.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { evaluate, field, node, workflow } from './harness.mjs';

const CONFIGURATION = { notionProfilePageId: 'p', notionInventoryDataSourceId: 'i', notionAnalysesDataSourceId: 'a', maxReadmeChars: 9000, maxDependencyChars: 5000 };

const parse = (githubUrl, name) => evaluate(field('Set - Parse and Validate Request', name), { json: { githubUrl }, nodes: { CONFIGURATION } });

test('request check accepts a repository link, with .git, a slash or a path', () => {
  for (const [url, key] of [['https://github.com/huggingface/lerobot', 'huggingface/lerobot'], ['https://github.com/o/r.git', 'o/r'], ['https://github.com/o/my.repo/', 'o/my.repo'], ['https://github.com/o/r/issues/3', 'o/r']]) {
    assert.equal(parse(url, 'repository').key, key, url);
    assert.deepEqual(parse(url, 'errors'), [], url);
  }
  assert.equal(parse('https://github.com/Hugging/LeRobot', 'repository').url, 'https://github.com/Hugging/LeRobot');
});

test('request check refuses GitHub pages that are not repositories, a name ending with a dot and other hosts', () => {
  for (const bad of ['https://github.com/orgs/acme', 'https://github.com/users/someone', 'https://github.com/a/b.', 'https://gitlab.com/a/b', 'http://github.com/a/b', 'github.com/a/b']) {
    assert.deepEqual(parse(bad, 'repository'), {}, bad);
    assert.match(parse(bad, 'errors')[0], /Not an https GitHub repository URL/, bad);
  }
});

test('request check refuses an empty request and more than one repository', () => {
  assert.match(parse('', 'errors').join(), /No GitHub URL given/);
  assert.match(parse('https://github.com/a/a https://github.com/b/b', 'errors').join(), /One repository per request \(2 links given\)/);
  assert.deepEqual(parse('https://github.com/a/a, https://github.com/b/b', 'repository'), {});
});

const inventory = ['LeRobot', 'n8n', 'Git', 'Python'].map((name, i) => ({ id: `inv-${i}`, name, state: 'installed', presence: 'present', version: '1' }));
const matchesFor = key => evaluate(field('Set - Gather Prompt Inputs', 'matches'), {
  nodes: { 'Set - Assemble Repository Evidence': { key }, 'Aggregate - Inventory': { inventory } },
}).map(m => `${m.repository}=${m.tool}`);

test('a repository matches an inventory tool only when the names are equal', () => {
  assert.deepEqual(matchesFor('huggingface/lerobot'), ['huggingface/lerobot=LeRobot']);
  assert.deepEqual(matchesFor('n8n-io/n8n'), ['n8n-io/n8n=n8n']);
  assert.deepEqual(matchesFor('git/git'), ['git/git=Git']);
  for (const key of ['go-gitea/gitea', 'someone/digital-twin', 'n8n-io/n8n-cli', 'x/lerobot-sim-extras', 'x/pythonista']) assert.deepEqual(matchesFor(key), [], key);
});

const select = (releases, repo) => name => evaluate(field('Set - Select Latest Release', name), { json: { releases }, nodes: { 'GitHub - Get Repository': repo } });
const REPO = { default_branch: 'main', pushed_at: '2026-10-20T10:00:00Z' };

test('the examined version is the newest stable release', () => {
  const pick = select([{ tag_name: 'v3-rc', prerelease: true }, { tag_name: 'v2.1', html_url: 'u' }, { tag_name: 'v2.0' }], REPO);
  assert.equal(pick('tag'), 'v2.1');
  assert.equal(pick('ref'), 'v2.1');
  assert.equal(pick('releaseUrl'), 'u');
});

test('without a stable release the default branch is examined, dated by its last push', () => {
  for (const releases of [[{}], [{ tag_name: 'v1-rc', prerelease: true }, { tag_name: 'v0', draft: true }]]) {
    const pick = select(releases, REPO);
    assert.equal(pick('tag'), 'main (2026-10-20)');
    assert.equal(pick('ref'), 'main');
    assert.equal(pick('releaseUrl'), '');
  }
});

test('control characters and a cut emoji are removed from the text sent to the XML node', async t => {
  const notes = select([{ tag_name: 'v1', body: `${'a'.repeat(2999)}\u{1F600}\u001b[31mred\u0000` }], REPO)('releaseNotes');
  assert.doesNotMatch(notes, /[\u0000-\u0008\u000B\u000C\u000E-\u001F]/);
  assert.ok(notes.isWellFormed());
  let Builder;
  try { Builder = createRequire(import.meta.url)('xml2js').Builder; } catch { t.diagnostic('xml2js is not installed: XML check skipped'); return; }
  assert.doesNotThrow(() => new Builder({ rootName: 'inputs', headless: true }).buildObject({ notes }));
});

const SELECTED = { repository: { key: 'o/r', url: 'https://github.com/o/r' }, tag: 'v1', ref: 'v1', releaseUrl: 'u' };
const evidence = (name, nodes) => evaluate(field('Set - Assemble Repository Evidence', name), { json: {}, nodes: { CONFIGURATION, 'Set - Select Latest Release': SELECTED, 'Extract from File - Read README': { content: 'readme' }, 'GitHub - Get Project File': {}, 'Extract from File - Read Project File': {}, ...nodes } });

test('a missing dependency file is normal, any other error is a stated limit', () => {
  assert.deepEqual(evidence('limits', {}), []);
  assert.deepEqual(evidence('limits', { 'GitHub - Get Project File': { error: 'The resource you are requesting could not be found' } }), []);
  assert.match(evidence('limits', { 'GitHub - Get Project File': { error: 'API rate limit exceeded' } }).join(), /o\/r: pyproject\.toml could not be read \(API rate limit exceeded\)/);
});

test('a repository without stable release says it in the limits', () => {
  const limits = evidence('limits', { 'Set - Select Latest Release': { ...SELECTED, tag: 'main (2026-10-20)', ref: 'main', releaseUrl: '' } });
  assert.match(limits.join(), /no stable release published, the default branch was examined \(main \(2026-10-20\)\)/);
});

test('pyproject.toml is given without comment lines and capped, or not at all', () => {
  const files = evidence('dependencyFiles', { CONFIGURATION: { ...CONFIGURATION, maxDependencyChars: 30 }, 'Extract from File - Read Project File': { content: '# comment\n[project]\nrequires-python = ">=3.12"\ndependencies = ["torch>=2.7"]\n' } });
  assert.deepEqual(files.map(f => [f.path, f.url]), [['pyproject.toml', 'https://github.com/o/r/blob/v1/pyproject.toml']]);
  assert.equal(files[0].text, '[project]\nrequires-python = ">=3.12"'.slice(0, 30));
  assert.deepEqual(evidence('dependencyFiles', {}), []);
});

const status = (notionUrl, limits) => evaluate(node('Data Table - Save Analysis').parameters.columns.value.deliveryStatus,
  { nodes: { 'Code - Render Report': { diagnostic: { examinationLimits: limits } }, 'Notion - Create Diagnostic Page': notionUrl ? { url: notionUrl } : { error: 'x' } } });

test('only a report with a Notion page and no unreadable file is marked complete', () => {
  assert.equal(status('https://notion.so/p', []), 'complete');
  assert.equal(status('https://notion.so/p', ['o/r: README.md could not be read at the examined version (README.rst and other names are not read)']), 'complete');
  assert.equal(status('https://notion.so/p', ['o/r: pyproject.toml could not be read (API rate limit exceeded)']), 'degraded');
  assert.equal(status('', []), 'notion failed');
});

test('the lookup of an existing analysis only returns reports that were fully delivered', () => {
  const conditions = node('Data Table - Find Existing Analysis').parameters.filters.conditions;
  assert.deepEqual(conditions.map(c => [c.keyName, c.keyValue]).filter(([k]) => k !== 'reuseKey'), [['status', 'done'], ['deliveryStatus', 'complete']]);
});

test('the Limit node cuts only outside production', () => {
  const maxItems = config => evaluate(node('Limit - Analyses Pages').parameters.maxItems, { nodes: { CONFIGURATION: config } });
  assert.equal(maxItems({ env: 'production', limitItems: 3 }), 999999);
  assert.equal(maxItems({ env: 'test', limitItems: 3 }), 3);
});

test('the workflow stays small and native: 40 nodes, no HTTP Request, two Code nodes, one repository per request', () => {
  const nodes = workflow.nodes.filter(n => !n.type.endsWith('stickyNote'));
  assert.equal(nodes.length, 40);
  assert.equal(nodes.filter(n => n.type === 'n8n-nodes-base.httpRequest').length, 0);
  assert.equal(nodes.filter(n => n.type === 'n8n-nodes-base.code').length, 2);
  assert.equal(nodes.filter(n => /Loop|Split Out|Issues|Requirements/.test(n.name)).length, 0);
});
