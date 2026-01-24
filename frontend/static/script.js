const searchInput = document.getElementById('searchInput');
const resultsBox = document.getElementById('searchResults');
let perfChart = null; 
let currentCompanyData = null;

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

// Pressing on 'Enter' button
// Add Enter key support for the chat input
document.getElementById('chatInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendUserMessage();
    }
});

function loadCompanyData(exactName) {
    fetch(`/api/get_company?name=${encodeURIComponent(exactName)}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) { alert(data.error); return; }
            currentCompanyData = data;
            updateDashboard(data);
        });
}

function updateDashboard(data) {
    // HEADER
    document.getElementById('companyName').textContent = data.name;
    document.getElementById('badgeLoc').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${data.city}, ${data.country}`;
    
    const clusters = { 0: "General B2B Services", 1: "Infrastructure & Communications", 2: "High-Efficiency Consultancies", 3: "High-Operation Service Firms", 4: "Industrial & Heavy Construction",  "micro": "Micro & Low-Activity"};
    const cName = `Cluster ${data.cluster_id}: ${clusters[data.cluster_id] || ""}`;
    document.getElementById('badgeCluster').innerHTML = `<i class="fa-solid fa-diagram-project"></i> ${cName}`;
    const yearText =
        data.age &&
            data.age !== "Unreported" &&
            data.age !== "nan" &&
            data.age !== "NaN"
            ? `<i class="fa-solid fa-calendar"></i> Founded in ${data.age}`
            : `<i class="fa-solid fa-calendar"></i> Founding Year Unreported`;
    document.getElementById("badgeYearFounded").innerHTML = yearText;

    // WEBSITE
    const websiteBadge =
        data.website &&
            data.website !== "Website Unavailable"
            ? `<i class="fa-solid fa-globe"></i>
           <a href="${data.website.startsWith("http") ? data.website : "https://" + data.website}"
              target="_blank"
              rel="noopener noreferrer"
              class="badge-link">
              ${data.website}
           </a>`
            : `<i class="fa-solid fa-globe"></i> Website Unavailable`;

    document.getElementById("badgeWebsite").innerHTML = websiteBadge;

    // COMPANY DESCRIPTION
    const desc =
        data.comp_desc &&
            data.comp_desc !== "nan" &&
            data.comp_desc !== "NaN"
            ? data.comp_desc
            : "No description available for this company.";
    document.getElementById("kpiDescription").innerText = desc;

    // KPIs
    const fmtMoney = n => !n ? "$0" : n < 1_000_000 ? `$${Math.floor(n / 1_000)}K` : `$${(n / 1_000_000).toFixed(2)}M`;
    document.getElementById('kpiRevenue').textContent = fmtMoney(data.revenue);
    document.getElementById('kpiEmployees').textContent = 
        typeof data.employees === 'number' ? data.employees.toLocaleString() : data.employees;
    document.getElementById('kpiIT').textContent = fmtMoney(data.it_spend);
    document.getElementById('kpiSIC').textContent = data.sic;

    // NEIGHBORS TABLE
    const tbody = document.getElementById('neighborTable');
    tbody.innerHTML = '';
    data.neighbors.forEach(n => {
        tbody.innerHTML += `<tr><td>${n.name}</td><td>${fmtMoney(n.revenue)}</td></tr>`;
    });

    // UPDATE CHART
    updateChart(data);

    // AI CHAT UPDATE
    const chat = document.getElementById('chatContainer');
    chat.innerHTML += `
        <div class="message bot">
            <strong>Loaded: ${data.name}</strong><br>
            This is a company in the <strong>${cName}</strong> cluster.<br>
            Compared to peers, their IT spend is <strong>${data.it_spend > data.cluster_avg_it ? "Higher" : "Lower"}</strong> than average.
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

function toggleChat(){
  document.querySelector('.chat-panel').classList.toggle('active');
}

function displayMessage(sender, message) {
    const chatContainer = document.getElementById('chatContainer');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender.toLowerCase()}`;
    msgDiv.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendUserMessage() {
    const chatInputElement = document.getElementById("chatInput");
    const userMessage = chatInputElement.value.trim();
    
    if (!userMessage || !currentCompanyData) return;

    displayMessage("You", userMessage); 
    chatInputElement.value = "";

    // Creating the 'Loading' placeholder for the AI
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = `message ai`;
    loadingDiv.innerHTML = `<p><strong>AI:</strong> <span class="loading-text">Thinking...</span></p>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: userMessage,
                context: currentCompanyData 
            })
        });

        const data = await response.json();
        displayMessage("AI", data.response);
    } catch (error) {
        displayMessage("AI", "Sorry, I'm having trouble connecting to the brain.");
    }
}

function sendQuickPrompt(text) {
    const chatInput = document.getElementById("chatInput");
    chatInput.value = text;
    chatInput.focus();

    // Trigger the existing send function
    // sendUserMessage();
}