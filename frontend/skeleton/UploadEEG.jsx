import React, { useState } from 'react';
import { Upload, FileUp } from 'lucide-react';

/**
 * EEG File Upload Component
 * Handles .npy file uploads for enrollment and authentication
 */
const UploadEEG = ({ onUpload, multiple = false, label = "Upload EEG Trial" }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    if (onUpload) {
      onUpload(files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
    if (onUpload) {
      onUpload(files);
    }
  };

  return (
    <div className="w-full">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          <FileUp className="w-12 h-12 text-gray-400" />
          
          <div>
            <label
              htmlFor="file-upload"
              className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <Upload className="w-4 h-4 mr-2" />
              {label}
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".npy"
              multiple={multiple}
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <p className="text-sm text-gray-500">
            {multiple ? 'Select multiple .npy files' : 'Select a .npy file'} or drag and drop
          </p>

          {selectedFiles.length > 0 && (
            <div className="mt-4 w-full">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Selected files ({selectedFiles.length}):
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                {selectedFiles.map((file, idx) => (
                  <li key={idx} className="truncate">
                    {file.name}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadEEG;
