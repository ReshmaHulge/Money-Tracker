
// Delete confirmation
function confirmDelete() {
    return confirm("Are you sure you want to delete this expense?");
}

// Amount Validation
function validateForm() {
    let amount = document.getElementById("amount").value;

    if (amount === "" || amount <= 0) {
        alert("Please enter a valid amount.");
        return false;
    }

    return true;
}

// Set Today's Date Automatically
window.addEventListener("load", function () {
    let dateInput = document.getElementById("date");

    if (dateInput && dateInput.value === "") {
        let today = new Date();

        let yyyy = today.getFullYear();
        let mm = String(today.getMonth() + 1).padStart(2, "0");
        let dd = String(today.getDate()).padStart(2, "0");

        dateInput.value = `${yyyy}-${mm}-${dd}`;
    }
});

// Dark / Light Mode
document.addEventListener("DOMContentLoaded", function () {

    const toggleButton = document.getElementById("themeToggle");

    const savedTheme = localStorage.getItem("expenseTheme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
    }

    function updateButton() {
        if (!toggleButton) return;

        const isDark = document.body.classList.contains("dark-mode");

        toggleButton.innerHTML = isDark
            ? '<i class="fa-solid fa-sun"></i><span>Light Mode</span>'
            : '<i class="fa-solid fa-moon"></i><span>Dark Mode</span>';
    }

    updateButton();

    if (toggleButton) {
        toggleButton.addEventListener("click", function () {

            document.body.classList.toggle("dark-mode");

            const isDark = document.body.classList.contains("dark-mode");

            localStorage.setItem(
                "expenseTheme",
                isDark ? "dark" : "light"
            );

            updateButton();
        });
    }
});
