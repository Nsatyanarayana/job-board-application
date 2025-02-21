const API_BASE_URL = "http://127.0.0.1:8600";
async function uploadResume(userId, file) {
    try {
        const formData = new FormData();
        formData.append("resume", file);
        const response = await fetch(`${API_BASE_URL}/upload_resume?user_id=${userId}`, {
            method: "POST",
            body: formData,
        });
        const result = await response.json();

        if (response.ok) {
            alert(result.message); 
        } else {v  
            alert(result.detail); 
        }
    } catch (error) {
        console.error("Error uploading resume:", error);
        alert("An error occurred while uploading the resume.");
    }
}

document.getElementById("upload-resume-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const userId = document.getElementById("user-id").value.trim();
    const fileInput = document.getElementById("resume-file");

    if (!userId || !fileInput.files.length) {
        alert("Please provide a valid user ID and select a file.");
        return;
    }

    const file = fileInput.files[0];
    await uploadResume(userId, file);
});



document.getElementById('searchForm').addEventListener('submit', async function (e) {
        e.preventDefault(); 
    
        const skill = document.getElementById('skill').value;
        const location = document.getElementById('location').value;
        const title = document.getElementById('title').value;

        const params = new URLSearchParams(); 
        if (skill) params.append('skill', skill);
        if (location) params.append('location', location);
        if (title) params.append('title', title);
    
        try {

            const response = await fetch(`/search_jobs?${params.toString()}`);
            if (!response.ok) {
                throw new Error('Failed to fetch jobs');
            }
    
            const data = await response.json();
            displayResults(data.jobs);
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
        }
    
    
    function displayResults(jobs) {
        const resultsDiv = document.getElementById('results');
    
        if (jobs.length === 0) {
            resultsDiv.innerHTML = '<p>No jobs found.</p>';
            return;
        }
    
        // Create HTML for each job
        const jobsHTML = jobs.map(job => `
            <div class="job">
                <h2>${job.title}</h2>
                <p><strong>Location:</strong> ${job.location}</p>
                <p><strong>Skills:</strong> ${job.skills.join(', ')}</p>
                <p><strong>Description:</strong> ${job.description}</p>
            </div>
        `).join('');
    
        resultsDiv.innerHTML = jobsHTML;
    }
});

async function applyForJob(jobId) {
    const token = localStorage.getItem("access_token");
    const API_BASE_URL = "http://127.0.0.1:8600";

    const response = await fetch(`${API_BASE_URL}/job_seeker/apply`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            
        },
        body: JSON.stringify({ job_id: jobId }),
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
    } else {
        alert(result.detail);
    }
}
async function renderJobDetails(jobId) {
    const jobDetails = await fetchJobDetails(jobId);
    if (!jobDetails) return;

    const jobDetailsContainer = document.getElementById("job-details");
    jobDetailsContainer.innerHTML = "";
    const jobHTML = `
        <div class="job-detail">
            <h2>${jobDetails.title}</h2>
            <p><strong>Location:</strong> ${jobDetails.location}</p>
            <p><strong>Skills:</strong> ${jobDetails.skills.join(", ")}</p>
            <p><strong>Description:</strong> ${jobDetails.description}</p>
            <button onclick="applyForJob(${jobDetails.id})">Apply Now</button>
        </div>
    `;
    jobDetailsContainer.innerHTML = jobHTML;
}
