document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");

  // ✅ Universal: Theme toggle logic
  if (themeToggle) {
    const darkMode = localStorage.getItem("dark-mode");
    if (darkMode === "true") {
      document.body.classList.add("dark-mode");
      themeToggle.checked = true;
    }

    themeToggle.addEventListener("change", () => {
      document.body.classList.toggle("dark-mode");
      localStorage.setItem("dark-mode", document.body.classList.contains("dark-mode"));
    });
  }

  // ✅ Page-specific: Form-based File Upload (index.html)
  const uploadForm = document.getElementById("upload-form");
  const preambleInput = document.getElementById("preamble-file");
  const judgmentInput = document.getElementById("judgment-file");
  const fileList = document.getElementById("file-list");
  const uploadStatus = document.getElementById("upload-status");

  if (uploadForm && preambleInput && judgmentInput) {
    uploadForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const preambleFile = preambleInput.files[0];
      const judgmentFile = judgmentInput.files[0];

      if (!preambleFile || !judgmentFile) {
        uploadStatus.textContent = "Please upload both preamble and judgment files.";
        uploadStatus.style.color = "red";
        return;
      }

      const formData = new FormData();
      formData.append("preamble_file", preambleFile);
      formData.append("judgment_file", judgmentFile);

      fileList.innerHTML = "";
      [preambleFile, judgmentFile].forEach((file) => {
        const li = document.createElement("li");
        li.textContent = file.name;
        fileList.appendChild(li);
      });

      uploadStatus.textContent = "Uploading...";
      uploadStatus.style.color = "blue";

      fetch("/upload", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          uploadStatus.textContent = data.message || "Files uploaded successfully!";
          uploadStatus.style.color = "green";
        })
        .catch((err) => {
          uploadStatus.textContent = "Upload failed: " + err.message;
          uploadStatus.style.color = "red";
        });
    });
  }

  // ✅ Page-specific: Drag-and-drop upload (if used on any page)
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("file-input");

  if (dropArea && fileInput && fileList) {
    dropArea.addEventListener("click", () => fileInput.click());

    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.style.background = "rgba(0, 123, 255, 0.2)";
    });

    dropArea.addEventListener("dragleave", () => {
      dropArea.style.background = "";
    });

    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.style.background = "";
      handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener("change", (e) => {
      handleFiles(e.target.files);
    });

    function handleFiles(files) {
      fileList.innerHTML = "";
      const formData = new FormData();

      Array.from(files).forEach((file) => {
        const li = document.createElement("li");
        li.textContent = file.name;
        fileList.appendChild(li);
        formData.append("files", file);
      });

      fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("Uploaded:", data.filenames);
        })
        .catch((err) => console.error("Upload failed", err));
    }
  }

  // ✅ Page-specific: Similar case finder (similar.html)
  const outputText = document.getElementById("output-text");
  const userInput = document.getElementById("user-input");
  const submitBtn = document.querySelector("button[onclick='generateOutput()']");

  if (outputText && userInput && submitBtn) {
    window.generateOutput = () => {
      const query = userInput.value.trim();
      if (!query) {
        outputText.textContent = "Please enter a query.";
        return;
      }

      outputText.textContent = "Generating response...";

      fetch("/generate_case", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.output) {
            outputText.textContent = data.output;
          } else {
            outputText.textContent = "No output received.";
          }
        })
        .catch((err) => {
          outputText.textContent = "Error: " + err.message;
        });
    };
  }
});

