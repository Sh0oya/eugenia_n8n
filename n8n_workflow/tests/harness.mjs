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

// Fixed clock for $now, and a minimal DateTime (n8n gives expressions the luxon one): enough to format a stored date.
const NOW = { toISODate: () => '2026-10-23', toISO: () => '2026-10-23T10:00:00.000+02:00', toFormat: () => '20261023-100000' };
export const DateTime = {
  fromISO: iso => {
    const [year, month, day] = String(iso).slice(0, 10).split('-');
    const value = { setZone: () => value, setLocale: () => value, toFormat: format => (format === 'dd/LL/yyyy' ? `${day}/${month}/${year}` : `${year}-${month}-${day}`) };
    return value;
  },
};

// Evaluates one n8n expression with $json, $now, DateTime and $('...') stubs.
export const evaluate = (expression, { json = {}, nodes = {} } = {}) => {
  const body = expression.replace(/^=\s*\{\{/, '').replace(/\}\}\s*$/, '');
  return new Function('$json', '$', '$now', 'DateTime', `return (${body});`)(json, dollar(nodes), NOW, DateTime);
};

// Runs the jsCode of a Code node. `input` is what the node receives, `nodes` what $('...') returns.
export const runCode = (nodeName, { input, nodes }) =>
  new AsyncFunction('$', '$input', 'DateTime', node(nodeName).parameters.jsCode)(dollar(nodes), { first: () => ({ json: input }) }, DateTime);
