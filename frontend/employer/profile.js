document.addEventListener("DOMContentLoaded", async () => {
    const userId = sessionStorage.getItem("user_id");
    const editBtn = document.getElementById("editProfileBtn");
    const saveBtn = document.getElementById("saveProfileBtn");
    const inputs = ["username", "email", "companyName", "position", "location"].map(id => document.getElementById(id));

    if (!userId) {
        console.warn("No user ID found in session storage.");
        document.getElementById("profileMessage").textContent = "User ID is missing!";
        document.getElementById("profileMessage").className = "text-danger";
        return; 
    }

    const fetchAndRenderProfile = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/employer/get_profile/${userId}`);
            if (!response.ok) throw new Error("Profile not found");
            const data = await response.json();

            document.getElementById("username").value = data.username || "";
            document.getElementById("email").value = data.email || "";
            document.getElementById("companyName").value = data.company_name || "";
            document.getElementById("position").value = data.position || "";
            document.getElementById("location").value = data.location || "";
        } catch (error) {
            console.warn("Error fetching profile:", error);
            document.getElementById("profileMessage").textContent = "Failed to load profile!";
            document.getElementById("profileMessage").className = "text-danger";
        }
    };

    await fetchAndRenderProfile();

   
    editBtn.addEventListener("click", () => {
        inputs.forEach(input => input.disabled = false);
        editBtn.style.display = "none";
        saveBtn.style.display = "block";
    });

    document.getElementById("employerProfileForm").addEventListener("submit", async (e) => {
        e.preventDefault();

        const profile = {
            user_id: userId,
            company_name: document.getElementById("companyName").value,
            position: document.getElementById("position").value,
            location: document.getElementById("location").value,
        };

        try {
            const response = await fetch(`${API_BASE_URL}/employer/update_profile`, {  
                method: "PUT",  
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(profile),
            });
            
            

            if (response.ok) {
                document.getElementById("profileMessage").textContent = "Profile updated successfully!";
                document.getElementById("profileMessage").className = "text-success";

                inputs.forEach(input => input.disabled = true);
                saveBtn.style.display = "none";
                editBtn.style.display = "block";

                await fetchAndRenderProfile();
            } else {
                throw new Error("Failed to update profile");
            }
        } catch (error) {
            document.getElementById("profileMessage").textContent = error.message;
            document.getElementById("profileMessage").className = "text-danger";
        }
    });
});