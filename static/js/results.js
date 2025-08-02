document.addEventListener("DOMContentLoaded", () => {
    console.log("Results page fully loaded and parsed.");
});

function downloadReport() {
    // Download as JSON report using the backend endpoint
    window.location.href = '/export/json';
}

function shareResults() {
    // Share via Web Share API if supported
    if (navigator.share) {
        navigator.share({
            title: 'WhatsInsight - Chat Analysis Results',
            text: 'Check out the results of my WhatsInsight chat analysis!',
            url: window.location.href
        }).then(() => console.log('Successfully shared'))
          .catch(error => console.log('Error sharing:', error));
    } else {
        // Fallback: Copy URL to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Results URL copied to clipboard!');
        }).catch(() => {
            alert('Unable to share. Please copy this URL manually: ' + window.location.href);
        });
    }
}

function exportData() {
    // Export data as CSV using the backend endpoint
    window.location.href = '/export/csv';
}
