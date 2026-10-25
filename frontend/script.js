

const API = ""; // Same origin as FastAPI

const csvInput = document.getElementById("csvFile");
const recipientInput = document.getElementById("recipients");
const countLabel = document.getElementById("recipientCount");
const generateBtn = document.getElementById("generateBtn");
const message = document.getElementById("message");
const downloadZipBtn = document.getElementById("downloadZipBtn");

let csvRecipients = null;

function parseCSV(text) {
    const rows = [];
    let row = [];
    let field = "";
    let quoted = false;

    text = text.replace(/^\uFEFF/, "");

    for (let i = 0; i < text.length; i++) {
        const ch = text[i];

        if (ch === '"') {
            if (quoted && text[i + 1] === '"') {
                field += '"';
                i++;
            } else {
                quoted = !quoted;
            }
        } else if (ch === "," && !quoted) {
            row.push(field.trim());
            field = "";
        } else if ((ch === "\n" || ch === "\r") && !quoted) {
            if (ch === "\r" && text[i + 1] === "\n") {
                i++;
            }

            row.push(field.trim());

            if (row.some(value => value !== "")) {
                rows.push(row);
            }

            row = [];
            field = "";
        } else {
            field += ch;
        }
    }

    row.push(field.trim());

    if (row.some(value => value !== "")) {
        rows.push(row);
    }

    if (quoted) {
        throw new Error("CSV contains an unclosed quotation mark.");
    }

    if (rows.length < 2) {
        throw new Error(
            "CSV must contain a header and at least one recipient."
        );
    }

    const headers = rows[0].map(value => value.toLowerCase());
    const nameIndex = headers.indexOf("name");
    const emailIndex = headers.indexOf("email");

    if (nameIndex === -1 || emailIndex === -1) {
        throw new Error(
            "CSV must have columns named name and email."
        );
    }

    return rows.slice(1).map(row => ({
        name: row[nameIndex] || "",
        email: row[emailIndex] || ""
    }));
}

function parseManualInput() {
    const text = recipientInput.value.trim();

    if (!text) {
        return [];
    }

    return text.split(/\r?\n/).map(line => {
        const comma = line.indexOf(",");

        if (comma === -1) {
            return {
                name: line.trim(),
                email: ""
            };
        }

        return {
            name: line.slice(0, comma).trim(),
            email: line.slice(comma + 1).trim()
        };
    });
}

function updateCount() {
    try {
        const recipients = csvRecipients ?? parseManualInput();
        countLabel.textContent = recipients.length;
    } catch {
        countLabel.textContent = "—";
    }
}

function validateRecipients(recipients) {
    if (recipients.length === 0) {
        throw new Error(
            "Upload a CSV or enter at least one recipient."
        );
    }

    if (recipients.some(r => !r.name || !r.email)) {
        throw new Error(
            "Every recipient must have a name and email."
        );
    }

    const invalidEmail = recipients.find(
        r => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(r.email)
    );

    if (invalidEmail) {
        throw new Error(
            `Invalid email address: ${invalidEmail.email}`
        );
    }
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    if (!response.ok) {
        const detail = await response.text();
        throw new Error(`API error ${response.status}: ${detail}`);
    }

    return response.json();
}

// Handle CSV upload
csvInput.addEventListener("change", async () => {
    const file = csvInput.files[0];

    if (!file) {
        return;
    }

    try {
        csvRecipients = parseCSV(await file.text());
        recipientInput.value = "";

        document.getElementById("fileName").textContent =
            `${file.name} · ${csvRecipients.length} recipients`;

        updateCount();

        message.textContent =
            "CSV loaded. Review the recipient count before generating.";
    } catch (error) {
        csvRecipients = null;

        document.getElementById("fileName").textContent =
            "Invalid CSV file";

        message.textContent = error.message;
        updateCount();
    }
});

// Handle manual recipient input
recipientInput.addEventListener("input", () => {
    csvRecipients = null;
    csvInput.value = "";

    document.getElementById("fileName").textContent =
        "No file selected";

    updateCount();
});

// Generate certificates
generateBtn.addEventListener("click", async () => {
    let recipients;

    try {
        recipients = csvRecipients ?? parseManualInput();
        validateRecipients(recipients);
    } catch (error) {
        message.textContent = error.message;
        return;
    }

    generateBtn.disabled = true;
    downloadZipBtn.hidden = true;
    downloadZipBtn.removeAttribute("href");

    document.getElementById("results").classList.add("hidden");

    message.textContent =
        `Creating a job for ${recipients.length} recipients...`;

    try {
        // Step 1: Create a job
        const job = await apiRequest("/api/jobs/", {
            method: "POST",
            body: JSON.stringify({ recipients })
        });

        message.textContent =
            `Job #${job.job_id} created. Generating certificates; please wait...`;

        // Step 2: Generate certificates
        const result = await apiRequest(
            `/api/jobs/${job.job_id}/generate`,
            { method: "POST" }
        );

        const total = result.total_recipients ?? recipients.length;
        const successful = result.successful_count ?? 0;
        const failed = result.failed_count ?? 0;

        document.getElementById("jobInfo").textContent =
            `Job #${job.job_id} · Status: ${result.status}`;

        document.getElementById("totalCount").textContent = total;
        document.getElementById("successCount").textContent = successful;
        document.getElementById("failedCount").textContent = failed;

        // Step 3: Configure ZIP download for this job
        if (successful > 0) {
            downloadZipBtn.href =
                `/api/jobs/${job.job_id}/download-zip`;

            downloadZipBtn.hidden = false;
        }

        // Step 4: Retrieve certificate records
        const listData = await apiRequest(
            `/api/jobs/${job.job_id}/certificates`
        );

        const certificates = listData.certificates ?? [];
        const list = document.getElementById("certificateList");

        list.replaceChildren();

        certificates.forEach(cert => {
            const item = document.createElement("div");
            item.className = "certificate";

            const details = document.createElement("div");

            const name = document.createElement("strong");
            name.textContent = cert.recipient_name;

            const email = document.createElement("small");
            email.textContent =
                `${cert.recipient_email} · ${cert.status}`;

            details.append(name, email);
            item.append(details);

            if (String(cert.status).toLowerCase() === "success") {
                const link = document.createElement("a");

                link.className = "download";
                link.href =
                    `/api/jobs/certificates/${cert.certificate_id}/download`;

                link.textContent = "Download PDF";

                link.setAttribute(
                    "aria-label",
                    `Download certificate for ${cert.recipient_name}`
                );

                item.append(link);
            }

            list.append(item);
        });

        // Step 5: Show results
        document.getElementById("results").classList.remove("hidden");

        message.textContent =
            `Finished. ${successful} successful, ${failed} failed.`;

        document.getElementById("results").scrollIntoView({
            behavior: "smooth"
        });
    } catch (error) {
        message.textContent =
            `Generation could not be completed: ${error.message}`;
    } finally {
        generateBtn.disabled = false;
    }
});

updateCount();
