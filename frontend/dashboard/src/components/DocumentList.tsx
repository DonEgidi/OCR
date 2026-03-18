import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Eye, RefreshCcw, FileJson, Clock3, Bot, FileSearch, X, FileText, ExternalLink, Coins, Loader2 } from "lucide-react";
import { ocrApi } from "../api";

const formatDateTime = (value?: string | null) => {
  if (value === undefined || value === null || value === "") return "No disponible";
  return new Date(value).toLocaleString();
};

const formatTokenUsage = (usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number } | null) => {
  if (!usage) return "No reportado por OpenRouter";
  const promptTokens = usage.prompt_tokens ?? 0;
  const completionTokens = usage.completion_tokens ?? 0;
  const totalTokens = usage.total_tokens ?? 0;
  return `Prompt ${promptTokens} · Completion ${completionTokens} · Total ${totalTokens}`;
};

const getFileExtension = (filename?: string | null) => {
  if (!filename) return "";
  const parts = filename.split(".");
  return parts.length > 1 ? parts.pop()?.toLowerCase() || "" : "";
};

const isImageExtension = (extension: string) => ["png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"].includes(extension);

const DocumentModal = ({ docData, onClose }: { docData: any; onClose: () => void }) => {
  const [detailDoc, setDetailDoc] = useState<any>(docData);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  useEffect(() => {
    const previousOverflow = window.document.body.style.overflow;
    window.document.body.style.overflow = "hidden";
    return () => {
      window.document.body.style.overflow = previousOverflow;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchDetail = async () => {
      setIsLoadingDetail(true);
      try {
        const response = await ocrApi.getDocument(docData.id);
        if (!cancelled) {
          setDetailDoc(response.data);
        }
      } catch (error) {
        console.error("Error loading document detail:", error);
      } finally {
        if (!cancelled) {
          setIsLoadingDetail(false);
        }
      }
    };

    fetchDetail();
    return () => {
      cancelled = true;
    };
  }, [docData.id]);

  const originalFileUrl = ocrApi.getDocumentOriginalUrl(detailDoc.id);
  const extension = getFileExtension(detailDoc.filename);
  const isImage = isImageExtension(extension);
  const isPdf = extension === "pdf";

  const modal = (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card modal-card-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="section-kicker">Detalle de procesamiento</p>
            <h3>{detailDoc.filename}</h3>
          </div>
          <button onClick={onClose} className="icon-button" title="Cerrar detalle">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="modal-body">
          {isLoadingDetail && (
            <div className="detail-loading-banner">
              <Loader2 className="w-4 h-4 animate-spin" />
              Actualizando detalle del documento...
            </div>
          )}

          <div className="detail-grid detail-grid-top">
            <div className="detail-card">
              <div className="detail-label"><Clock3 className="w-4 h-4" /> Hora inicio</div>
              <strong>{formatDateTime(detailDoc.processing_started_at)}</strong>
            </div>
            <div className="detail-card">
              <div className="detail-label"><Clock3 className="w-4 h-4" /> Hora fin</div>
              <strong>{formatDateTime(detailDoc.processing_completed_at)}</strong>
            </div>
            <div className="detail-card">
              <div className="detail-label"><FileSearch className="w-4 h-4" /> Modelo OCR</div>
              <strong>{detailDoc.ocr_model_used || "No disponible"}</strong>
              <span className="detail-meta"><Coins className="w-4 h-4" /> {formatTokenUsage(detailDoc.ocr_token_usage)}</span>
            </div>
            <div className="detail-card">
              <div className="detail-label"><Bot className="w-4 h-4" /> Modelo JSON</div>
              <strong>{detailDoc.llm_model_used || "No disponible"}</strong>
              <span className="detail-meta"><Coins className="w-4 h-4" /> {formatTokenUsage(detailDoc.llm_token_usage)}</span>
            </div>
          </div>

          <div className="detail-layout">
            <div className="detail-main-column">
              <div className="detail-section">
                <div className="detail-section-header detail-section-header-spread">
                  <h4>Archivo original</h4>
                  <a className="btn btn-outline btn-small" href={originalFileUrl} target="_blank" rel="noreferrer">
                    <ExternalLink className="w-4 h-4" />
                    Abrir original
                  </a>
                </div>

                <div className="original-file-shell">
                  {isImage ? (
                    <img src={originalFileUrl} alt={detailDoc.filename} className="original-file-image" />
                  ) : isPdf ? (
                    <iframe src={originalFileUrl} title={detailDoc.filename} className="original-file-frame" />
                  ) : (
                    <div className="original-file-fallback">
                      <FileText className="w-6 h-6" />
                      <p>No hay previsualizacion embebida para este tipo de archivo.</p>
                      <a className="btn btn-primary btn-small" href={originalFileUrl} target="_blank" rel="noreferrer">
                        Abrir archivo
                      </a>
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-section">
                <div className="detail-section-header">
                  <h4>Texto original OCR</h4>
                </div>
                <div className="detail-text">{detailDoc.raw_text || "No disponible"}</div>
              </div>
            </div>

            <div className="detail-side-column">
              <div className="detail-section">
                <div className="detail-section-header">
                  <h4>Todos los datos extraidos</h4>
                </div>
                <pre className="detail-code detail-code-tall">{JSON.stringify(detailDoc.json_result, null, 2)}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modal, window.document.body);
};

const DocumentList = ({ mode }: { mode: "user" | "admin" }) => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);

  const fetchDocs = async () => {
    try {
      const response = await ocrApi.getDocuments();
      setDocuments(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchDocs();
    const interval = setInterval(fetchDocs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleReprocess = async (id: string) => {
    try {
      await ocrApi.reprocessDocument(id);
      fetchDocs();
    } catch (error) {
      console.error("Error reprocessing:", error);
    }
  };

  const renderStatus = (doc: any) => {
    let badgeClass = "status-badge neutral";
    let label = doc.status;

    if (doc.status === "pending") {
      badgeClass = "status-badge warning";
      label = "Pendiente";
    } else if (doc.status === "extracting") {
      badgeClass = "status-badge processing";
      label = "OCR en proceso";
    } else if (doc.status === "converting") {
      badgeClass = "status-badge processing";
      label = "IA procesando";
    } else if (doc.status === "completed") {
      badgeClass = "status-badge success";
      label = "Completado";
    } else if (doc.status === "failed") {
      badgeClass = "status-badge danger";
      label = "Error";
    }

    return (
      <div className="status-with-tooltip">
        <span className={badgeClass}>{label}</span>
        {doc.status === "failed" && <span className="status-tooltip">{doc.error_message || "Error desconocido"}</span>}
      </div>
    );
  };

  return (
    <>
      <section className="records-card">
        {documents.length === 0 ? (
          <div className="empty-state">
            <FileJson className="w-5 h-5" />
            <span>No hay documentos procesados aun.</span>
          </div>
        ) : (
          <div className="records-table-shell">
            <table className="records-table">
              <thead>
                <tr>
                  <th>Documento</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  {mode === "admin" && <th>FTP Path</th>}
                  <th className="actions-cell">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => {
                  const rowActionsClass = "table-actions";
                  const reprocessDisabled = doc.status === "converting" || doc.status === "extracting";
                  const viewDisabled = doc.status !== "completed";
                  return (
                    <tr key={doc.id}>
                      <td>
                        <div className="doc-cell">
                          <div className="doc-icon"><FileJson className="w-4 h-4" /></div>
                          <div>
                            <strong>{doc.filename}</strong>
                            <span>{doc.id}</span>
                          </div>
                        </div>
                      </td>
                      <td>{renderStatus(doc)}</td>
                      <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                      {mode === "admin" && <td className="mono-cell">{doc.ftp_path}</td>}
                      <td className="actions-cell">
                        <div className={rowActionsClass}>
                          <button
                            onClick={() => handleReprocess(doc.id)}
                            className="icon-button"
                            title="Reprocesar"
                            disabled={reprocessDisabled}
                          >
                            <RefreshCcw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setSelectedDoc(doc)}
                            className="icon-button primary"
                            title="Ver detalle"
                            disabled={viewDisabled}
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedDoc !== null && <DocumentModal docData={selectedDoc} onClose={() => setSelectedDoc(null)} />}
    </>
  );
};

export default DocumentList;
