import React from "react";
import ImageGenerator from "../components/ImageGenerator";

const Image = () => {
  return (
    <div className="mx-auto" style={{ maxWidth: 720 }}>
      <h2 className="text-center mb-4 fw-bold">Image Generator</h2>
      <ImageGenerator />
    </div>
  );
};

export default Image;
