// Helpers shared by the tests: they read the generated workflow (exports/can-my-pc-run-it.json) and run its expressions and Code nodes
// with stubs, without n8n and without any network call.
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
export const workflow = JSON.parse(fs.readFileSync(process.env.WORKFLOW_JSON ?? new URL('exports/can-my-pc-run-it.json', root), 'utf8'));
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

export const node = name => {
  const found = workflow.nodes.find(n => n.name === name);
  if (!found) throw new Error(`node not found: ${name}`);
  return found;
};

// Value of a field of a Set node ("={{ ... }}").
export const field = (nodeName, fieldName) => {
  const assignment = node(nodeName).parameters.assignments.assignments.find(a => a.name === fieldName);
  if (!assignment) throw new Error(`field not found: ${nodeName}.${fieldName}`);
  return assignment.value;
};

// $('Node Name') stub: first(), last() and all() return the given json.
export const dollar = nodes => name => {
  if (!(name in nodes)) throw new Error(`no stub for $('${name}')`);
  const data = nodes[name];
  const items = (Array.isArray(data) ? data : [data]).map(json => ({ json }));
  return { first: () => items[0], last: () => items[items.length - 1], all: () => items };
};

// Evaluates one n8n expression with $json and $('...') stubs.
export const evaluate = (expression, { json = {}, nodes = {} } = {}) => {
  const body = expression.replace(/^=\s*\{\{/, '').replace(/\}\}\s*$/, '');
  return new Function('$json', '$', `return (${body});`)(json, dollar(nodes));
};

// Runs the jsCode of a Code node. `input` is what the node receives, `nodes` what $('...') returns.
export const runCode = (nodeName, { input, nodes, DateTime = {} }) =>
  new AsyncFunction('$', '$input', 'DateTime', node(nodeName).parameters.jsCode)(dollar(nodes), { first: () => ({ json: input }) }, DateTime);
