const algorithmSelect = document.getElementById('algorithm');
const datasetInput = document.getElementById('dataset');
const runBtn = document.getElementById('run');
const exportBtn = document.getElementById('export');
const viz = d3.select('#visualization');
const resultsDiv = document.getElementById('results');
let currentData = null;
let lastResult = null;

async function loadAlgorithms() {
  const res = await fetch('http://localhost:8000/api/algorithms');
  if (!res.ok) return;
  const data = await res.json();
  algorithmSelect.innerHTML = '';
  data.algorithms.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    algorithmSelect.appendChild(opt);
  });
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(JSON.parse(reader.result));
    reader.onerror = reject;
    reader.readAsText(file);
  });
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

datasetInput.addEventListener('change', async e => {
  const file = e.target.files[0];
  if (file) {
    currentData = await readFile(file);
  }
});
runBtn.addEventListener('click', runAlgorithm);
exportBtn.addEventListener('click', exportCSV);
loadAlgorithms();
