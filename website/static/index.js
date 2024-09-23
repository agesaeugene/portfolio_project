
    // Add a listener for the form submission
    document.getElementById('date-form').addEventListener('submit', function(event) {
        var dateInput = document.getElementById('date-input').value;
        
        // If no date is selected, show an alert and prevent form submission
        if (!dateInput) {
            event.preventDefault();  // Stop form submission
            alert('Please select a date before adding!');
        }
    });
    
    const button = document.querySelector(".button");
    
    button.addEventListener("click", () => {
        button.classList.add("active");
        setTimeout(() => {
            button.classList.remove("active");
            button
            .querySelector("i")
            .classList.replace("bx-cloud-download", "bx-check-circle");
            button.querySelector("span").innerText = "Completed";
            
            setTimeout(() => {
                button
                .querySelector("i")
                .classList.replace("bx-check-circle", "bx-cloud-download");
                button.querySelector("span").innerText = "Download Again";
            }, 3000);
        }, 6000);
    });

