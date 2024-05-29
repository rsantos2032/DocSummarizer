import axios from 'axios';
import React, { useState } from 'react';
import backgroundImage from './legal_document_image.jpg'


const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);
  const [summarizedText, setSummarizedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // const [summaryLength, setSummaryLength] = useState(64);
  const [activeTab, setActiveTab] = useState('text');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
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
        if (error.response.status == 422){
          setErrorMessage('Invalid file format, please upload .pdf, .txt, or .docx file.');
        } else {
          setErrorMessage('Error uploading file.');
        }
        return;
      } finally {
        setIsLoading(false);
      }
    }

    try {
      setIsLoading(true);
      setErrorMessage('');
      const response = await axios.post('/summarize', {
        text: inputText
      });
      setSummarizedText(response.data.summarized_text);
    } catch (error) {
      console.error('Error summarizing text:', error);
      setErrorMessage('Error summarizing text.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div
        className="background-container"
        style={{
          backgroundImage: `url(${backgroundImage})`,
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
          height: '33vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <h1 class="header">LawSum</h1>
        <br></br>
        <h3 class="description">AI-powered tools for streamlined legal document summarization.</h3>
      </div>
      <div className="center">
        <section className="grid-container">
          <div className="text-input-container">
            <div className="tabs">
              <button
                onClick={() => handleTabChange('text')}
                className={activeTab === 'text' ? 'active' : ''}
              >
                Text
              </button>
              <button
                onClick={() => handleTabChange('upload')}
                className={activeTab === 'upload' ? 'active' : ''}
              >
                Upload
              </button>
            </div>
            {activeTab === 'text' ? (
              <textarea value={text} onChange={handleTextChange} />
            ) : (
              <div className="upload-container">
                <input
                  type="file"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  id="file-input"
                />
                <label htmlFor="file-input" className="upload-button">
                  Choose File
                </label>
                {file && <span>{file.name}</span>}
                <button
                  className="summarize-button"
                  onClick={handleSummarize}
                  disabled={isLoading}
                >
                  Summarize
                </button>
              </div>
            )}
            {activeTab === 'text' && (
              <button
                className="summarize-button"
                onClick={handleSummarize}
                disabled={isLoading}
              >
                Summarize
              </button>
            )}
          </div>
          <div className="summarized-text-container">
            {summarizedText && <div>{summarizedText}</div>}
          </div>
        </section>
        {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
        {isLoading && <div>Loading...</div>}
      </div>
    </div>
  );
};

export default FileUpload;