document.getElementById('generateBtn').addEventListener('click', async () => {
    const length = document.getElementById('length').value;
    const useDigits = document.getElementById('useDigits').checked;
    const useSpecial = document.getElementById('useSpecial').checked;

    const statusDiv = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    statusDiv.style.display = 'block';
    statusDiv.textContent = '';
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length, use_digits: useDigits, use_special: useSpecial })
        });
        const { task_id } = await response.json();

        const poll = setInterval(async () => {
            const statusResp = await fetch(`/api/status/${task_id}`);
            const data = await statusResp.json();

            if (data.state === 'SUCCESS') {
                clearInterval(poll);
                statusDiv.style.display = 'none';
                resultDiv.style.display = 'block';
                document.getElementById('passwordValue').textContent = data.result;
            } else if (data.state === 'FAILURE') {
                clearInterval(poll);
                statusDiv.style.display = 'none';
                errorDiv.style.display = 'block';
                errorDiv.textContent = `Ошибка: ${data.status}`;
            } else {
                statusDiv.textContent = `Статус: ${data.status || data.state}`;
            }
        }, 1000);
    } catch (err) {
        statusDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Ошибка соединения с сервером';
    }
});