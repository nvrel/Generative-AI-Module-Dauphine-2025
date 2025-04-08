document.addEventListener('DOMContentLoaded', function() {
    const tweetForm = document.getElementById('tweetForm');
    const resultDiv = document.getElementById('result');
    const generatedTweet = document.getElementById('generatedTweet');
    const copyButton = document.getElementById('copyButton');
    const submitButton = tweetForm.querySelector('button[type="submit"]');

    // Handle form submission
    tweetForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form values
        const prompt = document.getElementById('prompt').value.trim();
        const company = document.getElementById('company').value;
        
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="loading"></span>Generating...';
        
        try {
            // Make API call to the backend
            const response = await fetch('/api/generate_tweet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt, company }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            generatedTweet.textContent = data.tweet;
            
            // Show the result
            resultDiv.classList.remove('d-none');
            
            // Scroll to result
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            alert('An error occurred while generating the tweet. Please try again.');
            console.error('Error:', error);
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Tweet';
        }
    });

    // Handle copy to clipboard
    copyButton.addEventListener('click', function() {
        const tweetText = generatedTweet.textContent;
        navigator.clipboard.writeText(tweetText).then(function() {
            // Show success feedback
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
            copyButton.classList.add('btn-success');
            copyButton.classList.remove('btn-outline-primary');
            
            // Reset button after 2 seconds
            setTimeout(() => {
                copyButton.innerHTML = originalText;
                copyButton.classList.remove('btn-success');
                copyButton.classList.add('btn-outline-primary');
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text to clipboard');
        });
    });
}); 