import { useState } from "react";
import { FileText, ShieldCheck, Activity, Search } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import FileUploader from "./components/FileUploader.tsx";
import DocumentList from "./components/DocumentList.tsx";
import ApiKeyAdmin from "./components/ApiKeyAdmin.tsx";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState<"user" | "admin">("user");
  const userTabClass = activeTab === "user" ? "tab-button active" : "tab-button";
  const adminTabClass = activeTab === "admin" ? "tab-button active" : "tab-button";

  return (
    <div className="app-shell">
      <div className="app-aurora app-aurora-left" />
      <div className="app-aurora app-aurora-right" />

      <nav className="topbar shell-width">
        <div className="brand-block">
          <div className="brand-icon">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="brand-kicker">Municipalidad de Pergamino</p>
            <h1 className="brand-title">Panel de Procesamiento Documental</h1>
          </div>
        </div>

        <div className="tab-switcher">
          <button onClick={() => setActiveTab("user")} className={userTabClass}>
            <FileText className="w-4 h-4" />
            Operacion
          </button>
          <button onClick={() => setActiveTab("admin")} className={adminTabClass}>
            <ShieldCheck className="w-4 h-4" />
            Administracion
          </button>
        </div>
      </nav>

      <main className="shell-width app-main">
        <AnimatePresence mode="wait">
          {activeTab === "user" ? (
            <motion.div
              key="user"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              className="page-stack"
            >
              {/*
              <section className="hero-panel">
                <div className="hero-copy">
                  <p className="section-kicker">Operacion</p>
                  <h2>Gestion centralizada para OCR, extraccion y conversion a JSON.</h2>
                  <p>
                    Cargue documentos PDF o imagen, supervise el estado del procesamiento y consulte el resultado estructurado sin salir del panel.
                  </p>
                  <div className="hero-inline-metadata">
                    <span className="soft-chip"><Shield className="w-4 h-4" /> Trazabilidad persistente</span>
                    <span className="soft-chip"><Network className="w-4 h-4" /> Orquestacion por cola</span>
                  </div>
                </div>

                <div className="hero-metrics hero-metrics-compact">
                  <article className="metric-card accent-teal">
                    <span>Ingreso documental</span>
                    <strong>PDF, JPG y PNG</strong>
                    <p>Recepcion unificada con almacenamiento y encolado inmediato.</p>
                  </article>
                  <article className="metric-card accent-slate">
                    <span>Extraccion OCR</span>
                    <strong>Modelos sobre OpenRouter</strong>
                    <p>Texto original conservado junto al resultado final.</p>
                  </article>
                  <article className="metric-card accent-orange">
                    <span>Salida estructurada</span>
                    <strong>JSON normalizado</strong>
                    <p>Contrato estable para consumo posterior y auditoria.</p>
                  </article>
                </div>
              </section>
              */}
              <section className="dashboard-grid">
                <div className="main-column">
                  <FileUploader />
                </div>
                <aside className="side-column">
                  <div className="status-card">
                    <div className="section-header compact">
                      <div>
                        <p className="section-kicker">Estado general</p>
                        <h3>Supervision del Pipeline</h3>
                      </div>
                      <span className="soft-chip positive">Operativo</span>
                    </div>

                    <div className="status-list">
                      <div className="status-row">
                        <div>
                          <span>OCR y conversion</span>
                          <strong>Modelos disponibles</strong>
                        </div>
                        <div className="status-marker success" />
                      </div>
                      <div className="status-row">
                        <div>
                          <span>Cola de mensajeria</span>
                          <strong>RabbitMQ conectado</strong>
                        </div>
                        <div className="status-marker success" />
                      </div>
                      <div className="status-row">
                        <div>
                          <span>Persistencia y consulta</span>
                          <strong>Resultados almacenados</strong>
                        </div>
                        <div className="status-marker success" />
                      </div>
                    </div>
                  </div>
                </aside>
              </section>

              <section className="records-section">
                <div className="section-header section-header-wide">
                  <div>
                    <p className="section-kicker">Seguimiento</p>
                    <h3>Documentos procesados</h3>
                  </div>
                  <div className="search-shell search-shell-muted">
                    <Search className="w-4 h-4" />
                    <input type="text" placeholder="Busqueda disponible en una siguiente iteracion" readOnly />
                  </div>
                </div>
                <DocumentList mode="user" />
              </section>
            </motion.div>
          ) : (
            <motion.div
              key="admin"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              className="page-stack"
            >
              {/**
              <section className="hero-panel admin-hero">
                <div className="hero-copy hero-copy-wide">
                  <p className="section-kicker">Administracion</p>
                  <h2>Control de claves, monitoreo del servicio y visibilidad completa del procesamiento.</h2>
                  <p>
                    Esta vista concentra la operacion sensible del sistema: disponibilidad de claves, monitoreo de documentos y consulta de resultados persistidos.
                  </p>
                </div>
                <div className="hero-strip">
                  <div className="hero-strip-item">
                    <ShieldCheck className="w-5 h-5" />
                    <div>
                      <span>Seguridad</span>
                      <strong>Claves enmascaradas</strong>
                    </div>
                  </div>
                  <div className="hero-strip-item">
                    <Database className="w-5 h-5" />
                    <div>
                      <span>Persistencia</span>
                      <strong>Resultados y trazas</strong>
                    </div>
                  </div>
                  <div className="hero-strip-item">
                    <FileStack className="w-5 h-5" />
                    <div>
                      <span>Supervision</span>
                      <strong>Vista global de documentos</strong>
                    </div>
                  </div>
                </div>
              </section>
              */}
              <ApiKeyAdmin />

              <section className="records-section">
                <div className="section-header">
                  <div>
                    <p className="section-kicker">Monitoreo</p>
                    <h3>Vista global de documentos</h3>
                  </div>
                </div>
                <DocumentList mode="admin" />
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="app-footer">
        <p>Municipalidad de Pergamino • OCR • OpenRouter • Procesamiento documental</p>
      </footer>
    </div>
  );
}

export default App;
