import { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Contact() {
  const [search, setSearch] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  
  const [ip, setIp] = useState('');
  const [pingResult, setPingResult] = useState('');

  const url = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

  const handleSearch = async (e) => {
      e.preventDefault();
      try {
          const res = await axios.get(`${url}/contact/faq?search=${encodeURIComponent(search)}`);
          setHtmlContent(res.data);
      } catch (err) { console.error(err); }
  };

  const handlePing = async (e) => {
      e.preventDefault();
      try {
          const res = await axios.post(`${url}/contact/status`, { server_ip: ip });
          setPingResult(res.data.output);
      } catch (err) {
          setPingResult("Impossible d'atteindre le serveur cible.");
      }
  };

  return (
    <>
      <Navbar />
      <main className="flex-grow bg-white">
        <section 
            className="relative h-80 bg-gray-500 overflow-hidden flex items-center justify-center bg-cover bg-center"
            style={{ backgroundImage: "url('/images/contact.png')" }}
        >
            <div className="absolute inset-0 bg-cmrBlue opacity-60 z-10 transition"></div>
            <div className="relative z-20 text-center text-white">
                <h1 className="text-5xl font-bold mb-4 drop-shadow-md px-4">Contactez-nous</h1>
            </div>
        </section>

        <section className="max-w-7xl mx-auto py-16 px-8 grid grid-cols-1 md:grid-cols-2 gap-16">
            
            {/* FAQ Search with XSS (Looks Normal) */}
            <div>
                <h2 className="text-3xl font-bold mb-6 text-cmrBlue">Recherche dans la FAQ</h2>
                <p className="text-gray-700 leading-relaxed mb-6">Recherchez une réponse parmi nos documents publics.</p>
                
                <form className="space-y-4" onSubmit={handleSearch}>
                    <div className="flex gap-2">
                        <input 
                            type="text" 
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-cmrBlue" 
                            placeholder="Entrez votre question..." 
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <button className="bg-cmrBlue text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700">Chercher</button>
                    </div>
                </form>
                {htmlContent && (
                    <div className="mt-4 p-4 bg-gray-50 border rounded text-sm text-gray-800" dangerouslySetInnerHTML={{ __html: htmlContent }} />
                )}

                <div className="mt-12">
                    <h3 className="text-xl font-bold mb-4 text-gray-800">Serveur & Stabilité</h3>
                    <p className="text-sm text-gray-600 mb-4">Si vous rencontrez des lenteurs, utilisez notre outil de diagnostic pour vérifier la latence avec votre serveur local.</p>
                    <form className="flex gap-2" onSubmit={handlePing}>
                        <input type="text" className="border border-gray-300 px-4 py-2 w-full rounded" placeholder="Votre IP (ex: 8.8.8.8)" value={ip} onChange={e => setIp(e.target.value)} />
                        <button type="submit" className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-black">Vérifier</button>
                    </form>
                    {pingResult && (
                        <pre className="mt-4 bg-gray-100 p-4 rounded text-xs border overflow-auto text-gray-800 max-h-32">
                            {pingResult}
                        </pre>
                    )}
                </div>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <h3 className="text-2xl font-bold mb-6 text-gray-800">Formulaire de Message</h3>
                <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Nom complet</label>
                        <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="Votre nom..." />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Adresse Email</label>
                        <input type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="Email@exemple.com" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                        <textarea rows="4" className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="Comment pouvons-nous vous aider ?"></textarea>
                    </div>
                    <button className="w-full bg-cmrOrange text-white font-bold py-3 px-4 rounded-lg hover:bg-orange-600">
                        Envoyer
                    </button>
                </form>
            </div>
            
        </section>
      </main>
      <Footer />
    </>
  );
}
