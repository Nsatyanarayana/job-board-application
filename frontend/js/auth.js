document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;
    // const API_BASE_URL = window__env.API_BASE_URL;

    try {
        const response = await fetch(`http://127.0.0.1:8600/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password, role }),
        });

        const result = await response.json();  
        console.log(result);
        
        if (response.ok) {
            alert("Register successfully!!!");
            window.location.href = "/login";  
        } else {
            alert(result.detail || "Registration failed!");  
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    }
});

document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    // const API_BASE_URL = window__env.API_BASE_URL;

    try {
        const response = await fetch(`http://127.0.0.1:8600/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const result = await response.json(); 
        console.log(result);

        if (response.ok) {
            
            sessionStorage.setItem("user_id", result.user_id);
            sessionStorage.setItem("email", result.email);
            sessionStorage.setItem("role", result.role);

            
            const role = result.role.toLowerCase();
            if (role === "employer") {
                window.location.href = "/employer/dashboard";
            } else if (role === "job_seeker") {
                window.location.href = "/job-seeker/dashboard";
            } else if (role === "admin") {  
                window.location.href = "/admin"; 
            } else {
                alert("Invalid role");
            }
        } else {
            alert(result.detail || "Login failed!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    }
});
