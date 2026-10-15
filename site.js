const messages = {
  fr: {
    skip: "Aller au contenu",
    "nav.results": "Résultats",
    "nav.method": "Méthode",
    "nav.repo": "Dépôt ↗",
    "nav.aria": "Navigation principale",
    "metric.aria": "Benchmark à comparer",
    "chart.aria": "Comparaison des résultats",
    "view.aria": "Affichage des résultats",
    "view.delta": "Δ vs BF16",
    "view.score": "Score",
    "page.title": "Quantization Bench — Résultats",
    "page.description": "Écart mesuré par quantification sur les benchmarks, comparé à une référence BF16.",
    "hero.eyebrow": "QUANTIFICATION DE MODÈLES OUVERTS",
    "hero.title": "Quantization<br><em>Bench</em>",
    "hero.lede": "La perte mesurée, benchmark par benchmark.",
    "hero.cta": "Voir les résultats",
    "hero.scoreLabel": "DELTA MOYEN · GGUF Q4_K_M VS BF16",
    "hero.scoreNote": "5 MODÈLES · 3 BENCHMARKS",
    "hero.summary": "Δ vs BF16 · 5 runs appariés",
    "stats.models": "modèles",
    "stats.variants": "variantes",
    "stats.runs": "runs",
    "results.title": "Résultats",
    "results.caption": "Δ vs BF16 · points sur 100",
    "results.chartCaption": "Δ moyenne appariée · points /100 · négatif = perte",
    "table.model": "Modèle @ quant.",
    "results.runs": "5 runs · moyenne ± écart-type",
    "results.pairedRuns": "5 runs appariés · moyenne ± écart-type",
    "results.csv": "CSV ↗",
    "method.title": "Protocole",
    "method.repo": "Détails et données ↗",
    "method.models": "Modèles",
    "method.modelsSummary": "5 familles de modèles",
    "method.formats": "Formats",
    "method.scoring": "Scores",
    "method.environment": "Environnements",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 comparé à une référence RoleGPT.",
    "details.specific": "10 prompts liés à un rôle · ROUGE-L F1.",
    "details.character": "12 exemples · CharacterRM · note de 1–5 ramenée à 0–100.",
    "details.protocol": "Δ = score GGUF quantifié − BF16 du même modèle · 5 runs appariés.",
    "details.claims": "Les pertes annoncées par les éditeurs ne sont pas référencées.",
    "details.pending": "Pas encore exécutés :"
  },
  en: {
    skip: "Skip to content",
    "nav.results": "Results",
    "nav.method": "Method",
    "nav.repo": "Repository ↗",
    "nav.aria": "Primary navigation",
    "metric.aria": "Benchmark to compare",
    "chart.aria": "Results comparison",
    "view.aria": "Results view",
    "view.delta": "Δ vs BF16",
    "view.score": "Score",
    "page.title": "Quantization Bench — Results",
    "page.description": "Measured benchmark score changes by quantization, compared with BF16 baselines.",
    "hero.eyebrow": "OPEN MODEL QUANTIZATION",
    "hero.title": "Quantization<br><em>Bench</em>",
    "hero.lede": "Measured loss, benchmark by benchmark.",
    "hero.cta": "View results",
    "hero.scoreLabel": "AVERAGE DELTA · GGUF Q4_K_M VS BF16",
    "hero.scoreNote": "5 MODELS · 3 BENCHMARKS",
    "hero.summary": "Δ vs BF16 · 5 paired runs",
    "stats.models": "models",
    "stats.variants": "variants",
    "stats.runs": "runs",
    "results.title": "Results",
    "results.caption": "Δ vs BF16 · points on a 100-point scale",
    "results.chartCaption": "Mean paired Δ · points /100 · negative = loss",
    "table.model": "Model @ quant.",
    "results.runs": "5 runs · mean ± sample SD",
    "results.pairedRuns": "5 paired runs · mean ± sample SD",
    "results.csv": "CSV ↗",
    "method.title": "Protocol",
    "method.repo": "Details and data ↗",
    "method.models": "Models",
    "method.modelsSummary": "5 model families",
    "method.formats": "Formats",
    "method.scoring": "Scoring",
    "method.environment": "Runtimes",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 against a RoleGPT reference.",
    "details.specific": "10 role-specific prompts · ROUGE-L F1.",
    "details.character": "12 examples · CharacterRM · score mapped from 1–5 to 0–100.",
    "details.protocol": "Δ = quantized GGUF score − same-model BF16 score · 5 paired runs.",
    "details.claims": "Publisher-reported loss claims are not included.",
    "details.pending": "Not run yet:"
  }
};

