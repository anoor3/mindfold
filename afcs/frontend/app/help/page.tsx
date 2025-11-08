export default function HelpPage() {
  return (
    <div className="glassy space-y-6 p-8">
      <h1 className="text-3xl font-bold">Help & glossary</h1>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">How AFCS works</h2>
        <p className="text-sm opacity-75">
          AFCS processes your CSV locally, infers column types, handles missing values, and optionally one-hot encodes categorical features. Choose PCA or Autoencoder for compression, then download latent representations and reproducible artifacts.
        </p>
      </section>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Privacy</h2>
        <p className="text-sm opacity-75">
          All uploads stay on your machine. AFCS never sends data to third parties.
        </p>
      </section>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Glossary</h2>
        <ul className="space-y-2 text-sm">
          <li><strong>PCA</strong> — Principal Component Analysis, a linear dimensionality reduction method.</li>
          <li><strong>Autoencoder</strong> — Neural network that learns to reconstruct inputs through a compact latent bottleneck.</li>
          <li><strong>Reconstruction error</strong> — Average difference between original and reconstructed samples.</li>
          <li><strong>Feature importance</strong> — AFCS scoring combining variance, PCA loadings, and redundancy penalties.</li>
        </ul>
      </section>
    </div>
  );
}
