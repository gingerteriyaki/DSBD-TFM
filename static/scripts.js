document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const resultDiv = document.getElementById('prediction-result');
        if (result.error) {
            resultDiv.textContent = 'Error: ' + result.error;
        } else {
            resultDiv.textContent = 'Rendimiento Predicho: ' + result.rendimiento_predicho;
        }
    })
    .catch(error => {
        document.getElementById('prediction-result').textContent = 'Error: ' + error;
    });
});
