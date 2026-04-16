import { Link } from 'react-router-dom';
import { Search, User } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm py-4 px-8 flex justify-between items-center border-t-4 border-cmrBlue">
      <div className="flex items-center space-x-6">
        <Link to="/" className="text-2xl font-bold text-gray-800">
          CMR Logo
        </Link>
        <div className="hidden md:flex space-x-6 text-sm font-semibold text-gray-700">
          <Link to="/" className="hover:text-cmrBlue pb-2 border-b-2 border-transparent hover:border-cmrBlue transition-all">LA CMR</Link>
          <Link to="/about" className="hover:text-cmrBlue pb-2 border-b-2 border-transparent hover:border-cmrBlue transition-all">À PROPOS</Link>
          <Link to="/contact" className="hover:text-cmrBlue pb-2 border-b-2 border-transparent hover:border-cmrBlue transition-all">CONTACT</Link>
          <a href="#" className="hover:text-cmrBlue pb-2 border-b-2 border-transparent hover:border-cmrBlue transition-all">ESERVICES</a>
        </div>
      </div>
      
      <div className="flex items-center space-x-6 text-sm font-semibold">
        <a href="#" className="hover:text-cmrBlue">AIDE ET CONTACT</a>
        <div className="bg-gray-200 p-2 rounded-full cursor-pointer hover:bg-gray-300">
          <Search size={18} />
        </div>
        <span>A+</span>
        <span>FR | E</span>
        <Link to="/login" className="bg-cmrBlue text-white px-4 py-2 flex items-center space-x-2 rounded-md hover:bg-blue-700 transition">
          <User size={18} />
          <span>SE CONNECTER</span>
        </Link>
      </div>
    </nav>
  );
}
