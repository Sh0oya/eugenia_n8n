// The four e-mails of the workflow, rendered from sample data (no sending): report, report of a failed diagnostic, existing report, error alert.
import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluate, field, node } from './harness.mjs';
import { CONFIGURATION, answer, render, report, validate } from './fixtures.mjs';

const GMAIL_NODES = ['Gmail - Send Report', 'Gmail - Send Existing Report', 'Gmail - Send Alert'];
const NOTION_URL = 'https://www.notion.so/exemple-123';

const gmail = (name, nodes = {}, json = {}) => {
  const p = node(name).parameters;
  const ctx = { json, nodes: { CONFIGURATION, ...nodes } };
  return { to: evaluate(p.sendTo, ctx), subject: evaluate(p.subject, ctx), html: evaluate(p.message, ctx), type: p.emailType, options: p.options };
};

// The e-mail sent after the Notion page was created (or not), for an AI answer.
const reportMail = async (input, { notion = { url: NOTION_URL }, limits = [] } = {}) => {
  const { diagnostic } = await validate(input, { limits });
  return gmail('Gmail - Send Report', { 'Code - Render Report': await render(diagnostic), 'Notion - Create Diagnostic Page': notion });
};

test('every e-mail is HTML, sent from the service name, to the address of CONFIGURATION, without attachment', () => {
  for (const name of GMAIL_NODES) {
    const p = node(name).parameters;
    assert.equal(p.emailType, 'html', name);
    assert.equal(p.options.senderName, 'Can My PC Run It', name);
    assert.equal(p.options.appendAttribution, false, name);
    assert.equal(p.options.attachmentsUi, undefined, name);
    assert.equal(evaluate(p.sendTo, { nodes: { CONFIGURATION } }), 'moi@example.com', name);
  }
});

test('report e-mail: subject, recommendation card, the seven compatibility rows, link to the Notion page', async () => {
  const mail = await reportMail(answer({ report: report({ tldr: { recommendation: 'Garder la version installée', mainBenefit: 'Utile', mainLimit: 'Pas de CUDA', nextStep: 'Rien à faire' } }), recommendation: 'Garder la version installée' }));
  assert.equal(mail.subject, 'Diagnostic — acme/tool');
  assert.match(mail.html, /^<!doctype html>/);
  assert.match(mail.html, /Garder la version installée/);
  assert.match(mail.html, /href="https:\/\/www\.notion\.so\/exemple-123"[^>]*>Ouvrir le rapport dans Notion/);
  assert.doesNotMatch(mail.html, /__NOTION_BLOCK__/);
  for (const row of ['Windows 11', 'WSL Ubuntu', 'CPU', 'GPU', 'RAM', 'Stockage', 'Dépendances']) assert.match(mail.html, new RegExp(`>${row}<`), row);
  for (const heading of ['Utilité', 'Compatibilité', 'Premier essai', 'Notes']) assert.match(mail.html, new RegExp(heading, 'i'), heading);
  assert.match(mail.html, /version <b[^>]*>v1<\/b>/);
  assert.match(mail.html, /Le JSON complet du diagnostic est en bas de la page Notion/);
  assert.doesNotMatch(mail.html, /pièce jointe/);
});

test('report e-mail: the limits of the examination are listed', async () => {
  const mail = await reportMail(answer(), { limits: ['acme/tool: README.md could not be read at the examined version (README.rst and other names are not read)'] });
  assert.match(mail.html, /Limites : acme\/tool: README\.md could not be read/);
});

test('report e-mail: when Notion fails, the e-mail says so and still carries the report', async () => {
  const mail = await reportMail(answer(), { notion: { error: { message: 'Notion API error' } } });
  assert.match(mail.html, /Page Notion non créée \(Notion API error\)/);
  assert.doesNotMatch(mail.html, /__NOTION_BLOCK__|href=""/);
  assert.match(mail.html, /Compatibilité/i);
});

test('report e-mail: text written by the AI cannot inject HTML', async () => {
  const hostile = report({ tldr: { recommendation: '<b>gras</b> & <script>alert(1)</script> et 5 < 6', mainBenefit: 'b', mainLimit: 'l', nextStep: 'n' } });
  const mail = await reportMail(answer({ report: hostile }));
  assert.doesNotMatch(mail.html, /<script|<b>gras/);
  assert.match(mail.html, /&amp;/);
  assert.match(mail.html, /5 &lt; 6/);
});

