const messages = {
  fr: {
    skip: "Aller au contenu",
    "nav.results": "Résultats",
    "nav.method": "Méthode",
    "nav.repo": "Dépôt ↗",
    "nav.aria": "Navigation principale",
    "metric.aria": "Benchmark à comparer",
    "chart.aria": "Comparaison des scores",
    "page.title": "Roleplay Bench — Résultats",
    "page.description": "Comparaison de modèles ouverts compacts sur des benchmarks de jeu de rôle.",
    "hero.eyebrow": "BENCHMARK DE JEU DE RÔLE",
    "hero.title": "Petits modèles,<br><em>grand rôle.</em>",
    "hero.lede": "Modèles quantifiés · trois benchmarks · résultats reproductibles.",
    "hero.cta": "Voir les résultats",
    "hero.scoreLabel": "MEILLEUR SCORE · ROLEBENCH GENERALIZATION",
    "hero.scoreNote": "ROUGE-L F1 · MOYENNE ± ÉCART-TYPE",
    "hero.summary": "Résultats ouverts · 5 runs par variante",
    "stats.models": "modèles",
    "stats.variants": "variantes",
    "stats.runs": "runs",
    "results.title": "Résultats",
    "results.caption": "Moyenne ± écart-type · 5 runs",
    "results.chartCaption": "Moyenne ± écart-type",
    "table.model": "Modèle @ quant.",
    "results.runs": "5 runs · moyenne ± écart-type",
    "results.csv": "CSV ↗",
    "results.note": "Les scores diffèrent selon le benchmark ; comparez les modèles dans chaque colonne.",
    "method.title": "Protocole",
    "method.repo": "Détails et données ↗",
    "method.models": "Modèles",
    "method.modelsSummary": "4 familles de modèles",
    "method.formats": "Formats",
    "method.scoring": "Scores",
    "method.environment": "Environnements",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 comparé à une référence RoleGPT.",
    "details.specific": "10 prompts liés à un rôle · ROUGE-L F1.",
    "details.character": "12 exemples · CharacterRM · note de 1–5 ramenée à 0–100.",
    "details.protocol": "5 graines fixes · température 1 · top-p 0,95 · top-k 64 · 512 tokens.",
    "details.pending": "Pas encore exécutés :"
  },
  en: {
    skip: "Skip to content",
    "nav.results": "Results",
    "nav.method": "Method",
    "nav.repo": "Repository ↗",
    "nav.aria": "Primary navigation",
    "metric.aria": "Benchmark to compare",
    "chart.aria": "Score comparison",
    "page.title": "Roleplay Bench — Results",
    "page.description": "Compact open-weight models compared on role-play benchmarks.",
    "hero.eyebrow": "ROLE-PLAY MODEL BENCHMARK",
    "hero.title": "Small models,<br><em>big character.</em>",
    "hero.lede": "Quantized models · three benchmarks · reproducible results.",
    "hero.cta": "View results",
    "hero.scoreLabel": "TOP SCORE · ROLEBENCH GENERALIZATION",
    "hero.scoreNote": "ROUGE-L F1 · MEAN ± SD",
    "hero.summary": "Open results · 5 runs per variant",
    "stats.models": "models",
    "stats.variants": "variants",
    "stats.runs": "runs",
    "results.title": "Results",
    "results.caption": "Mean ± SD · 5 runs",
    "results.chartCaption": "Mean ± sample SD",
    "table.model": "Model @ quant.",
    "results.runs": "5 runs · mean ± sample SD",
    "results.csv": "CSV ↗",
    "results.note": "Scores differ by benchmark; compare models within each column.",
    "method.title": "Protocol",
    "method.repo": "Details and data ↗",
    "method.models": "Models",
    "method.modelsSummary": "4 model families",
    "method.formats": "Formats",
    "method.scoring": "Scoring",
    "method.environment": "Runtimes",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 against a RoleGPT reference.",
    "details.specific": "10 role-specific prompts · ROUGE-L F1.",
    "details.character": "12 examples · CharacterRM · score mapped from 1–5 to 0–100.",
    "details.protocol": "5 fixed seeds · temperature 1 · top-p 0.95 · top-k 64 · 512-token limit.",
    "details.pending": "Not run yet:"
  }
};

