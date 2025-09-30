import React, { useState, useEffect } from 'react';
import FileDropzone from './FileDropzone';
import { FileMetadata } from '../../../types';
import { quickScan } from '../../../services/mockApi';

interface UploadStepProps {
  title: string;
  description: string;
  onFilesUpdate: (files: FileMetadata[]) => void;
}

const UploadStep: React.FC<UploadStepProps> = ({ title, description, onFilesUpdate }) => {
  const [uploadedFiles, setUploadedFiles] = useState<FileMetadata[]>([]);

  const handleDrop = (files: File[]) => {
    const newFiles: FileMetadata[] = files.map(file => ({ file, status: 'scanning' }));
    setUploadedFiles(prevFiles => [...prevFiles, ...newFiles]);
  };

  useEffect(() => {
    const scanFiles = async () => {
      const newFiles = [...uploadedFiles];
      for (let i = 0; i < newFiles.length; i++) {
        const currentFile = newFiles[i];
        if (currentFile && currentFile.status === 'scanning') {
          const metadata = await quickScan(currentFile.file);
          newFiles[i] = { file: currentFile.file, status: 'completed', metadata };
        }
      }
      setUploadedFiles(newFiles);
      onFilesUpdate(newFiles);
    };
    scanFiles();
  }, [uploadedFiles, onFilesUpdate]);

  const completedFiles = uploadedFiles.filter(f => f.status === 'completed').length;
  const progress = uploadedFiles.length > 0 ? (completedFiles / uploadedFiles.length) * 100 : 0;

  return (
    <div>
      <h2>{title}</h2>
      <p>{description}</p>
      <FileDropzone onDrop={handleDrop} />
      {uploadedFiles.length > 0 && (
        <div>
          <h4>Upload Progress:</h4>
          <progress value={progress} max="100" />
          <span>{Math.round(progress)}%</span>
        </div>
      )}
    </div>
  );
};

export default UploadStep;
