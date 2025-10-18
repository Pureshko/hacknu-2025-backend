import { useState } from 'react';
import { Search, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../services/api';

const Scanner = () => {
  const [selectedRegion, setSelectedRegion] = useState('Almaty');
  const [dataSource, setDataSource] = useState('2gis');
  const [scanning, setScanning] = useState(false);
  const [status, setStatus] = useState(null);

  const regions = [
    'Almaty',
    'Astana',
    'Karaganda',
    'Shymkent',
    'Aktau',
  ];

  const handleScan = async () => {
    setScanning(true);
    setStatus(null);

    try {
      const endpoint =
        dataSource === 'google'
          ? '/api/scan/google-places'
          : '/api/scan/start';

      await api.post(endpoint, null, {
        params: { region: selectedRegion },
      });

      setStatus({
        type: 'success',
        message: `Scan started for ${selectedRegion} using ${dataSource}.`,
      });
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Failed to start scan.',
      });
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Data Scanner</h1>
        <p className="text-gray-600 mt-1">
          Scan regions for new accommodation data
        </p>
      </div>

      <div className="card max-w-2xl">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source
            </label>
            <select
              value={dataSource}
              onChange={(e) => setDataSource(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 
                       rounded-lg focus:ring-2 focus:ring-primary-500"
              disabled={scanning}
            >
              <option value="2gis">2GIS</option>
              <option value="google">Google Places</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Region
            </label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 
                       rounded-lg focus:ring-2 focus:ring-primary-500 
                       focus:border-transparent"
              disabled={scanning}
            >
              {regions.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleScan}
            disabled={scanning}
            className="btn btn-primary w-full flex items-center 
                     justify-center text-lg py-3 disabled:opacity-50 
                     disabled:cursor-not-allowed"
          >
            {scanning ? (
              <>
                <div
                  className="animate-spin rounded-full h-5 w-5 
                             border-b-2 border-white mr-2"
                ></div>
                Scanning...
              </>
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                Start Scan
              </>
            )}
          </button>

          {status && (
            <div
              className={`p-4 rounded-lg flex items-start ${
                status.type === 'success'
                  ? 'bg-green-50 text-green-800'
                  : 'bg-red-50 text-red-800'
              }`}
            >
              {status.type === 'success' ? (
                <CheckCircle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              )}
              <p>{status.message}</p>
            </div>
          )}

          <div className="border-t pt-6">
            <h3 className="font-semibold text-gray-900 mb-3">
              What happens during a scan?
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                Search {dataSource === 'google' ? 'Google Places' : '2GIS'} for
                accommodations
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                Collect contact information and business details
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                Calculate priority scores and lead status
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                Generate AI descriptions for each accommodation
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scanner;