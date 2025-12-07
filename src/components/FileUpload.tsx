/**
 * Secure file upload component for WatchTower
 */

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Upload, File, X, AlertCircle } from "lucide-react";
import { FILE_TYPES_ALLOWED, MAX_FILE_SIZE } from "@/utils/constants";

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  accept?: string;
  maxSize?: number;
}

export const FileUpload = ({
  onFileSelect,
  accept = ".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif",
  maxSize = MAX_FILE_SIZE,
}: FileUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const validateFile = (file: File): boolean => {
    setError(null);

    if (!FILE_TYPES_ALLOWED.includes(file.type)) {
      setError("Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, GIF");
      return false;
    }

    if (file.size > maxSize) {
      setError(`File too large. Maximum size: ${maxSize / 1024 / 1024}MB`);
      return false;
    }

    return true;
  };

  const handleFile = useCallback(
    (selectedFile: File) => {
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        onFileSelect(selectedFile);
      }
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        handleFile(droppedFile);
      }
    },
    [handleFile]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
    onFileSelect(null);
  };

  return (
    <div className="space-y-2">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-accent bg-accent/5"
            : error
            ? "border-destructive bg-destructive/5"
            : "border-border hover:border-primary/50"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {file ? (
          <div className="flex items-center justify-center gap-4">
            <File className="h-10 w-10 text-primary" />
            <div className="text-left">
              <p className="font-medium text-foreground">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={removeFile}
              className="p-2 hover:bg-muted rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-muted-foreground" />
            </button>
          </div>
        ) : (
          <label className="cursor-pointer">
            <input
              type="file"
              accept={accept}
              onChange={handleChange}
              className="hidden"
            />
            <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-foreground font-medium">
              Drop file here or click to upload
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              PDF, DOC, DOCX, JPG, PNG, GIF (Max {maxSize / 1024 / 1024}MB)
            </p>
          </label>
        )}
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-destructive text-sm"
        >
          <AlertCircle className="h-4 w-4" />
          {error}
        </motion.div>
      )}
    </div>
  );
};
