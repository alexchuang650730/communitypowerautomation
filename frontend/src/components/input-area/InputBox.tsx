import React, { useState, useRef } from 'react';
import './InputBox.css';

interface InputBoxProps {
  onSend: (message: string, files?: File[]) => void;
  agentType: 'code' | 'ppt' | 'web' | 'general';
}

const InputBox: React.FC<InputBoxProps> = ({ onSend, agentType }) => {
  const [message, setMessage] = useState<string>('');
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const placeholderTexts = {
    code: "请输入代码需求或上传文件，代码智能体将帮您实现...",
    ppt: "请输入PPT的主题和需求，或上传文件，PPT智能体将帮您制作...",
    web: "请输入网页需求或上传设计稿，网页智能体将帮您创建...",
    general: "请输入您的问题或需求，通用智能体将为您提供帮助..."
  };

  const handleSend = () => {
    if (message.trim() || files.length > 0) {
      onSend(message, files);
      setMessage('');
      setFiles([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files);
      setFiles(prev => [...prev, ...fileArray]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files) {
      const fileArray = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...fileArray]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div 
      className={`input-box-container ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholderTexts[agentType]}
        rows={3}
        className="input-box-textarea"
      />
      
      {files.length > 0 && (
        <div className="input-box-files">
          {files.map((file, index) => (
            <div key={index} className="input-box-file">
              <span className="input-box-file-name">{file.name}</span>
              <button 
                className="input-box-file-remove"
                onClick={() => removeFile(index)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      
      <div className="input-box-actions">
        <button 
          className="input-box-attachment"
          onClick={openFileDialog}
        >
          📎
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          style={{ display: 'none' }}
        />
        <button 
          className="input-box-send"
          onClick={handleSend}
          disabled={!message.trim() && files.length === 0}
        >
          发送
        </button>
      </div>
    </div>
  );
};

export default InputBox;
