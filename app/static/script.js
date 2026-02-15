function showLoader(id) {
    document.getElementById(id).classList.remove("hidden");
}

function hideLoader(id) {
    document.getElementById(id).classList.add("hidden");
}

async function loadDocuments() {
    const res = await fetch('/documents');
    const data = await res.json();

    const list = document.getElementById('docList');
    list.innerHTML = '';

    data.documents.forEach(doc => {
        const li = document.createElement('li');
        li.textContent = doc;
        list.appendChild(li);
    });
}

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const files = document.getElementById('files').files;
    if (files.length === 0) {
        alert("Please select at least one .txt file.");
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const files = document.getElementById('files').files;
    const messageBox = document.getElementById('uploadMessage');

    if (files.length === 0) {
        alert("Please select at least one .txt file.");
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    // Reset UI state
    messageBox.classList.add("hidden");
    messageBox.innerText = "";
    showLoader("uploadLoader");

    try {
        const res = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        hideLoader("uploadLoader");

        if (res.ok) {
            messageBox.classList.remove("hidden");
            messageBox.innerText =
                `Added: ${data.added?.join(", ") || "None"} | skipped: ${data.skipped?.join(", ") || "None"}`;
        } else {
            messageBox.classList.remove("hidden");
            messageBox.innerText = "Upload failed.";
        }

        loadDocuments();

    } catch (err) {
        hideLoader("uploadLoader");
        messageBox.classList.remove("hidden");
        messageBox.innerText = "Unexpected error occurred.";
    }
});

});

async function askQuestion() {
    const question = document.getElementById('question').value;

    if (!question.trim()) {
        alert("Question cannot be empty.");
        return;
    }

    showLoader("queryLoader");

    const res = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });

    const data = await res.json();

    hideLoader("queryLoader");

    document.getElementById("answerBox").classList.remove("hidden");
    document.getElementById("sourcesBox").classList.remove("hidden");

    document.getElementById('answerText').innerText = data.answer;

    const sourcesDiv = document.getElementById('sources');
    sourcesDiv.innerHTML = '';

    if (data.sources) {
        data.sources.forEach(src => {
            const div = document.createElement('div');
            div.classList.add("source-item");
            div.innerHTML = `
                <strong>${src.document}</strong>
                <div>${src.snippet}</div>
            `;
            div.style.marginBottom = "12px";
            sourcesDiv.appendChild(div);
        });
    }
}

async function checkStatus() {
    const res = await fetch('/status');
    const data = await res.json();

    document.getElementById('statusBox').innerText =
        JSON.stringify(data, null, 2);

    const indicator = document.getElementById('statusIndicator');
    if (data.llm_connection === "ok") {
        indicator.style.background = "#16a34a";
        indicator.innerText = "Healthy";
    } else {
        indicator.style.background = "#dc2626";
        indicator.innerText = "Issue";
    }
}

checkStatus();
loadDocuments();
