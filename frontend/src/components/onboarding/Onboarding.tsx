import React, { useState } from 'react';
import UploadStep from './UploadStep';
import { FileMetadata } from '../../types';

const Onboarding: React.FC = () => {
  const [files, setFiles] = useState<Record<string, FileMetadata[]>>({});

  const handleFilesUpdate = (category: string, updatedFiles: FileMetadata[]) => {
    setFiles(prevFiles => ({
      ...prevFiles,
      [category]: updatedFiles,
    }));
  };

  const allFiles = Object.values(files).flat();
  const allFilesUploaded = allFiles.length > 0 && allFiles.every(f => f.status === 'completed');

  return (
    <div>
      <UploadStep
        title="Company DNA"
        description="Upload strategy documents that describe the identity, values, and DNA of your company."
        onFilesUpdate={updatedFiles => handleFilesUpdate('dna', updatedFiles)}
      />
      <UploadStep
        title="Prefered Future"
        description="Upload documents that describe the company's aspirations and perceived future state."
        onFilesUpdate={updatedFiles => handleFilesUpdate('future', updatedFiles)}
      />
      <UploadStep
        title="Products and Terminology"
        description="Upload your product catalog and any additional terminology documents."
        onFilesUpdate={updatedFiles => handleFilesUpdate('products', updatedFiles)}
      />

      {allFiles.length > 0 && (
        <div>
          <h2>Processing Matrix</h2>
          <table>
            <thead>
              <tr>
                <th>File Name</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Format</th>
                <th>Topic</th>
                <th>Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {allFiles.map((fileData, index) => (
                <tr key={index}>
                  <td>{fileData.file.name}</td>
                  <td>{fileData.status}</td>
                  <td>{fileData.metadata?.summary}</td>
                  <td>{fileData.metadata?.format}</td>
                  <td>{fileData.metadata?.topic}</td>
                  <td>{fileData.metadata?.sentiment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {allFilesUploaded && (
        <button style={{ padding: '8px', marginTop: '10px' }}>
          Ready for Next
        </button>
      )}
    </div>
  );
};

export default Onboarding;
