// Checks the AI answer against the GitHub evidence and builds the final diagnostic JSON (schema 3.0).
// Evidence always wins over the model: repository, version and URL come from GitHub, never from the AI.
const config = $('CONFIGURATION').first().json;
const input = $('Set - Gather Prompt Inputs').first().json;
const parsed = $('Set - Parse and Validate Request').first().json;
const request = input.request;
const answer = $input.first().json;
const output = answer.output || {};
const failure = answer.error ? String(answer.error.message || answer.error).slice(0, 300) : '';
const repositories = input.repositories;

const CRITERIA = ['usefulFeatures', 'easeOfUse', 'easeOfInstallation', 'pcPerformance', 'cost', 'privacy', 'documentation', 'maintenance', 'modifiability'];
const reasons = [];
if (failure) reasons.push(`AI call failed: ${failure}`);
if (!failure) {
  const reports = Array.isArray(output.reports) ? output.reports : [];
  if (reports.length !== repositories.length) reasons.push('number of reports differs from the number of repositories');
  reports.forEach((report, index) => {
    const evidence = repositories[index] || {};
    if (String(report.repository).toLowerCase() !== evidence.key) reasons.push(`report ${index + 1}: repository differs from the GitHub evidence`);
    for (const key of CRITERIA) {
      const rating = report.ratings?.[key];
      if (!rating) reasons.push(`report ${index + 1}: rating ${key} is missing`);
      else if (rating.value !== null && !(Number.isInteger(rating.value) && rating.value >= 1 && rating.value <= 5)) reasons.push(`report ${index + 1}: rating ${key} is out of range`);
      else if (rating.value === null && !rating.unratedReason) reasons.push(`report ${index + 1}: rating ${key} is unknown without a reason`);
    }
  });
  if (request.mode === 'compare' && !output.comparison) reasons.push('comparison is missing in compare mode');
  if (!(output.sources || []).length) reasons.push('no source cited');
  if (!(output.usedContext || []).length) reasons.push('no personal context cited');
  const knownIds = new Set([...input.profile.map(p => p.id), ...input.inventory.map(o => o.id), ...input.decisions.map(d => d.id)]);
  if ((output.usedContext || []).some(c => !knownIds.has(c.id))) reasons.push('cited context is not part of the provided profile, inventory and decisions');
}

const ok = reasons.length === 0;
const decisionLabel = d => `${d.repository} (${d.decision})`;
const labelOf = id => input.profile.find(p => p.id === id) || input.inventory.find(o => o.id === id) || (d => (d ? { label: decisionLabel(d) } : {}))(input.decisions.find(x => x.id === id));
const typeOf = id => (input.profile.some(p => p.id === id) ? 'profile' : input.decisions.some(d => d.id === id) ? 'decision' : 'inventory');

const diagnostic = {
  schemaVersion: config.schemaVersion,
  id: request.id,
  date: new Date().toISOString(),
  status: ok ? 'done' : 'failed',
  mode: request.mode,
  goal: parsed.goal || null,
  repositories: repositories.map(r => ({ repository: r.key, url: r.url, version: r.tag, releaseUrl: r.releaseUrl || null, publishedAt: r.publishedAt || null, license: r.license || null })),
  usedProfile: {
    machine: input.machine,
    profileRevision: input.profileRevision || null,
    inventoryMatches: input.matches,
    decisions: input.decisions,
    passages: ok ? output.usedContext.map(c => ({ id: c.id, usage: c.usage, label: labelOf(c.id).label || labelOf(c.id).name || c.id, type: typeOf(c.id) })) : [],
  },
  recommendation: ok ? output.recommendation : 'Diagnostic non produit : relancer après correction de la cause.',
  reports: ok ? output.reports.map((report, index) => ({ ...report, repository: repositories[index].key, version: repositories[index].tag, url: repositories[index].url })) : [],
  comparison: ok && request.mode === 'compare' ? output.comparison : null,
  sources: ok ? output.sources : [],
  unknowns: ok ? (output.unknowns || []) : reasons,
  examinationLimits: input.limits,
  trace: {
    engine: 'gemini',
    model: config.diagnosticModel,
    // Same rule as the lookup in "Data Table - Find Existing Analysis": repositories with version, then the goal.
    reuseKey: `${repositories.map(r => `${r.key}@${r.tag}`).sort().join(' + ')} | ${parsed.goal.toLowerCase()}`,
    durationSeconds: Math.round((Date.now() - new Date(request.receivedAt).getTime()) / 1000),
    context: { profileSections: input.profile.length, inventoryItems: input.inventory.length, decisions: input.decisions.length },
  },
};

return [{ json: { diagnostic, failed: !ok, failureReason: reasons.join(' ; ') } }];
