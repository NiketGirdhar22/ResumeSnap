document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const uploadedFile = document.getElementById('uploaded-file');
    const processingOverlay = document.getElementById('processing-overlay');
    const summaryContainer = document.getElementById('summary-container');
    const summaryContent = document.getElementById('summary-content');
    const progressValue = document.getElementById('progress-value');
    const circularProgress = document.getElementById('circular-progress');
    const jobRoleInput = document.getElementById('job-role');
    const reviewButton = document.getElementById('review-button');
    const reviewContainer = document.getElementById('review-container');
    const reviewForm = document.getElementById('review-form');
    const reviewText = document.getElementById('review-text');
    const reviewerName = document.getElementById('reviewer-name');
    const reviewerEmail = document.getElementById('reviewer-email');

    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file) {
            uploadedFile.textContent = `Selected file: ${file.name}`;
            uploadButton.disabled = false;
        } else {
            uploadedFile.textContent = '';
            uploadButton.disabled = true;
        }
    });

    document.getElementById('upload-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const file = fileInput.files[0];
        const jobRole = jobRoleInput.value.trim();

        if (file && jobRole) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('jobRole', jobRole);

            processingOverlay.classList.add('visible');
            summaryContainer.style.display = 'none';

            fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                processingOverlay.classList.remove('visible');
                if (data.summary) {
                    summaryContent.textContent = data.summary;
                    summaryContainer.style.display = 'block';
                    reviewButton.style.display = 'block';
                    updateProgressBar(data.readability_rating);
                } else {
                    alert('Failed to generate summary. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                processingOverlay.classList.remove('visible');
                alert('An error occurred while processing the file.');
            });
        } else {
            alert('Please select a file and enter a job role.');
        }
    });

    reviewButton.addEventListener('click', function() {
        reviewContainer.style.display = 'block';
        reviewButton.style.display = 'none';
    });

    reviewForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const review = reviewText.value.trim();
        const name = reviewerName.value.trim();
        const email = reviewerEmail.value.trim();
        
        if (review && name && email) {
            fetch('http://localhost:5000/review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ review, name, email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Review submitted successfully!');
                    reviewContainer.style.display = 'none';
                } else {
                    alert('Failed to submit review. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the review.');
            });
        } else {
            alert('Please fill out all fields.');
        }
    });

    function updateProgressBar(score) {
        const percentage = (score / 10) * 100;
        circularProgress.style.background = `conic-gradient(#4CAF50 ${percentage * 3.6}deg, #757575 ${percentage * 3.6}deg)`;
        progressValue.textContent = score;
    }
});