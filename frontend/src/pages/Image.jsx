import React from "react";
import ImageGenerator from "../components/ImageGenerator";

const Image = () => {
  return (
    <div className="max-w-3xl mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4">Image Generator</h2>
      <ImageGenerator />
    </div>
  );
};

export default Image;
