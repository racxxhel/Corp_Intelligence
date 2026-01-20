const searchInput = document.getElementById('searchInput');
const resultsBox = document.getElementById('searchResults');
let perfChart = null; 

searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    if (query.length < 1) { resultsBox.style.display = 'none'; return; }

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(names => {
            resultsBox.innerHTML = '';
            if (names.length > 0) {
                resultsBox.style.display = 'block';
                names.forEach(name => {
                    const div = document.createElement('div');
                    div.className = 'search-item';
                    div.textContent = name;
                    div.onclick = () => {
                        searchInput.value = name;
                        resultsBox.style.display = 'none';
                        loadCompanyData(name);
                    };
                    resultsBox.appendChild(div);
                });
            } else { resultsBox.style.display = 'none'; }
        });
});

// Hide dropdown if clicked outside
document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
        resultsBox.style.display = 'none';
    }
});

function loadCompanyData(exactName) {
    fetch(`/api/get_company?name=${encodeURIComponent(exactName)}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) { alert(data.error); return; }
            updateDashboard(data);
        });
}

function updateDashboard(data) {
    // HEADER
    document.getElementById('companyName').textContent = data.name;
    document.getElementById('badgeLoc').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${data.city}, ${data.country}`;
    
    const clusters = { 0: "Emerging SME", 1: "High Growth", 2: "Mature Corp", 3: "Global Giant" };
    const cName = clusters[data.cluster_id] || `Cluster ${data.cluster_id}`;
    document.getElementById('badgeCluster').innerHTML = `<i class="fa-solid fa-diagram-project"></i> ${cName}`;

    // KPIs
    const fmtMoney = (n) => n ? "$" + (n / 1000000).toFixed(1) + "M" : "$0";
    document.getElementById('kpiRevenue').textContent = fmtMoney(data.revenue);
    document.getElementById('kpiEmployees').textContent = data.employees.toLocaleString();
    document.getElementById('kpiAge').textContent = data.age;
    document.getElementById('kpiIT').textContent = fmtMoney(data.it_spend);
    document.getElementById('kpiSIC').textContent = data.sic;

    // NEIGHBORS TABLE
    const tbody = document.getElementById('neighborTable');
    tbody.innerHTML = '';
    data.neighbors.forEach(n => {
        tbody.innerHTML += `<tr><td>${n['Company Sites']}</td><td>${fmtMoney(n['Revenue (USD)'])}</td></tr>`;
    });

    // UPDATE CHART
    updateChart(data);

    // AI CHAT UPDATE
    const chat = document.getElementById('chatContainer');
    chat.innerHTML += `
        <div class="message bot">
            <p><strong>Loaded: ${data.name}</strong></p>
            <p>This is a company in the <strong>${cName}</strong> cluster.</p>
            <p>Compared to peers, their IT spend is <strong>${data.it_spend > data.cluster_avg_it ? "Higher" : "Lower"}</strong> than average.</p>
        </div>`;
    chat.scrollTop = chat.scrollHeight;
}

function updateChart(data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    if (perfChart) perfChart.destroy();

    perfChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Revenue ($M)', 'IT Spend ($M x10)'],
            datasets: [
                {
                    label: 'Selected Company',
                    data: [data.revenue/1000000, (data.it_spend/1000000)*10],
                    backgroundColor: '#2563eb', borderRadius: 4
                },
                {
                    label: 'Cluster Average',
                    data: [data.cluster_avg_rev/1000000, (data.cluster_avg_it/1000000)*10],
                    backgroundColor: '#cbd5e1', borderRadius: 4
                }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
    });
}