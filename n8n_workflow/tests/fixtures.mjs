// Sample data shared by the tests: a complete AI answer, the inputs of the validation node, and helpers that run validation and rendering.
import { runCode } from './harness.mjs';

export const REPO = 'https://github.com/acme/tool';
export const GOAL = 'Entraîner un bras SO-101';
export const RATING = { value: 3, justification: 'x', confidence: 'low', unratedReason: null };
export const verdict = (detail = 'ok', evidence = `${REPO}/blob/v1/README.md#install`) => ({ verdict: 'compatible', detail, evidence });

export const report = (extra = {}) => ({
  repository: 'acme/tool', tldr: { recommendation: 'ok', mainBenefit: 'b', mainLimit: 'l', nextStep: 'n' }, usefulness: 'u',
  existingAndAlternatives: { knownEquivalents: [], externalAlternatives: [], conclusion: 'c' },
  compatibility: Object.fromEntries(['windows', 'wsl', 'cpu', 'gpu', 'ram', 'storage', 'dependencies'].map(k => [k, verdict()])),
  conflicts: [], risks: [], projectCosts: [],
  firstTrial: { feasibleLocally: true, prerequisites: [], steps: ['a'], expectedResult: 'r', durationMinutes: 20, resources: 'x', stop: 's', cleanup: 'c' },
  ratings: Object.fromEntries(['usefulFeatures', 'easeOfUse', 'easeOfInstallation', 'pcPerformance', 'cost', 'privacy', 'documentation', 'maintenance', 'modifiability'].map(k => [k, RATING])),
  examinedScope: { documents: [], limits: '' }, unknowns: [], ...extra,
});

export const answer = (overrides = {}) => ({
  output: { recommendation: 'ok', report: report(), usedContext: [{ id: 'profile-1', usage: 'u' }],
    sources: [{ url: `${REPO}/releases/tag/v1`, type: 'github', usage: 'u' }], unknowns: [], ...overrides },
});

export const EVIDENCE = { key: 'acme/tool', url: REPO, tag: 'v1', versionKind: 'stable release', releaseUrl: `${REPO}/releases/tag/v1`, publishedAt: '', license: 'MIT' };
export const CONFIGURATION = { schemaVersion: '4.0', diagnosticModel: 'gemini-flash-latest', notificationEmail: 'moi@example.com' };

// Output of "Code - Validate and Finalize Diagnostic" for a given AI answer (or error).
export const validate = (input, { limits = [] } = {}) => runCode('Code - Validate and Finalize Diagnostic', {
  input,
  nodes: {
    CONFIGURATION,
    'Set - Gather Prompt Inputs': {
      request: { id: 'req-1', receivedAt: new Date().toISOString() }, repository: EVIDENCE,
      profile: [{ id: 'profile-1', label: 'p', text: 't' }], inventory: [],
      decisions: [{ id: 'decision-1', repository: 'acme/old', decision: 'installé', url: 'https://www.notion.so/decision-1' }],
      machine: {}, profileRevision: '', matches: [], limits,
    },
    'Set - Parse and Validate Request': { goal: GOAL },
  },
}).then(([item]) => item.json);

// Output of "Code - Render Report" for a diagnostic.
export const render = diagnostic => runCode('Code - Render Report', { input: { diagnostic }, nodes: {} }).then(([{ json }]) => json);