const metrics = {
  rolebench_generalization: {
    mean: "rolebench_generalization_mean_100",
    sd: "rolebench_generalization_sd_100"
  },
  rolebench_role_specific: {
    mean: "rolebench_role_specific_mean_100",
    sd: "rolebench_role_specific_sd_100"
  },
  charactereval: {
    mean: "charactereval_mean_100",
    sd: "charactereval_sd_100"
  }
};

const benchmarkTabs = {
  rolebench_generalization: "tab-general",
  rolebench_role_specific: "tab-specific",
  charactereval: "tab-character"
};
let activeLanguage = localStorage.getItem("roleplay-bench-language") === "en" ? "en" : "fr";
let summaryRows = [];
let activeMetric = "rolebench_generalization";

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
  document.querySelectorAll("[data-language]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.language === activeLanguage));
  });
  document.querySelectorAll("[data-metric]").forEach(function (button) {
    const active = button.dataset.metric === activeMetric;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
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

function scoredRows(metricKey) {
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.mean] === "number"; });
}

function renderChart() {
  const metric = metrics[activeMetric];
  const rows = scoredRows(activeMetric).sort(function (a, b) { return b[metric.mean] - a[metric.mean]; });
  document.getElementById("metric-panel").setAttribute("aria-labelledby", benchmarkTabs[activeMetric]);
  document.getElementById("bar-chart").innerHTML = rows.map(function (row, index) {
    const value = row[metric.mean];
    const width = Math.max(2, Math.min(100, value));
    const label = escapeHtml(modelTag(row));
    const score = escapeHtml(scoreText(row, activeMetric));
    return '<div class="bar-row ' + (index === 0 ? "is-best" : "") + '" title="' + label + ': ' + score + '"><span class="bar-label">' + label + '</span><div class="bar-track" role="img" aria-label="' + label + ': ' + score + '"><div class="bar-fill" style="width:' + width + '%"></div></div><span class="bar-value">' + score + '</span></div>';
  }).join("");
}

function renderTable() {
  const rows = summaryRows.filter(function (row) {
    return typeof row.rolebench_generalization_mean_100 === "number" || typeof row.charactereval_mean_100 === "number";
  });
  document.getElementById("score-table").innerHTML = rows.map(function (row) {
    const label = escapeHtml(modelTag(row));
    return '<tr><td><span class="model-name">' + label + '</span></td><td>' + scoreText(row, "rolebench_generalization") + '</td><td>' + scoreText(row, "rolebench_role_specific") + '</td><td>' + scoreText(row, "charactereval") + '</td></tr>';
  }).join("");
}

function renderHero() {
  const rows = scoredRows("rolebench_generalization").sort(function (a, b) {
    return b.rolebench_generalization_mean_100 - a.rolebench_generalization_mean_100;
  });
  if (rows.length) {
    document.getElementById("hero-score-value").textContent = pretty(rows[0].rolebench_generalization_mean_100);
    document.getElementById("hero-score-model").textContent = modelTag(rows[0]) + " · " + pretty(rows[0].rolebench_generalization_sd_100) + " SD";
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
    localStorage.setItem("roleplay-bench-language", activeLanguage);
    renderAll();
  });
});
document.querySelectorAll("[data-metric]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeMetric = button.dataset.metric;
    renderAll();
  });
});

Promise.all([
  fetch("data/summary.json").then(function (response) { if (!response.ok) throw new Error("summary"); return response.json(); }),
  fetch("data/environment.json").then(function (response) { if (!response.ok) throw new Error("environment"); return response.json(); })
]).then(function (data) {
  summaryRows = data[0];
  renderEnvironment(data[1]);
  renderAll();
}).catch(function () {
  document.getElementById("hero-score-value").textContent = "—";
  document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "Données indisponibles." : "Data unavailable.";
});

renderAll();
