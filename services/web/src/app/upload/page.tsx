'use client';
import { useState } from 'react';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
    setStatus('');
    setProgress(0);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please choose a file first.');
      return;
    }

    setIsUploading(true);
    setStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('user_id', '1');
      formData.append('language', 'es');
      formData.append('file', file);

      const apiUrl = process.env.PALABRA_API_URL || 'http://localhost:4000';
      const xhr = new XMLHttpRequest();

      xhr.open('POST', `${apiUrl}/api/books/upload`, true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          setProgress(percent);
        }
      };

      xhr.onload = () => {
        setIsUploading(false);
        if (xhr.status >= 200 && xhr.status < 300) {
          setStatus('✅ Upload successful! Processing book...');
        } else {
          setStatus(`❌ Upload failed: ${xhr.statusText}`);
        }
      };

      xhr.onerror = () => {
        setIsUploading(false);
        setStatus('❌ Network error during upload.');
      };

      xhr.send(formData);
    } catch (err) {
      console.error(err);
      setIsUploading(false);
      setStatus('❌ Unexpected error occurred.');
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      <div className="bg-white shadow-md rounded-lg p-8 max-w-md w-full text-center">
        <h1 className="text-2xl font-semibold mb-6">Upload a Book</h1>

        <input
          type="file"
          onChange={handleFileChange}
          className="mb-4 block w-full text-sm text-gray-700
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-md file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-600 file:text-white
                     hover:file:bg-blue-700"
        />

        <button
          onClick={handleUpload}
          disabled={isUploading}
          className={`w-full py-2 px-4 rounded-md text-white font-semibold transition 
            ${isUploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}
          `}
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>

        {progress > 0 && (
          <div className="w-full bg-gray-200 rounded-full h-2.5 mt-4">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        {status && <p className="mt-4 text-gray-700">{status}</p>}
      </div>
    </main>
  );
}
