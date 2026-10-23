// The prompt against what the AI really receives: the examples and the rules must speak about tags that exist in the XML built by the workflow.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { evaluate, field, node } from './harness.mjs';

const read = name => fs.readFileSync(new URL(`../tools/prompts/${name}`, import.meta.url), 'utf8').replace(/\r\n/g, '\n');
const USER = read('diagnostic.user.xml');
const SYSTEM = read('diagnostic.system.md');

// ---- the inputs the AI receives, built by the workflow from sample data (every field of every node that feeds them) ----
const names = nodeName => node(nodeName).parameters.assignments.assignments.map(a => a.name);
const filled = (nodeName, values = {}) => Object.fromEntries(names(nodeName).map(n => [n, values[n] ?? 'x']));
const CONFIGURATION = { maxReadmeChars: 9000, maxDependencyChars: 5000 };
const SELECTED = { repository: { key: 'a/b', url: 'https://github.com/a/b' }, ref: 'v1', releaseUrl: 'u', tag: 'v1' };
const dependencyFiles = evaluate(field('Set - Assemble Repository Evidence', 'dependencyFiles'), {
  nodes: { CONFIGURATION, 'Set - Select Latest Release': SELECTED, 'Extract from File - Read Project File': { content: 'x = 1' } } });
const EVIDENCE = filled('Set - Assemble Repository Evidence', { topics: ['t'], archived: false, dependencyFiles, limits: ['a/b: a limit'] });
const PROFILE = '# Machine\n- texte du profil assez long pour être gardé\n\n```json\n{"revision":"r","machine":{"gpu":"Intel Arc"}}\n```';
const DECISION_PAGE = { url: 'u', last_edited_time: '2026-10-20T10:00:00Z', properties: { Decision: { select: { name: 'installé' } }, Depots: { rich_text: [{ plain_text: 'a/b' }] }, Version: { rich_text: [{ plain_text: 'a/b@v1' }] } } };
const INPUTS = Object.fromEntries(names('Set - Gather Prompt Inputs').map(name => [name, evaluate(field('Set - Gather Prompt Inputs', name), {
  json: { decisionPages: [DECISION_PAGE] },
  nodes: { CONFIGURATION, 'Set - Parse and Validate Request': { requestId: 'r', goal: '', receivedAt: 't' }, 'Notion - Get Profile': { markdown: PROFILE },
    'Aggregate - Inventory': { inventory: [filled('Set - Format Inventory Items')] }, 'Set - Assemble Repository Evidence': EVIDENCE },
})]));

// Paths of the XML elements the workflow produces (arrays become repeated elements, so they do not appear in the path).
const pathsOf = (value, prefix, out = new Set()) => {
  if (Array.isArray(value)) value.forEach(v => pathsOf(v, prefix, out));
  else if (value && typeof value === 'object') for (const [key, v] of Object.entries(value)) { out.add(`${prefix}/${key}`); pathsOf(v, `${prefix}/${key}`, out); }
  return out;
};
const REAL = pathsOf(INPUTS, 'inputs');
const isReal = path => path === 'inputs' || REAL.has(path) || path.startsWith('inputs/machine/');   // the machine block is free-form

const elementPaths = xml => {
  const stack = [], paths = [];
  for (const [, closing, tag] of xml.matchAll(/<(\/?)([A-Za-z][\w]*)>/g)) {
    if (closing) stack.pop();
    else { stack.push(tag); paths.push(stack.join('/')); }
  }
  return paths;
};

test('the inputs built by the workflow have the shape the prompt describes', () => {
  assert.deepEqual(Object.keys(INPUTS).sort(), ['decisions', 'inventory', 'limits', 'machine', 'matches', 'profile', 'profileRevision', 'repository', 'request']);
  for (const tag of ['profile', 'inventory', 'decisions', 'matches', 'repository', 'machine', 'limits']) assert.ok(REAL.has(`inputs/${tag}`), tag);
});

test('the limits are given once, at the top, not again inside the repository', () => {
  assert.ok(REAL.has('inputs/limits'));
  assert.equal(REAL.has('inputs/repository/limits'), false);
  assert.deepEqual(INPUTS.limits, ['a/b: a limit']);
});

test('every example speaks about elements that exist in the real inputs', () => {
  const examples = USER.match(/<example_\d+>[\s\S]*?<\/example_\d+>/g);
  assert.equal(examples.length, 5);
  for (const example of examples) {
    const inputs = example.match(/<inputs>[\s\S]*?<\/inputs>/)[0];
    for (const path of elementPaths(inputs)) assert.ok(isReal(path), `${example.slice(0, 11)}: <${path}> does not exist in the real inputs`);
  }
});

test('the rules and the examples use the real names of the fields', () => {
  for (const name of ['presence', 'analysedVersion', 'versionKind', 'dependencyFiles', 'matches', 'decisions', 'inventory', 'profile']) {
    assert.ok([...REAL].some(p => p.endsWith(`/${name}`)), `${name} is not a field of the inputs`);
    assert.ok(USER.includes(name), `${name} is not in the prompt`);
  }
  assert.doesNotMatch(USER, /<match>|<repositories>|<issues?>/);
});

test('the prompt follows the course: role alone in the system message, XML sections, 3 to 5 examples, inputs last', () => {
  assert.doesNotMatch(SYSTEM, /[{}]/, 'braces in the system message would be read as variables by the chain');
  assert.match(SYSTEM, /^<role>[\s\S]*<\/role>\s*$/);
  for (const section of ['goal', 'context', 'examples', 'output_format']) assert.match(USER, new RegExp(`<${section}>[\\s\\S]*</${section}>`), section);
  assert.equal((USER.match(/\{\{/g) || []).length, 1, 'only the inputs are an expression');
  assert.match(USER, /<inputs>\n\{\{ \$json\.data \}\}\n<\/inputs>\s*$/);
  assert.deepEqual([...USER.matchAll(/^(\d+)\. /gm)].map(m => Number(m[1])), Array.from({ length: 12 }, (_, i) => i + 1), 'the 12 rules are numbered without a gap');
});

test('the prompt knows nothing of the removed features', () => {
  assert.doesNotMatch(USER, /compare mode|comparison|issues about|reports/i);
});
