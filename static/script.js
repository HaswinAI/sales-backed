document.getElementById("chat-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    
    const message = document.getElementById("chat-input").value;
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
    });

    const data = await response.json();
    if (data.response) {
        const chatOutput = document.getElementById("chat-output");
        chatOutput.innerHTML = `<p>Assistant: ${data.response}</p>`;
    } else {
        alert("Error communicating with the chatbot.");
    }
});