test('failed diagnostic: the e-mail announces the failure and its reason, with no report card', async () => {
  const mail = await reportMail({ error: { message: 'service unavailable' } });
  assert.equal(mail.subject, 'Échec du diagnostic — acme/tool');
  assert.match(mail.html, /AI call failed: service unavailable/);
  assert.match(mail.html, /#dc2626/);
  assert.doesNotMatch(mail.html, />Compatibilité</i);
  assert.match(mail.html, /Ouvrir le rapport dans Notion/);
});

const existing = json => gmail('Gmail - Send Existing Report', {}, { repositoriesKey: 'acme/tool', versions: 'acme/tool@v1', summary: 'Garder', notionUrl: NOTION_URL, ...json });

test('existing report e-mail: says when the analysis was made, with its version, and links to the page', () => {
  const mail = existing({ updatedAt: '2026-10-23T08:00:00.000Z', createdAt: '2026-10-01T08:00:00.000Z' });
  assert.equal(mail.subject, 'Rapport existant - acme/tool');
  assert.match(mail.html, /analysé le <b>23\/10\/2026<\/b> avec la même version \(acme\/tool@v1\)/);
  assert.match(mail.html, /Aucune nouvelle analyse n’a été lancée/);
  assert.match(mail.html, new RegExp(`<a href="${NOTION_URL}">${NOTION_URL}</a>`));
  assert.match(mail.html, /« Refaire l’analyse » sur Oui/);
});

test('existing report e-mail: the date is the last update, the creation date only when there is none', () => {
  assert.match(existing({ createdAt: '2026-10-01T08:00:00.000Z' }).html, /<b>01\/10\/2026<\/b>/);
  assert.match(existing({ updatedAt: '2026-10-23T08:00:00.000Z', createdAt: '2026-10-01T08:00:00.000Z' }).html, /<b>23\/10\/2026<\/b>/);
});

test('existing report e-mail: the stored summary is escaped', () => {
  const mail = existing({ updatedAt: '2026-10-23T08:00:00.000Z', summary: '<script>x</script> & <b>y' });
  assert.doesNotMatch(mail.html, /<script/);
  assert.match(mail.html, /&lt;script>x&lt;\/script> &amp; &lt;b>y/);
});

// What the Error Trigger gives the workflow, and what the error handler makes of it.
const failure = (message, extra = {}) => ({ workflow: { name: 'Can My PC Run It' }, execution: { id: '123', url: 'https://n8n.example/execution/123', lastNodeExecuted: 'GitHub - Get Repository', error: { message }, ...extra } });
const incident = json => Object.fromEntries(node('Set - Format Incident').parameters.assignments.assignments.map(a => [a.name, evaluate(a.value, { json })]));
const alertMail = json => gmail('Gmail - Send Alert', { 'Set - Format Incident': incident(json) }, json);

test('error handler: the incident keeps the workflow, the node, the message, the execution and its link', () => {
  assert.deepEqual(incident(failure('Not Found')), { workflowName: 'Can My PC Run It', nodeName: 'GitHub - Get Repository', errorMessage: 'Not Found', executionId: '123', executionUrl: 'https://n8n.example/execution/123' });
  assert.deepEqual(incident({ execution: {} }), { workflowName: 'Unknown workflow', nodeName: 'Unknown node', errorMessage: 'Unknown error', executionId: '', executionUrl: '' });
  assert.equal(incident(failure('x'.repeat(5000))).errorMessage.length, 1000);
  const columns = node('Data Table - Log Incident').parameters.columns.value;
  assert.deepEqual(Object.keys(columns).sort(), ['errorMessage', 'executionId', 'executionUrl', 'nodeName', 'workflowName']);
});

test('error alert e-mail: names the workflow and the node, escapes the message, links to the failed execution', () => {
  const mail = alertMail(failure('Not Found <b> & more'));
  assert.equal(mail.subject, 'Échec - Can My PC Run It');
  assert.match(mail.html, /<b>Node<\/b> : GitHub - Get Repository/);
  assert.match(mail.html, /Not Found &lt;b> &amp; more/);
  assert.doesNotMatch(mail.html, /<b> &/);
  assert.match(mail.html, /<a href="https:\/\/n8n\.example\/execution\/123">Ouvrir l’exécution en échec<\/a>/);
});

test('invalid request: the reason reaches the alert e-mail', () => {
  const message = evaluate(node('Stop and Error - Invalid Request').parameters.errorMessage, { json: { errors: ['Not an https GitHub repository URL: gitlab.com/a/b', 'One repository per request (2 links given)'] } });
  assert.equal(message, 'Invalid request: Not an https GitHub repository URL: gitlab.com/a/b ; One repository per request (2 links given)');
  assert.match(alertMail(failure(message, { lastNodeExecuted: 'Stop and Error - Invalid Request' })).html, /Invalid request: Not an https GitHub repository URL: gitlab\.com\/a\/b ; One repository per request/);
});

test('each run takes the right branch: the form starts an analysis, the error trigger the error handler', () => {
  const rules = node('Switch - Route by Trigger').parameters.rules.values;
  const matches = json => rules.map(rule => evaluate(rule.conditions.conditions[0].leftValue, { json }));
  assert.deepEqual(matches({ githubUrl: 'https://github.com/a/b', goal: '', forceNew: 'Non' }), [true, false]);
  assert.deepEqual(matches(failure('x')), [false, true]);
  assert.equal(field('Set - Parse and Validate Request', 'repository').includes('githubUrl'), true);
});
