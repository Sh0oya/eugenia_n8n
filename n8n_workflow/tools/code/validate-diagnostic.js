// Checks the AI answer against the GitHub evidence and builds the final diagnostic JSON (schema 2.0).
// Evidence always wins over the model: repository, version and commit come from GitHub, never from the AI.
const config = $('CONFIGURATION').first().json;
const input = $('Set - Gather Prompt Inputs').first().json;
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
    if (String(report.repository).toLowerCase() !== evidence.key || report.commit !== evidence.commit) {
      reasons.push(`report ${index + 1}: repository or commit differs from the GitHub evidence`);
    }
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
  const knownIds = new Set([...input.passages.map(p => p.id), ...input.inventoryCatalog.map(c => c.id)]);
  if ((output.usedContext || []).some(c => !knownIds.has(c.id))) reasons.push('cited context is not part of the provided passages');
}

const ok = reasons.length === 0;
const labelOf = id => (input.passages.find(p => p.id === id) || input.inventoryCatalog.find(c => c.id === id) || {});
const estimateTokens = text => Math.ceil(String(text || '').length / 3.5);
const tokensIn = estimateTokens($('XML - Convert Inputs').first().json.data);
const tokensOut = estimateTokens(JSON.stringify(output));
const webCost = input.webResults.enabled ? config.webSearchCostEur : 0;
const costEur = Math.round(((tokensIn * config.rateInputEurPerMillion + tokensOut * config.rateOutputEurPerMillion) / 1e6 + webCost) * 10000) / 10000;

const diagnostic = {
  schemaVersion: config.schemaVersion,
  id: request.id,
  date: new Date().toISOString(),
  status: ok ? 'done' : 'failed',
  mode: request.mode,
  goal: request.goal || null,
  origin: request.origin,
  previousAnalysisUrl: request.previousUrl || null,
  previousAnalysisId: $('Set - Decide Next Step').first().json.previousId || null,
  repositories: repositories.map(r => ({ repository: r.key, url: r.url, version: r.tag, commit: r.commit, manualReference: r.manualReference, releaseUrl: r.releaseUrl || null, publishedAt: r.publishedAt || null, license: r.license || null })),
  usedProfile: {
    machine: input.machine,
    profileRevision: input.profileRevision || null,
    inventoryMatches: input.matches,
    passages: ok ? output.usedContext.map(c => ({ id: c.id, usage: c.usage, label: labelOf(c.id).label || labelOf(c.id).name || c.id, type: labelOf(c.id).type || 'inventory', url: labelOf(c.id).url || null })) : [],
  },
  recommendation: ok ? output.recommendation : 'Diagnostic non produit : relancer après correction de la cause.',
  reports: ok ? output.reports.map((report, index) => ({ ...report, repository: repositories[index].key, version: repositories[index].tag, commit: repositories[index].commit, url: repositories[index].url })) : [],
  comparison: ok && request.mode === 'compare' ? output.comparison : null,
  sources: ok ? output.sources : [],
  unknowns: ok ? (output.unknowns || []) : reasons,
  examinationLimits: input.limits,
  trace: {
    engine: 'gemini',
    model: config.diagnosticModel,
    reuseKey: $('Set - Decide Next Step').first().json.reuseKey,
    estimatedCostEur: costEur,
    estimatedTokens: { input: tokensIn, output: tokensOut },
    durationSeconds: Math.round((Date.now() - new Date(request.receivedAt).getTime()) / 1000),
    rag: { method: input.retrievalMethod, passages: input.passages.length, catalog: input.inventoryCatalog.length },
    webSearch: { enabled: input.webResults.enabled, sources: input.webResults.sources.length },
  },
};

return [{ json: { diagnostic, failed: !ok, failureReason: reasons.join(' ; ') } }];
