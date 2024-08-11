import React, { useState, useEffect } from 'react';
import '../App.css';

function Plot() {
  const [plotUrl, setPlotUrl] = useState('');

  useEffect(() => {
    setPlotUrl('http://127.0.0.1:5000/get_plot');
  }, []);

  return (
    <div className="plot-container">
      <h2>Generated Plot</h2>
      {plotUrl ? (
        <img src={plotUrl} alt="Generated Plot" />
      ) : (
        <p>No plot available.</p>
      )}
    </div>
  );
}

export default Plot;
