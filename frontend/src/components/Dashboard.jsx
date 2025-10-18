import { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  MapPin, 
  Building2 
} from 'lucide-react';
import { analyticsService } from '../services/api';

const StatCard = ({ title, value, icon: Icon, color }) => (
  <div className="card">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600 mb-1">{title}</p>
        <p className="text-3xl font-bold">{value}</p>
      </div>
      <div className={`p-3 rounded-full ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await analyticsService.getDashboard();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Dashboard
        </h1>
        <p className="text-gray-600 mt-1">
          Overview of accommodation data collection
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 
                     lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Accommodations"
          value={analytics?.total_accommodations || 0}
          icon={Building2}
          color="bg-blue-500"
        />
        <StatCard
          title="Hot Leads"
          value={analytics?.hot_leads || 0}
          icon={TrendingUp}
          color="bg-green-500"
        />
        <StatCard
          title="Regions"
          value={Object.keys(analytics?.by_region || {}).length}
          icon={MapPin}
          color="bg-purple-500"
        />
        <StatCard
          title="Categories"
          value={Object.keys(analytics?.by_type || {}).length}
          icon={Activity}
          color="bg-orange-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            By Region
          </h3>
          <div className="space-y-3">
            {Object.entries(analytics?.by_region || {}).map(
              ([region, count]) => (
                <div key={region} 
                     className="flex items-center justify-between">
                  <span className="text-gray-700">{region}</span>
                  <span className="font-semibold text-primary-600">
                    {count}
                  </span>
                </div>
              )
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            By Type
          </h3>
          <div className="space-y-3">
            {Object.entries(analytics?.by_type || {}).map(
              ([type, count]) => (
                <div key={type} 
                     className="flex items-center justify-between">
                  <span className="text-gray-700 capitalize">
                    {type.replace(/_/g, ' ')}
                  </span>
                  <span className="font-semibold text-primary-600">
                    {count}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;