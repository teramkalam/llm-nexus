async function showString() {
  const input = document.getElementById('userInput').value;
  const checkboxes = document.querySelectorAll('.llm-options input[type="checkbox"]:checked');
  const selectedModels = Array.from(checkboxes).map(cb => cb.value);

  if (!input || selectedModels.length === 0) {
    alert("Please enter a prompt and select at least one model.");
    return;
  }

  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = 'Processing...';

  try
  {
    const response = await fetch("http://127.0.0.1:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: input, models: selectedModels })
    });

    const data = await response.json();
    resultDiv.innerHTML = "";

    if (data.groups)
    {
      for(const groupId in data.groups)
      {
        resultDiv.innerHTML += `<h3>Group ${groupId}</h3>`;
        data.groups[groupId].forEach(item => {
          resultDiv.innerHTML += `<h4>${item.model}:</h4><p>${item.answer}</p>`;
        });
        resultDiv.innerHTML += "<hr>";
      }
    }
    else
    {
      resultDiv.innerHTML = "❌ No groups found";
    }
  }
  catch(err)
  {
    resultDiv.textContent = "❌ Error: " + err.message;
  }
}
