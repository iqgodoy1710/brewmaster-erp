import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";

import "../App.css";
import { apiGet } from "../lib/api";
import type { Keg, PackagingFormat } from "../types/api";

const formatVolume = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function KegQrLabelPage() {
  const { code } = useParams();

  const [keg, setKeg] = useState<Keg | null>(null);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadLabel() {
      if (!code) {
        setError("El código del barril no es válido.");
        return;
      }

      try {
        const [kegData, formatsData] = await Promise.all([
          apiGet<Keg>(`/kegs/by-code/${encodeURIComponent(code)}`),
          apiGet<PackagingFormat[]>("/packaging-formats/"),
        ]);

        setKeg(kegData);
        setFormats(formatsData);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudo generar la etiqueta.",
        );
      }
    }

    void loadLabel();
  }, [code]);

  const packagingFormat = useMemo(
    () =>
      formats.find(
        (format) => format.id === keg?.packaging_format_id,
      ) ?? null,
    [formats, keg],
  );

  const qrUrl = keg
    ? `${window.location.origin}/barriles/qr/${encodeURIComponent(keg.code)}`
    : "";

  return (
    <main className="dashboard qr-label-page">
      <section className="page-heading print-hidden">
        <p className="eyebrow">Barriles</p>
        <h1>Etiqueta QR</h1>
        <p>Imprimí la etiqueta y adherila al barril correspondiente.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {keg && (
        <>
          <section className="panel qr-label">
            <QRCodeSVG
              bgColor="#ffffff"
              fgColor="#172033"
              level="M"
              marginSize={2}
              size={230}
              value={qrUrl}
            />

            <div>
              <h2>{keg.code}</h2>
              <p>
                {packagingFormat
                  ? `${packagingFormat.name} · ${formatVolume(
                      packagingFormat.capacity_liters,
                    )} L`
                  : "Formato no disponible"}
              </p>
              <p>Variante: {keg.form_factor}</p>
              <p className="form-help">
                Escaneá para gestionar este barril desde el celular.
              </p>
            </div>
          </section>

          <button
            className="print-hidden"
            onClick={() => window.print()}
            type="button"
          >
            Imprimir etiqueta
          </button>
        </>
      )}
    </main>
  );
}

export default KegQrLabelPage;