export default function Footer() {
  return (
    <footer className="bg-cmrBlue text-white pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-8 grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        <div>
          <h2 className="text-2xl font-bold mb-4">CMR Logo</h2>
          <p className="text-sm border border-white inline-block px-4 py-2 rounded-full mb-4">CENTRE D'APPEL<br/><span className="text-lg font-bold">0537 567 567</span></p>
          <p className="text-sm">Avenue Al Araar Hay Riad - B.P 2048 Rabat - 10.113</p>
          <p className="text-sm mt-4 underline cursor-pointer">Adresses des délégations régionales</p>
        </div>
        
        <div className="space-y-4 text-sm font-semibold">
          <a href="#" className="block hover:underline">Charte des services</a>
          <a href="#" className="block hover:underline">Guides & Brochures</a>
          <a href="#" className="block hover:underline">Pièces à fournir</a>
          <a href="#" className="block hover:underline">Formulaires</a>
        </div>

        <div className="space-y-4 text-sm font-semibold">
          <a href="#" className="block hover:underline">Maw3idi</a>
          <a href="#" className="block hover:underline">Chikaya</a>
          <a href="#" className="block hover:underline">Bureau d'ordre digital</a>
        </div>

        <div className="space-y-4 text-sm font-semibold">
          <a href="#" className="block hover:underline">E-Retraite</a>
          <a href="#" className="block hover:underline">Portail partenaire</a>
          <a href="#" className="block hover:underline">Portail RH</a>
          <a href="#" className="block hover:underline">Espace Fournisseurs</a>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-8 border-t border-blue-400 pt-8 flex justify-center space-x-6 text-sm">
        <a href="#" className="hover:underline">Plan du site</a>
        <a href="#" className="hover:underline">Mentions légales</a>
        <span>© Copyright CMR 2024</span>
      </div>
    </footer>
  );
}
