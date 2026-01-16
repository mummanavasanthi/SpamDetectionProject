function toggleInputs() {
  const type = document.getElementById("inputType").value;

  const smsBox = document.getElementById("smsBox");
  const emailBox = document.getElementById("emailBox");

  if (type === "sms") {
    smsBox.classList.remove("hidden");
    emailBox.classList.add("hidden");
  } else {
    smsBox.classList.add("hidden");
    emailBox.classList.remove("hidden");
  }
}

async function predictSpam() {
  const type = document.getElementById("inputType").value;

  const loading = document.getElementById("loading");
  const resultBox = document.getElementById("resultBox");

  let text = "";

  if (type === "sms") {
    text = document.getElementById("smsMessage").value.trim();
  } else {
    const subject = document.getElementById("emailSubject").value.trim();
    const body = document.getElementById("emailBody").value.trim();
    text = `Subject: ${subject}\n\n${body}`.trim();
  }

  if (!text || text === "Subject:") {
    alert("Please enter some text!");
    return;
  }

  loading.classList.remove("hidden");
  resultBox.classList.add("hidden");

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_type: type, text: text })
    });

    // ✅ if server error
    if (!res.ok) {
      loading.classList.add("hidden");
      alert("Server error! Check terminal output.");
      return;
    }

    const data = await res.json();

    loading.classList.add("hidden");
    resultBox.classList.remove("hidden");

    if (data.error) {
      document.getElementById("resultTitle").innerText = "❌ Error";
      document.getElementById("resultType").innerText = data.error;
      document.getElementById("spamProb").innerText = "--";
      document.getElementById("modelAcc").innerText = "--";
      return;
    }

    document.getElementById("resultTitle").innerText =
      data.prediction === "SPAM" ? "🚨 SPAM Detected" : "✅ NOT SPAM";

    document.getElementById("resultType").innerText = "Type: " + data.type;
    document.getElementById("spamProb").innerText = data.probability + "%";
    document.getElementById("modelAcc").innerText = data.accuracy + "%";

  } catch (err) {
    loading.classList.add("hidden");
    alert("Fetch failed! Check terminal + console.");
    console.log(err);
  }
}

toggleInputs();
