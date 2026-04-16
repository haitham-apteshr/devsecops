import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="flex-grow bg-white">
        {/* Banner Section */}
        <section className="relative h-96 bg-gray-500 overflow-hidden flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-30 z-10"></div>
            <div className="relative z-20 text-center text-white">
                <h1 className="text-5xl font-bold mb-4 drop-shadow-md">Caisse Marocaine des Retraites</h1>
                <p className="text-2xl italic font-serif drop-shadow-md">La Retraite du Secteur Public</p>
            </div>
        </section>

        {/* Action Banner */}
        <section className="flex border-b border-gray-200 h-20 shadow-md">
            <div className="flex-1 bg-cmrBlue text-white flex items-center justify-center cursor-pointer hover:bg-blue-700 transition">
                <span className="text-lg font-semibold tracking-wider">SE CONNECTER</span>
            </div>
            <div className="flex-1 bg-white text-cmrBlue flex items-center justify-center cursor-pointer hover:bg-gray-50 transition border-r border-gray-200">
                <span className="text-lg font-semibold tracking-wider">S'INSCRIRE</span>
            </div>
            <div className="flex-1 bg-white text-cmrBlue flex items-center justify-center cursor-pointer hover:bg-gray-50 transition">
                <span className="text-lg font-semibold tracking-wider">S'INFORMER</span>
            </div>
        </section>

        {/* Mon Parcours Section */}
        <section className="max-w-7xl mx-auto py-16 px-8">
            <h2 className="text-2xl font-bold mb-2">MON PARCOURS</h2>
            <div className="w-24 h-1 bg-cmrBlue mb-4"></div>
            <p className="text-gray-600 mb-8">Accédez à tous les services et infos pratiques selon votre situation</p>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {['ACTIF', 'RETRAITÉ', 'AYANTS-CAUSE', 'ATTAKMILI'].map((title, i) => (
                    <div key={i} className="h-64 rounded-xl overflow-hidden relative group cursor-pointer shadow-lg bg-gray-200">
                        <div className="absolute inset-0 bg-cmrBlue opacity-20 group-hover:opacity-10 transition"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <h3 className="text-white text-xl font-bold tracking-wider drop-shadow-lg">{title}</h3>
                        </div>
                    </div>
                ))}
            </div>
        </section>

        {/* Nos Services Section */}
        <section className="max-w-7xl mx-auto py-8 px-8 bg-white">
            <h2 className="text-2xl font-bold mb-2">NOS SERVICES</h2>
            <div className="w-24 h-1 bg-cmrBlue mb-4"></div>
            <p className="text-gray-600 mb-8">Services à accès libre</p>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { title: "Prendre un rendez-vous" },
                    { title: "Authentifier une attestation" },
                    { title: "Demander une pension d'ayant cause" },
                    { title: "Autres services" }
                ].map((item, i) => (
                    <div key={i} className="border border-gray-200 rounded-xl p-8 flex flex-col items-center text-center hover:shadow-xl transition h-48 justify-center cursor-pointer bg-white">
                        <div className="w-16 h-16 bg-blue-50 text-cmrBlue rounded-full flex items-center justify-center mb-4">
                            Icon
                        </div>
                        <h4 className="font-semibold text-gray-800">{item.title}</h4>
                    </div>
                ))}
            </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
