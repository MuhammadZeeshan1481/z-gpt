import React, { useState } from "react";
import { generateImage } from "../api/image";

const ImageGenerator = () => {
  const [prompt, setPrompt] = useState("");
  const [imageBase64, setImageBase64] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    try {
      const image = await generateImage(prompt);
      setImageBase64(image);
    } catch {
      alert("Failed to generate image.");
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-xl mx-auto bg-white rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4"> Image Generator</h2>
      <div className="flex gap-2 mb-4">
        <input
          className="flex-1 border rounded px-3 py-2"
          placeholder="Enter image prompt..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button
          className="bg-green-600 text-white px-4 py-2 rounded"
          onClick={handleGenerate}
        >
          {loading ? "Loading..." : "Generate"}
        </button>
      </div>
      {imageBase64 && (
        <img
          src={`data:image/png;base64,${imageBase64}`}
          alt="Generated"
          className="rounded shadow"
        />
      )}
    </div>
  );
};

export default ImageGenerator;
