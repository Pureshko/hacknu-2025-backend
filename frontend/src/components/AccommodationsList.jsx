import { useState, useEffect } from 'react';
import { 
  Search, 
  Download, 
  Eye, 
  MapPin, 
  Phone,
  ExternalLink 
} from 'lucide-react';
import { accommodationService } from '../services/api';

const AccommodationCard = ({ accommodation, onViewDetails }) => {
  const getLeadBadgeColor = (status) => {
    switch (status) {
      case 'hot':
        return 'bg-red-100 text-red-800';
      case 'warm':
        return 'bg-yellow-100 text-yellow-800';
      case 'cold':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {accommodation.name}
          </h3>
          <div className="flex items-center text-gray-600 text-sm mb-2">
            <MapPin className="w-4 h-4 mr-1" />
            {accommodation.address || accommodation.region}
          </div>
          {accommodation.phone && (
            <div className="flex items-center text-gray-600 text-sm">
              <Phone className="w-4 h-4 mr-1" />
              {accommodation.phone}
            </div>
          )}
        </div>
        <span className={`px-3 py-1 rounded-full text-xs 
                        font-semibold ${getLeadBadgeColor(
                          accommodation.lead_status
                        )}`}>
          {accommodation.lead_status?.toUpperCase()}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <p className="text-xs text-gray-500">Priority Score</p>
            <p className="text-lg font-bold text-primary-600">
              {accommodation.priority_score?.toFixed(1) || 'N/A'}
            </p>
          </div>
          {accommodation.rating && (
            <div>
              <p className="text-xs text-gray-500">Rating</p>
              <p className="text-lg font-bold text-yellow-600">
                ⭐ {accommodation.rating}
              </p>
            </div>
          )}
        </div>
        <div className="flex space-x-2">
          {accommodation.website && (
            <a
              href={accommodation.website}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-gray-600 hover:text-primary-600"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
          )}
          <button
            onClick={() => onViewDetails(accommodation.id)}
            className="btn btn-primary"
          >
            <Eye className="w-4 h-4 mr-1 inline" />
            View
          </button>
        </div>
      </div>
    </div>
  );
};

const AccommodationsList = ({ onViewDetails }) => {
  const [accommodations, setAccommodations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [regionFilter, setRegionFilter] = useState('');

  useEffect(() => {
    loadAccommodations();
  }, [regionFilter]);

  const loadAccommodations = async () => {
    try {
      const params = regionFilter ? { region: regionFilter } : {};
      const response = await accommodationService.getAll(params);
      setAccommodations(response.data.items || []);
    } catch (error) {
      console.error('Error loading accommodations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await accommodationService.exportCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'accommodations.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting:', error);
    }
  };

  const filteredAccommodations = accommodations.filter(acc =>
    acc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 
                       border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Accommodations
        </h1>
        <button
          onClick={handleExport}
          className="btn btn-secondary flex items-center"
        >
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform 
                           -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search accommodations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 
                     rounded-lg focus:ring-2 focus:ring-primary-500 
                     focus:border-transparent"
          />
        </div>
        <select
          value={regionFilter}
          onChange={(e) => setRegionFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-primary-500 
                   focus:border-transparent"
        >
          <option value="">All Regions</option>
          <option value="Almaty">Almaty</option>
          <option value="Astana">Astana</option>
          <option value="Karaganda">Karaganda</option>
          <option value="Shymkent">Shymkent</option>
          <option value="Aktau">Aktau</option>
        </select>
      </div>

      {filteredAccommodations.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            No accommodations found
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredAccommodations.map((accommodation) => (
            <AccommodationCard
              key={accommodation.id}
              accommodation={accommodation}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default AccommodationsList;