const metrics = {
  rolebench_generalization: {
    mean: "rolebench_generalization_mean_100",
    sd: "rolebench_generalization_sd_100",
    delta: "rolebench_generalization_delta_vs_bf16_mean_pp",
    deltaSd: "rolebench_generalization_delta_vs_bf16_sd_pp"
  },
  rolebench_role_specific: {
    mean: "rolebench_role_specific_mean_100",
    sd: "rolebench_role_specific_sd_100",
    delta: "rolebench_role_specific_delta_vs_bf16_mean_pp",
    deltaSd: "rolebench_role_specific_delta_vs_bf16_sd_pp"
  },
  charactereval: {
    mean: "charactereval_mean_100",
    sd: "charactereval_sd_100",
    delta: "charactereval_delta_vs_bf16_mean_pp",
    deltaSd: "charactereval_delta_vs_bf16_sd_pp"
  }
};

const benchmarkTabs = {
  rolebench_generalization: "tab-general",
  rolebench_role_specific: "tab-specific",
  charactereval: "tab-character"
};
let activeLanguage = localStorage.getItem("quantization-bench-language") === "en" ? "en" : "fr";
let summaryRows = [];
let activeMetric = "rolebench_generalization";
let activeView = "delta";

function translate() {
  const words = messages[activeLanguage];
  document.documentElement.lang = activeLanguage;
  document.title = words["page.title"];
  document.querySelector('meta[name="description"]').setAttribute("content", words["page.description"]);
  document.querySelectorAll("[data-i18n]").forEach(function (element) {
    const text = words[element.dataset.i18n];
    if (text !== undefined) element.innerHTML = text;
  });
  document.querySelectorAll("[data-i18n-aria]").forEach(function (element) {
    const text = words[element.dataset.i18nAria];
    if (text !== undefined) element.setAttribute("aria-label", text);
  });
  document.getElementById("result-runs-label").textContent = activeView === "delta"
    ? words["results.pairedRuns"]
    : words["results.runs"];
  document.querySelectorAll("[data-language]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.language === activeLanguage));
  });
  document.querySelectorAll("[data-metric]").forEach(function (button) {
    const active = button.dataset.metric === activeMetric;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.querySelectorAll("[data-view]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.view === activeView));
  });
  const caption = activeView === "delta"
    ? words["results.chartCaption"]
    : (activeLanguage === "fr" ? "Moyenne ± écart-type · 5 runs · score /100" : "Mean ± sample SD · 5 runs · score /100");
  document.querySelector(".chart-caption").textContent = caption;
  document.getElementById("scale-label").textContent = activeView === "delta" ? "± points" : "0–100";
  document.querySelector(".section-intro").textContent = activeView === "delta"
    ? words["results.caption"]
    : (activeLanguage === "fr" ? "Moyenne ± écart-type · score /100" : "Mean ± sample SD · score /100");
}

function pretty(value) {
  return new Intl.NumberFormat(activeLanguage === "fr" ? "fr-FR" : "en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (character) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character];
  });
}

function modelTag(row) {
  if (row.model_tag || row.quantization) return row.model_tag || row.quantization;
  const name = (row.model_name || row.model_key || "model").toLowerCase().replaceAll(" ", "-");
  const quant = row.variant || "unknown";
  return name + "@" + quant.replace(/^gguf_/, "").replace(/^mlx_/, "mlx");
}

function scoreText(row, metricKey) {
  const metric = metrics[metricKey];
  const mean = row[metric.mean];
  if (typeof mean !== "number") return "—";
  const deviation = typeof row[metric.sd] === "number" ? row[metric.sd] : 0;
  return pretty(mean) + " ± " + pretty(deviation);
}

function deltaText(row, metricKey) {
  const metric = metrics[metricKey];
  const value = row[metric.delta];
  if (typeof value !== "number") return "—";
  const deviation = typeof row[metric.deltaSd] === "number" ? row[metric.deltaSd] : 0;
  const signed = value > 0 ? "+" + pretty(value) : value < 0 ? "−" + pretty(Math.abs(value)) : pretty(0);
  return signed + " ± " + pretty(deviation) + " pp";
}

function scoredRows(metricKey) {
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.mean] === "number"; });
}

function deltaRows(metricKey) {
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.delta] === "number"; });
}

