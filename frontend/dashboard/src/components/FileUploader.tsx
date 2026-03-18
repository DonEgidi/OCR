import React, { useRef, useState } from "react";
import { Upload, X, File, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ocrApi } from "../api";

const FileUploader = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus("idle");
    }
  };

  const handleUpload = async () => {
    if (file === null) return;
    setStatus("uploading");
    try {
      await ocrApi.uploadDocument(file);
      setStatus("success");
      setTimeout(() => {
        setFile(null);
        setStatus("idle");
      }, 2500);
    } catch (error) {
      console.error(error);
      setStatus("error");
    }
  };

  let dropzoneClass = "upload-dropzone";
  if (isDragging) dropzoneClass += " dragging";
  if (file !== null) dropzoneClass += " has-file";

  return (
    <section className="upload-card">
      <div className="section-header compact">
        <div>
          <p className="section-kicker">Ingreso de archivo</p>
          <h3>Carga y despacho a procesamiento</h3>
        </div>
        <span className="soft-chip neutral-chip">PDF, JPG, PNG</span>
      </div>

      {/** 
      <div className="upload-intro-grid">
        <article className="info-tile">
          <ShieldCheck className="w-5 h-5" />
          <div>
            <strong>Recepcion controlada</strong>
            <span>El archivo se persiste y se encola para procesamiento asincronico.</span>
          </div>
        </article>
        <article className="info-tile">
          <FileSearch className="w-5 h-5" />
          <div>
            <strong>OCR y extraccion</strong>
            <span>Se conserva el texto base para auditoria y reprocesamiento.</span>
          </div>
        </article>
        <article className="info-tile">
          <Braces className="w-5 h-5" />
          <div>
            <strong>Salida JSON</strong>
            <span>El resultado final queda normalizado bajo una estructura fija.</span>
          </div>
        </article>
      </div>
      */}
      <div
        className={dropzoneClass}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            setStatus("idle");
          }
        }}
      >
        <input
          type="file"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*,.pdf"
        />

        <AnimatePresence mode="wait">
          {file === null ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="upload-empty"
            >
              <div className="upload-icon-shell">
                <Upload className="w-8 h-8" />
              </div>
              <div className="upload-copy">
                <h4>Seleccione un documento para iniciar el flujo</h4>
                <p>El sistema enviara el archivo a OCR, convertira el contenido a JSON y almacenara tanto la salida estructurada como el texto original.</p>
              </div>
              <div className="upload-actions">
                <button onClick={() => fileInputRef.current?.click()} className="btn btn-primary">
                  Seleccionar archivo
                </button>
                <span className="upload-hint">Tamanio recomendado: hasta 10 MB</span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="selected"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.97 }}
              className="upload-selected"
            >
              <div className="file-preview-card">
                <div className="file-preview-icon">
                  <File className="w-5 h-5" />
                </div>
                <div className="file-preview-copy">
                  <strong>{file.name}</strong>
                  <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
                <button
                  onClick={() => setFile(null)}
                  disabled={status === "uploading"}
                  className="icon-button subtle"
                  title="Quitar archivo"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="upload-status-row">
                {status === "idle" && (
                  <button onClick={handleUpload} className="btn btn-primary btn-wide">
                    Iniciar procesamiento
                  </button>
                )}
                {status === "uploading" && (
                  <button disabled className="btn btn-primary btn-wide is-loading">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Enviando documento...
                  </button>
                )}
                {status === "success" && (
                  <p className="status-inline success">
                    <CheckCircle2 className="w-5 h-5" />
                    Documento enviado correctamente
                  </p>
                )}
                {status === "error" && (
                  <p className="status-inline error">
                    <AlertCircle className="w-5 h-5" />
                    No se pudo cargar el archivo
                  </p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default FileUploader;
