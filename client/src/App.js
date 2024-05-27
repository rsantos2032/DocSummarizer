import axios from 'axios';
import React, { useState } from 'react';


const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);
  const [summarizedText, setSummarizedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [summaryLength, setSummaryLength] = useState(64);
  const [activeTab, setActiveTab] = useState('text');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    // const allowedTypes = ['text/plain', 'application/pdf']
    // if (selectedFile && !allowedTypes.includes(selectedFile.type)) {
    //   setErrorMessage('Please select a PDF or Text file.');
    // } else {
    //   setFile(selectedFile);
    //   setErrorMessage('');
    // }
  };

  const handleTextChange = (event) => {
    setText(event.target.value);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setErrorMessage(null);
    if (tab === 'text'){
      setFile(null);
    } else if (tab === 'upload'){
      setText('');
    }
  };

  const handleSummarize = async() => {
    if (!text && !file) {
      setErrorMessage('Please input text or upload a file.');
      return;
    }

    let inputText = text;

    if (!inputText && file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        setIsLoading(true);
        setErrorMessage('');
        const response = await axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        inputText = response.data.text;
      } catch (error) {
        console.error('Error uploading file:', error);
        setErrorMessage('Error uploading file.');
        return;
      } finally {
        setIsLoading(false);
      }
    }

    try {
      setIsLoading(true);
      setErrorMessage('');
      const response = await axios.post('/summarize', {
        text: inputText,
        length: summaryLength
      });
      setSummarizedText(response.data.summarized_text);
    } catch (error) {
      console.error('Error summarizing text:', error);
      setErrorMessage('Error summarizing text.');
    } finally {
      setIsLoading(false);
    }
  };

  // const handleSubmit = async () => {
  //   if (!file) {
  //     setErrorMessage('Please select a file.');
  //     return;
  //   }

  //   const formData = new FormData();
  //   formData.append('file', file);

  //   try {
  //     setIsLoading(true);
  //     const response = await axios.post('/upload', formData, {
  //       headers: {
  //         'Content-Type': 'multipart/form-data'
  //       }
  //     });
  //     setSummarizedText(response.data.summarized_text)
  //     console.log('File uploaded successfully.');
  //   } catch (error) {
  //     console.error('Error uploading file:', error);
  //     setErrorMessage('Error uploading file.')
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  // return (
  //   <div className="center">
  //     <h1>DocSummarizer</h1>
  //     {/* <h2>Document Summarizer</h2> */}

  //     <section className="upload-section" id="upload">
  //       <input type="file" id="file-input" accept=".pdf,.txt" onChange={handleFileChange} hidden />
  //       <label htmlFor="file-input" className="custom-file-upload">
  //         Choose File
  //       </label>
  //       {file && <span className="file-name">{file.name}</span>}
  //       {isLoading ? (
  //         <span className="loading-indicator">Loading...</span>
  //       ) : (
  //         <button className="custom-button" onClick={handleSubmit} disabled={isLoading}>
  //           Submit
  //         </button>
  //       )}
  //     </section>

  //     <section className="summarized-section center">
  //       <div className="summarized-text">
  //         {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
  //         {summarizedText && <div style={{ color: 'blue' }}>{summarizedText}</div>}
  //       </div>
  //     </section>
  //   </div>
  // );

  return (
    <div className="center">
      <h1>LawSum</h1>
      <h3>AI powered tools built for law document summarization</h3>

      <div className="slider">
        <span>Summary Length: </span>
        <input
          type="range"
          min="64"
          max="256"
          step="64"
          value={summaryLength}
          onChange={(e) => setSummaryLength(parseInt(e.target.value))}
          list="tickmarks"
        />
        <datalist id="tickmarks">
          <option value="64" label="64"></option>
          <option value="128" label="128"></option>
          <option value="192" label="192"></option>
          <option value="256" label="256"></option>
        </datalist>
        <div className="slider-values">
          <span>64</span>
          <span>128</span>
          <span>192</span>
          <span>256</span>
        </div>
      </div>

      <section className="grid-container">
        <div className="text-input-container">
          <div className="tabs">
            <button onClick={() => handleTabChange('text')} className={activeTab === 'text' ? 'active' : ''}>Text</button>
            <button onClick={() => handleTabChange('upload')} className={activeTab === 'upload' ? 'active' : ''}>Upload</button>
          </div>
          {activeTab === 'text' ? (
            <textarea value={text} onChange={handleTextChange} />
          ) : (
            <div className="upload-container">
              <input type="file" onChange={handleFileChange} style={{ display: 'none' }} id="file-input" />
              <label htmlFor="file-input" className="upload-button">Choose File</label>
              {file && <span>{file.name}</span>}
            </div>
          )}
          <button className='summarize-button' onClick={handleSummarize} disabled={isLoading}>Summarize</button>
        </div>

        <div className="summarized-text-container">
          {summarizedText && <div>{summarizedText}</div>}
        </div>
      </section>

      {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
      {isLoading && <div>Loading...</div>}
    </div>
  );
};

export default FileUpload;