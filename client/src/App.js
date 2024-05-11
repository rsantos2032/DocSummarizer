// import React, { useState, useEffect } from 'react';
// import { BrowserRouter, Link, Switch, Route } from 'react-router-dom';
// import logo from './logo.svg';
// import './App.css';

// function App() {
//   const [currentTime, setCurrentTime] = useState(0);

//   useEffect(() => {
//     fetch('/api/time').then(res => res.json()).then(data => {
//       setCurrentTime(data.time);
//     });
//   }, []);

//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a> 
//         <p>The current time is {currentTime}.</p>
//         <p>This is a new line as 2 + 2.</p>
//       </header>
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import axios from  'axios';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    const allowedTypes = ['text/plain', 'application/pdf']
    if (selectedFile && !allowedTypes.includes(selectedFile.type)) {
      setErrorMessage('Please select a PDF file.');
    } else {
      setFile(selectedFile);
      setErrorMessage('');
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setErrorMessage('Please select a file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('File uploaded successfully.');
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <input type="file" accept=".pdf,.txt" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Submit</button>
      {errorMessage && <div style={{color:'red'}}>{errorMessage}</div>}
    </div>
  );
};

export default FileUpload;