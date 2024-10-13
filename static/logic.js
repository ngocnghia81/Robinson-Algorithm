function prove() {
    const hypotheses = document.getElementById('hypotheses').value.split(',').map(h => h.trim());
    const conclusion = document.getElementById('conclusion').value.split(',').map(c => c.trim());

    fetch('/prove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hypotheses: hypotheses, conclusion: conclusion })
    })
    .then(response => response.json())
    .then(data => {
        displayResult(data.steps);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displayResult(steps) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ''; // Clear previous results

    steps.forEach(step => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step';
        stepDiv.innerHTML = `<strong>${step.title}:</strong><br>${step.content}`;
        resultDiv.appendChild(stepDiv);
    });
}
