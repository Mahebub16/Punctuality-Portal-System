function validateEntry() {
    var studentIdInput = document.getElementById('student_id');
    var appMessage = document.getElementById('appMessage');

    // Get the entered student ID
    var enteredStudentId = studentIdInput.value;

    // Check if the entered student ID has entry_count 5 or more
    var latecomersData = JSON.parse('{{ latecomers | tojson | safe }}');
    
    for (var i = 0; i < latecomersData.length; i++) {
        var latecomerId = latecomersData[i][1];
        var entryCount = latecomersData[i][2];
        
        if (enteredStudentId === latecomerId && entryCount >= 2) {
            // Display the message for the specific ID
            appMessage.textContent = 'Warning: '+' Entry not allowed. ' +'"' + enteredStudentId +'"'+ ' is coming too late to College';
            appMessage.style.display = 'block';
            studentIdInput.focus();  // Set focus on the input
            return false;  // Prevent form submission
        }
    }

    // Hide the message if the entered ID does not meet the condition
    appMessage.style.display = 'none';
    
    // Allow form submission
    return true;
}

function downloadDatabase() {
var latecomersData = JSON.parse('{{ latecomers | tojson | safe }}');
if (latecomersData.length === 0) {
alert("No data available to download.");
return;
}

var csvContent = "sep=,\nStudent ID,No. of days,Year,Section\n";

// Add each entry to the CSV content
latecomersData.forEach(entry => {
// Assuming the structure is [Student ID, Year, Section, Entry Count, Entry Date, Entry Time]
var formattedEntry = entry.slice(1, 5).concat(entry.slice(6)); // Exclude ID and Date
csvContent += formattedEntry.join(',') + '\n';
});

// Create a Blob and generate a download link
var blob = new Blob([csvContent], { type: 'text/csv' });
var link = document.createElement('a');
link.href = window.URL.createObjectURL(blob);
link.download = 'latecomers_database.csv';

// Append the link to the document and trigger a click to start the download
document.body.appendChild(link);
link.click();

// Remove the link from the document
document.body.removeChild(link);
}



function clearDatabase() {
    if (confirm("Are you sure you want to clear the entire database?")) {
        // Send an AJAX request to the server to clear the database
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '{{ url_for("clear_database") }}', true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                // Refresh the page after clearing the database
                window.location.reload();
            }
        };
        xhr.send();
    }
}