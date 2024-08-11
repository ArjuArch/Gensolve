import React, { useState } from 'react';
import axios from 'axios';
import '../App.css'; 

function ImageUpload() {
  const [file, setFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload_image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setImageUrl(URL.createObjectURL(file));
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Image for Processing</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      {imageUrl && (
        <div className="image-preview">
          <h3>Processed Image</h3>
          <img src={imageUrl} alt="Processed" />
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
