import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";

import "../App.css";
import { apiGet } from "../lib/api";
import type {
  Keg,
  KegFormFactor,
  PackagingFormat,
} from "../types/api";

const formFactorLabels: Record<KegFormFactor, string> = {
  standard: "Estándar",
  flat: "Flat",
  slim: "Slim",
};

const formatVolume = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(Number(value));

function KegQrLabelsPage() {
  const [kegs, setKegs] = useState<Keg[]>([]);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [selectedKegIds, setSelectedKegIds] = useState<Set<number>>(
    new Set(),
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [kegsData, formatsData] = await Promise.all([
        apiGet<Keg[]>("/kegs/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
      ]);

      setKegs(kegsData);
      setFormats(
        formatsData.filter((format) => format.format_type === "keg"),
      );
      setSelectedKegIds(new Set(kegsData.map((keg) => keg.id)));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los barriles.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const selectedKegs = useMemo(
    () => kegs.filter((keg) => selectedKegIds.has(keg.id)),
    [kegs, selectedKegIds],
  );

  function getFormat(keg: Keg) {
    return (
      formats.find(
        (format) => format.id === keg.packaging_format_id,
      ) ?? null
    );
  }

  function toggleKeg(kegId: number) {
    setSelectedKegIds((currentIds) => {
      const nextIds = new Set(currentIds);

      if (nextIds.has(kegId)) {
        nextIds.delete(kegId);
      } else {
        nextIds.add(kegId);
      }

      return nextIds;
    });
  }

  function selectAll() {
    setSelectedKegIds(new Set(kegs.map((keg) => keg.id)));
  }

  function clearSelection() {
    setSelectedKegIds(new Set());
  }

  return (
    <main className="dashboard">
      <section className="page-heading print-hidden">
        <p className="eyebrow">Barriles</p>
        <h1>Imprimir etiquetas QR</h1>
        <p>
          Seleccioná los barriles y generá etiquetas de 4 × 5 cm para hoja A4.
        </p>

        <Link className="inline-link-button" to="/barriles">
          Volver a barriles
        </Link>
      </section>

      {isLoading && <p className="print-hidden">Cargando barriles...</p>}

      {error && (
        <p className="error-message print-hidden" role="alert">
          {error}
        </p>
      )}

      {!isLoading && !error && (
        <>
          <section className="panel print-hidden">
            <h2>Selección de etiquetas</h2>

            <p className="form-help">
              Etiquetas seleccionadas: {selectedKegs.length} de {kegs.length}.
            </p>

            <div className="button-row">
              <button onClick={selectAll} type="button">
                Seleccionar todos
              </button>

              <button onClick={clearSelection} type="button">
                Limpiar selección
              </button>

              <button
                disabled={selectedKegs.length === 0}
                onClick={() => window.print()}
                type="button"
              >
                Imprimir etiquetas
              </button>
            </div>

            <div className="checkbox-list keg-label-selection">
              {kegs.map((keg) => {
                const format = getFormat(keg);

                return (
                  <label key={keg.id} className="checkbox-option">
                    <input
                      checked={selectedKegIds.has(keg.id)}
                      onChange={() => toggleKeg(keg.id)}
                      type="checkbox"
                    />

                    <span>
                      <strong>{keg.code}</strong>
                      {" · "}
                      {format
                        ? `${format.name} · ${formatVolume(
                            format.capacity_liters,
                          )} L`
                        : "Formato no disponible"}
                      {" · "}
                      {formFactorLabels[keg.form_factor]}
                    </span>
                  </label>
                );
              })}
            </div>
          </section>

          <section className="qr-print-sheet">
            {selectedKegs.map((keg) => {
              const format = getFormat(keg);
              const qrUrl = `${window.location.origin}/barriles/qr/${encodeURIComponent(
                keg.code,
              )}`;

              return (
                <article key={keg.id} className="qr-print-label">
                  <QRCodeSVG
                    bgColor="#ffffff"
                    fgColor="#172033"
                    level="M"
                    marginSize={1}
                    value={qrUrl}
                  />

                  <strong>{keg.code}</strong>

                  <span>
                    {format
                      ? `${format.name} · ${formatVolume(
                          format.capacity_liters,
                        )} L`
                      : "Formato no disponible"}
                  </span>

                  <span>{formFactorLabels[keg.form_factor]}</span>

                  <small>ELIXIA art beer</small>
                </article>
              );
            })}
          </section>
        </>
      )}
    </main>
  );
}

export default KegQrLabelsPage;