import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Dashboard() {
  const [appointments, setAppointments] = useState([]);
  const [services, setServices] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [preferences, setPreferences] = useState('');
  const [importMessage, setImportMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return navigate('/login');

    const fetchData = async () => {
      try {
        const url = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
        const headers = { Authorization: `Bearer ${token}` };
        
        const [appRes, servRes] = await Promise.all([
            axios.get(`${url}/appointments`, { headers }),
            axios.get(`${url}/appointments/services`, { headers })
        ]);
        setAppointments(appRes.data.data);
        setServices(servRes.data.data);
      } catch (err) {
        if (err.response && err.response.status === 401) {
            localStorage.removeItem('token');
            navigate('/login');
        }
      }
    };
    fetchData();
  }, [navigate]);

  const url = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  const getHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('token')}` });

  // Normal functionality with hidden SQLi
  const handleSearch = async (e) => {
      e.preventDefault();
      try {
          const res = await axios.get(`${url}/appointments/search?query=${searchQuery}`, { headers: getHeaders() });
          setSearchResults(res.data.data);
      } catch (err) { console.error(err); }
  };

  // Normal functionality with hidden IDOR
  const viewDetails = async (id) => {
      try {
          const res = await axios.get(`${url}/appointments/${id}`, { headers: getHeaders() });
          setSelectedAppointment(res.data.data);
      } catch (err) { alert("Erreur d'accès"); }
  };

  // Normal functionality with hidden Deserialization
  const handleImport = async (e) => {
      e.preventDefault();
      try {
          const res = await axios.post(`${url}/user/preferences`, { preferences }, { headers: getHeaders() });
          setImportMessage("Préférences importées avec succès.");
      } catch (err) { setImportMessage("Échec de l'importation."); }
  };

  // Normal functionality with hidden File Upload Vulnerability
  const handleUpload = async (e) => {
      e.preventDefault();
      if (!selectedFile) return;
      const formData = new FormData();
      formData.append('document', selectedFile);
      try {
          const res = await axios.post(`${url}/user/upload`, formData, { headers: getHeaders() });
          setUploadMessage("Document transmis pour vérification.");
      } catch (err) { setUploadMessage("Erreur d'envoi."); }
  };

  return (
    <>
      <Navbar />
      <div className="flex-grow bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-8 text-cmrBlue">Espace Personnel</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            
            {/* Appointments Section */}
            <div className="bg-white shadow rounded-lg p-6 border-t-4 border-cmrBlue">
                <div className="flex justify-between mb-4">
                    <h2 className="text-xl font-bold">Mes Rendez-vous</h2>
                    <form onSubmit={handleSearch} className="flex gap-2">
                        <input type="text" className="border px-2 py-1 text-sm rounded" placeholder="Rechercher statut..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
                        <button type="submit" className="bg-gray-200 px-3 py-1 rounded text-sm hover:bg-gray-300">Rechercher</button>
                    </form>
                </div>

                <ul className="divide-y divide-gray-200">
                    {(searchResults.length > 0 ? searchResults : appointments).map(app => (
                        <li key={app.id} className="py-4 flex justify-between items-center">
                            <div>
                                <p className="font-semibold cursor-pointer hover:underline text-cmrBlue" onClick={() => viewDetails(app.id)}>
                                    Rendez-vous #{app.id}
                                </p>
                                <p className="text-sm text-gray-500">{new Date(app.appointment_date).toLocaleDateString()}</p>
                            </div>
                            <span className="text-sm text-gray-600">{app.status}</span>
                        </li>
                    ))}
                </ul>

                {selectedAppointment && (
                    <div className="mt-4 p-4 bg-gray-100 rounded text-sm">
                        <p><strong>Détails pour ID #{selectedAppointment.id}:</strong></p>
                        <p>Date: {new Date(selectedAppointment.appointment_date).toLocaleString()}</p>
                        <p>Statut: {selectedAppointment.status}</p>
                        <button onClick={() => setSelectedAppointment(null)} className="mt-2 text-red-500 underline text-xs">Fermer</button>
                    </div>
                )}
            </div>

            {/* Profile Settings Section */}
            <div className="bg-white shadow rounded-lg p-6 border-t-4 border-cmrOrange flex flex-col gap-8">
                
                <div>
                    <h2 className="text-xl font-bold mb-4">Uploader Document Identité</h2>
                    <form onSubmit={handleUpload} className="flex gap-2">
                        <input type="file" className="border px-4 py-2 w-full rounded text-sm" onChange={e => setSelectedFile(e.target.files[0])} />
                        <button type="submit" className="bg-cmrBlue text-white px-4 py-2 rounded text-sm font-bold">Envoyer</button>
                    </form>
                    {uploadMessage && <p className="text-xs text-green-600 mt-2">{uploadMessage}</p>}
                </div>

                <div>
                    <h2 className="text-xl font-bold mb-4">Importer Préférences (JSON)</h2>
                    <form onSubmit={handleImport} className="flex flex-col gap-2">
                        <textarea className="border px-4 py-2 w-full rounded text-sm h-20" placeholder='Ex: {"theme": "dark"}' value={preferences} onChange={e => setPreferences(e.target.value)}></textarea>
                        <button type="submit" className="bg-cmrBlue text-white px-4 py-2 rounded text-sm font-bold self-start">Sauvegarder</button>
                    </form>
                    {importMessage && <p className="text-xs text-green-600 mt-2">{importMessage}</p>}
                </div>

            </div>
        </div>
      </div>
      <Footer />
    </>
  );
}
