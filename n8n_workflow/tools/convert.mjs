// Converts an exported n8n workflow JSON into the n8n SDK format (.workflow.ts) used by n8n-cli.
// Usage: node tools/convert.mjs <workflow.json> <workflow.workflow.ts>
import { generateWorkflowCode } from '@n8n/workflow-sdk';
import fs from 'node:fs';
import path from 'node:path';

const [, , source, target] = process.argv;
if (!source || !target) {
  console.error('Usage: node tools/convert.mjs <workflow.json> <workflow.workflow.ts>');
  process.exit(1);
}
const workflow = JSON.parse(fs.readFileSync(source, 'utf-8'));
const code = generateWorkflowCode(workflow);
fs.mkdirSync(path.dirname(target), { recursive: true });
fs.writeFileSync(target, code);
console.log(`${target}: ${code.length} characters`);
