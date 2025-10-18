import { useState } from 'react';
import { 
  LayoutDashboard, 
  Building2, 
  Search, 
  Menu, 
  X 
} from 'lucide-react';
import Dashboard from './components/Dashboard';
import AccommodationsList from './components/AccommodationsList';
import Scanner from './components/Scanner';

const App = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { id: 'accommodations', name: 'Accommodations', icon: Building2 },
    { id: 'scanner', name: 'Scanner', icon: Search },
  ];

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'accommodations':
        return <AccommodationsList />;
      case 'scanner':
        return <Scanner />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 
                   lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-white 
                     shadow-lg transform transition-transform 
                     duration-300 ease-in-out lg:translate-x-0 
                     ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-6 
                       border-b">
          <h1 className="text-xl font-bold text-primary-600">
            MyTravel AI
          </h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <nav className="p-4 space-y-2">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setCurrentView(item.id);
                setSidebarOpen(false);
              }}
              className={`w-full flex items-center px-4 py-3 
                       rounded-lg transition-colors ${
                currentView === item.id
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <div className="sticky top-0 z-10 flex items-center h-16 px-6 
                       bg-white border-b lg:hidden">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="ml-4 text-xl font-bold text-primary-600">
            MyTravel AI
          </h1>
        </div>
        <main className="p-6 lg:p-8">
          {renderView()}
        </main>
      </div>
    </div>
  );
};

export default App;