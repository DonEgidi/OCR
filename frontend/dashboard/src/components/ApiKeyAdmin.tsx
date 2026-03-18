import { useEffect, useState } from "react";
import { Key, Plus, CheckCircle, AlertCircle, RefreshCcw } from "lucide-react";
import { keyApi } from "../api";

const ApiKeyAdmin = () => {
  const [keys, setKeys] = useState<any[]>([]);
  const [newKey, setNewKey] = useState("");
  const [loading, setLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);

  const fetchKeys = async () => {
    try {
      const response = await keyApi.getKeys();
      setKeys(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleAddKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newKey === "") return;
    setIsAdding(true);
    try {
      await keyApi.addKey(newKey);
      setNewKey("");
      fetchKeys();
    } catch (error) {
      console.error(error);
      alert("Error al anadir la clave. Posiblemente ya existe.");
    } finally {
      setIsAdding(false);
    }
  };

  const handleReactivate = async (id: number) => {
    try {
      await keyApi.reactivateKey(id);
      fetchKeys();
    } catch (error) {
      console.error(error);
    }
  };

  const activeCount = keys.filter((k) => k.is_active).length;
  const inactiveCount = keys.filter((k) => k.is_active === false).length;

  return (
    <section className="admin-stack">
      <div className="stats-grid">
        <article className="stat-card">
          <span>Claves activas</span>
          <strong>{activeCount}</strong>
        </article>
        <article className="stat-card warning">
          <span>Claves agotadas</span>
          <strong>{inactiveCount}</strong>
        </article>
        <article className="stat-card subtle">
          <span>Proveedor</span>
          <strong>OpenRouter v1</strong>
        </article>
      </div>

      <article className="admin-card">
        <div className="section-header compact">
          <div>
            <p className="section-kicker">Seguridad operativa</p>
            <h3>Registrar nueva API key</h3>
          </div>
          <Key className="w-5 h-5" />
        </div>

        <form onSubmit={handleAddKey} className="key-form">
          <input
            type="password"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            placeholder="sk-or-v1-..."
            className="field-input"
          />
          <button type="submit" disabled={isAdding || newKey === ""} className="btn btn-primary">
            {isAdding ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Guardar clave
          </button>
        </form>
      </article>

      <article className="admin-card table-card">
        <div className="section-header compact">
          <div>
            <p className="section-kicker">Inventario</p>
            <h3>Claves registradas</h3>
          </div>
        </div>

        {loading ? (
          <div className="empty-state small">
            <RefreshCcw className="w-5 h-5 animate-spin" />
            <span>Cargando claves...</span>
          </div>
        ) : keys.length === 0 ? (
          <div className="empty-state small">
            <span>No hay claves registradas en el sistema.</span>
          </div>
        ) : (
          <div className="key-list">
            {keys.map((k) => {
              const dotClass = k.is_active ? "status-dot ok" : "status-dot error";
              return (
                <div key={k.id} className="key-row">
                  <div className="key-row-main">
                    <div className={dotClass}>
                      {k.is_active ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    </div>
                    <div>
                      <p className="key-preview">{k.masked_key || "Clave oculta"}</p>
                      <p className="key-meta">
                        Errores: {k.error_count} • Usada: {k.last_used ? new Date(k.last_used).toLocaleString() : "Nunca"}
                      </p>
                    </div>
                  </div>
                  {k.is_active === false && (
                    <button onClick={() => handleReactivate(k.id)} className="btn btn-outline btn-small">
                      Reactivar
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </article>
    </section>
  );
};

export default ApiKeyAdmin;
