document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                document.getElementById('prediction-result').innerHTML = 
                    `<p>Rendimiento Predicho: ${result.rendimiento_predicho}</p>`;
            } else {
                document.getElementById('prediction-result').innerHTML = 
                    `<p>Error: ${result.error}</p>`;
            }
        } catch (error) {
            document.getElementById('prediction-result').innerHTML = 
                `<p>Error: ${error.message}</p>`;
        }
    });
});
