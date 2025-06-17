const algorithmSelect = document.getElementById('algorithm');
const datasetInput = document.getElementById('dataset');
const dropzone = document.getElementById('dropzone');
const runBtn = document.getElementById('run');
const benchBtn = document.getElementById('bench');
const exportBtn = document.getElementById('export');
const toggleTheme = document.getElementById('toggle-theme');
const searchBox = document.getElementById('search-box');
const searchBtn = document.getElementById('search-btn');
const viz = d3.select('#visualization');
const resultsDiv = document.getElementById('results');
const benchmarkDiv = document.getElementById('benchmark');
const logDiv = document.getElementById('log');
const searchResults = document.getElementById('search-results');
let currentData = null;
let lastResult = null;
let algorithms = [];

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(JSON.parse(reader.result));
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

async function initAlgorithms() {
  const res = await fetch('http://localhost:8000/api/algorithms');
  const data = await res.json();
  algorithms = data.algorithms;
  algorithmSelect.innerHTML = algorithms.map(a => `<option value="${a}">${a}</option>`).join('');
}

function initLogs() {
  const es = new EventSource('http://localhost:8000/api/logs');
  es.onmessage = e => {
    logDiv.textContent += e.data + '\n';
    logDiv.scrollTop = logDiv.scrollHeight;
  };
}

async function runAlgorithm() {
  const algorithm = algorithmSelect.value;
  if (!currentData) {
    alert('Please upload a dataset');
    return;
  }
  const res = await fetch('http://localhost:8000/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algorithm, data: currentData })
  });
  if (!res.ok) {
    alert('Error running algorithm');
    return;
  }
  const result = await res.json();
  lastResult = result;
  showResult(algorithm, result);
}

async function runBenchmark() {
  if (!currentData) {
    alert('Please upload a dataset');
    return;
  }
  const res = await fetch('http://localhost:8000/api/benchmark', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algorithms, data: currentData })
  });
  const result = await res.json();
  benchmarkDiv.textContent = JSON.stringify(result.results, null, 2);
}

function showResult(algorithm, result) {
  resultsDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
  viz.selectAll('*').remove();
  if (algorithm === 'tsp') {
    drawTsp(result);
  } else if (algorithm === 'dijkstra') {
    drawDijkstra(result);
  }
}

function drawTsp(result) {
  const width = parseInt(viz.style('width'));
  const height = parseInt(viz.style('height'));
  const svg = viz.append('svg').attr('width', width).attr('height', height);
  const x = d3.scaleLinear().domain(d3.extent(result.points, d => d.x)).range([20, width-20]);
  const y = d3.scaleLinear().domain(d3.extent(result.points, d => d.y)).range([height-20, 20]);
  svg.selectAll('circle')
    .data(result.points)
    .enter()
    .append('circle')
    .attr('cx', d => x(d.x))
    .attr('cy', d => y(d.y))
    .attr('r', 5)
    .attr('fill', 'steelblue');
  svg.append('path')
    .attr('d', d3.line()
      .x(d => x(result.points[d].x))
      .y(d => y(result.points[d].y))
    (result.path))
    .attr('fill', 'none')
    .attr('stroke', 'red');
}

function drawDijkstra(result) {
  const width = parseInt(viz.style('width'));
  const height = parseInt(viz.style('height'));
  const svg = viz.append('svg').attr('width', width).attr('height', height);
  const x = d3.scaleLinear().domain(d3.extent(result.nodes, d => d.x)).range([20, width-20]);
  const y = d3.scaleLinear().domain(d3.extent(result.nodes, d => d.y)).range([height-20, 20]);
  svg.selectAll('line')
    .data(result.all_edges)
    .enter()
    .append('line')
    .attr('x1', d => x(result.nodes[d.source].x))
    .attr('y1', d => y(result.nodes[d.source].y))
    .attr('x2', d => x(result.nodes[d.target].x))
    .attr('y2', d => y(result.nodes[d.target].y))
    .attr('stroke', '#ccc');
  svg.selectAll('circle')
    .data(result.nodes)
    .enter()
    .append('circle')
    .attr('cx', d => x(d.x))
    .attr('cy', d => y(d.y))
    .attr('r', 5)
    .attr('fill', 'steelblue');
  svg.append('path')
    .attr('d', d3.line()
      .x(d => x(result.nodes[d].x))
      .y(d => y(result.nodes[d].y))
    (result.path))
    .attr('fill', 'none')
    .attr('stroke', 'red');
}

function exportCSV() {
  if (!lastResult) return;
  const csv = lastResult.path.join(',');
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'result.csv';
  a.click();
  URL.revokeObjectURL(a.href);
}

async function search() {
  const q = searchBox.value;
  if (!q) return;
  const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  searchResults.textContent = JSON.stringify(data.results, null, 2);
}

datasetInput.addEventListener('change', async e => {
  const file = e.target.files[0];
  if (file) {
    currentData = await readFile(file);
  }
});
dropzone.addEventListener('dragover', e => {
  e.preventDefault();
});
dropzone.addEventListener('drop', async e => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) {
    currentData = await readFile(file);
  }
});
runBtn.addEventListener('click', runAlgorithm);
benchBtn.addEventListener('click', runBenchmark);
exportBtn.addEventListener('click', exportCSV);
searchBtn.addEventListener('click', search);
toggleTheme.addEventListener('click', () => {
  document.body.classList.toggle('dark');
});

initAlgorithms();
initLogs();
