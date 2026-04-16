import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function About() {
  return (
    <>
      <Navbar />
      <main className="flex-grow bg-white">
        {/* Banner Section */}
        <section 
            className="relative h-96 bg-gray-500 overflow-hidden flex items-center justify-center bg-cover bg-center"
            style={{ backgroundImage: "url('/images/about.png')" }}
        >
            <div className="absolute inset-0 bg-black opacity-50 z-10"></div>
            <div className="relative z-20 text-center text-white p-4">
                <h1 className="text-5xl font-bold mb-4 drop-shadow-md">À Propos de Nous</h1>
                <p className="text-2xl font-serif drop-shadow-md">Une institution dédiée au service public</p>
            </div>
        </section>

        {/* Content Section */}
        <section className="max-w-7xl mx-auto py-16 px-8 flex flex-col md:flex-row gap-12">
            <div className="w-full md:w-1/2">
                <h2 className="text-3xl font-bold mb-6 text-cmrBlue">Notre Mission</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Depuis sa création, la Caisse a toujours veillé à la gestion optimale des droits à la retraite 
                    et à l'accompagnement continu des bénéficiaires tout au long de leur vie.
                </p>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Notre institution combine l'innovation technologique avec un service humain de qualité pour 
                    offrir des prestations modernes, rapides et entièrement sécurisées.
                </p>
            </div>
            
            <div className="w-full md:w-1/2 bg-gray-100 p-8 rounded-xl shadow-inner border border-gray-200">
                <h3 className="text-xl font-bold mb-4 text-gray-800">Nos Valeurs Fondamentales</h3>
                <ul className="space-y-4">
                    <li className="flex items-center">
                        <div className="w-4 h-4 bg-cmrOrange rounded-full mr-4"></div>
                        <span className="font-semibold text-gray-800">Transparence et Équité</span>
                    </li>
                    <li className="flex items-center">
                        <div className="w-4 h-4 bg-cmrOrange rounded-full mr-4"></div>
                        <span className="font-semibold text-gray-800">Innovation Continue</span>
                    </li>
                    <li className="flex items-center">
                        <div className="w-4 h-4 bg-cmrOrange rounded-full mr-4"></div>
                        <span className="font-semibold text-gray-800">Engagement envers nos affiliés</span>
                    </li>
                    <li className="flex items-center">
                        <div className="w-4 h-4 bg-cmrOrange rounded-full mr-4"></div>
                        <span className="font-semibold text-gray-800">Responsabilité Sociale</span>
                    </li>
                </ul>
            </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
