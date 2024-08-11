import React from "react";
import UploadCSV from "./components/UploadCSV";
import UploadImage from "./components/UploadImage";
import Plot from "./components/Plot";
import "./App.css";

function App() {
  return (
    <div className="App">
      <UploadCSV />
      <UploadImage />
      <Plot />
    </div>
  );
}

export default App;
