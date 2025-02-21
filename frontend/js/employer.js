document.getElementById("post-job-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const skills = document.getElementById("skills").value.split(", ");
    const salary = document.getElementById("salary").value;
    const location = document.getElementById("location").value;
    const user_id = sessionStorage.getItem("user_id");
    if(!user_id){
        alert("user_id misssing. please login again");
        return;
    }

    const token = localStorage.getItem("access_token");
    const API_BASE_URL = "http://127.0.0.1:8600"; 

    const response = await fetch(`${API_BASE_URL}/employer/post_job?user_id=${user_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer   ${token}`,
        },
        body: JSON.stringify({ title, description, skills, salary, location }),
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        window.location.href = "dashboard.html";
    } else {
        alert(result.detail);
    }
});
function renderJobs(jobs) {
    jobListingsContainer.innerHTML = ""; 
    jobs.forEach((job) => {
        const jobCard = `
            <div class="col-md-4">
                <div class="card mb-4 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${job.title}</h5>
                        <p class="card-text">${job.description}</p>
                        <p><strong>Skills:</strong> ${job.skills.join(", ")}</p>
                        <p><strong>Salary:</strong> $${job.salary}</p>
                        <p><strong>Location:</strong> ${job.location}</p>
                    </div>
                </div>
            </div>
        `;
        jobListingsContainer.insertAdjacentHTML("beforeend", jobCard);
    });
}

fetchJobs();