function renderChart() {
  const metric = metrics[activeMetric];
  const deltaMode = activeView === "delta";
  const rows = (deltaMode ? deltaRows(activeMetric) : scoredRows(activeMetric)).sort(function (a, b) {
    return deltaMode ? a[metric.delta] - b[metric.delta] : b[metric.mean] - a[metric.mean];
  });
  const maxAbs = Math.max(1, ...rows.map(function (row) { return Math.abs(row[metric.delta] || 0); }));
  document.getElementById("metric-panel").setAttribute("aria-labelledby", benchmarkTabs[activeMetric]);
  document.getElementById("bar-chart").classList.toggle("delta-view", deltaMode);
  document.getElementById("bar-chart").innerHTML = rows.map(function (row, index) {
    const value = deltaMode ? row[metric.delta] : row[metric.mean];
    const text = deltaMode ? deltaText(row, activeMetric) : scoreText(row, activeMetric);
    const fill = deltaMode
      ? '<div class="bar-fill ' + (value < 0 ? "negative" : value > 0 ? "positive" : "neutral") + '" style="left:' + (value < 0 ? 50 + value / maxAbs * 50 : 50) + '%;width:' + Math.abs(value) / maxAbs * 50 + '%"></div>'
      : '<div class="bar-fill" style="width:' + Math.max(2, Math.min(100, value)) + '%"></div>';
    const label = escapeHtml(modelTag(row));
    const score = escapeHtml(text);
    return '<div class="bar-row ' + (deltaMode && value < 0 ? "is-loss" : index === 0 ? "is-best" : "") + '" title="' + label + ': ' + score + '"><span class="bar-label">' + label + '</span><div class="bar-track" role="img" aria-label="' + label + ': ' + score + '">' + fill + '</div><span class="bar-value">' + score + '</span></div>';
  }).join("");
}

function renderTable() {
  const rows = summaryRows.filter(function (row) {
    return activeView === "delta"
      ? typeof row.rolebench_generalization_delta_vs_bf16_mean_pp === "number"
      : typeof row.rolebench_generalization_mean_100 === "number" || typeof row.charactereval_mean_100 === "number";
  });
  document.getElementById("score-table").innerHTML = rows.map(function (row) {
    const label = escapeHtml(modelTag(row));
    const value = activeView === "delta" ? deltaText : scoreText;
    return '<tr><td><span class="model-name">' + label + '</span></td><td>' + value(row, "rolebench_generalization") + '</td><td>' + value(row, "rolebench_role_specific") + '</td><td>' + value(row, "charactereval") + '</td></tr>';
  }).join("");
}

function renderHero() {
  const q4Deltas = summaryRows.flatMap(function (row) {
    if (row.variant !== "gguf_q4_k_m") return [];
    return Object.keys(metrics).map(function (key) { return row[metrics[key].delta]; }).filter(function (value) { return typeof value === "number"; });
  });
  if (q4Deltas.length) {
    const mean = q4Deltas.reduce(function (total, value) { return total + value; }, 0) / q4Deltas.length;
    const value = mean > 0 ? "+" + pretty(mean) : mean < 0 ? "−" + pretty(Math.abs(mean)) : pretty(0);
    document.getElementById("hero-score-value").textContent = value + " pp";
    document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "vs BF16 du même modèle" : "vs same-model BF16";
  }
  const models = new Set(summaryRows.filter(function (row) {
    return typeof row.rolebench_generalization_mean_100 === "number";
  }).map(function (row) { return row.model_key; }));
  document.getElementById("stat-models").textContent = String(models.size);
  document.getElementById("stat-variants").textContent = String(scoredRows("rolebench_generalization").length);
}

function renderEnvironment(environment) {
  const hardware = environment.hardware || {};
  const gguf = environment.gguf_evaluation || {};
  const ggufHardware = gguf.hardware || {};
  const values = [
    ["MLX", hardware.chip, hardware.macos ? "macOS " + hardware.macos : ""],
    ["GGUF", ggufHardware.gpu, ggufHardware.os]
  ].map(function (parts) { return parts.filter(Boolean).join(" · "); }).filter(Boolean);
  document.getElementById("environment-summary").textContent = values.join(" / ") || "MLX · GGUF";
}

function renderAll() {
  translate();
  renderHero();
  renderTable();
  renderChart();
}

document.querySelectorAll("[data-language]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeLanguage = button.dataset.language;
    localStorage.setItem("quantization-bench-language", activeLanguage);
    renderAll();
  });
});
document.querySelectorAll("[data-metric]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeMetric = button.dataset.metric;
    renderAll();
  });
});
document.querySelectorAll("[data-view]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeView = button.dataset.view;
    renderAll();
  });
});

Promise.all([
  fetch("site-data/summary.json").then(function (response) { if (!response.ok) throw new Error("summary"); return response.json(); }),
  fetch("site-data/environment.json").then(function (response) { if (!response.ok) throw new Error("environment"); return response.json(); })
]).then(function (data) {
  summaryRows = data[0];
  renderEnvironment(data[1]);
  renderAll();
}).catch(function () {
  document.getElementById("hero-score-value").textContent = "—";
  document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "Données indisponibles." : "Data unavailable.";
});

renderAll();
