    // Add a listener for the form submission
    document.getElementById('date-form').addEventListener('submit', function(event) {
        var dateInput = document.getElementById('date-input').value;
        
        // If no date is selected, show an alert and prevent form submission
        if (!dateInput) {
            event.preventDefault();  // Stop form submission
            alert('Please select a date before adding!');
        }
    });
