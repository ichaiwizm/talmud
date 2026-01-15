import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="min-h-screen bg-ink texture-overlay">
      <div className="flex">
        <Sidebar />
        <div className="flex-1 min-h-screen flex flex-col lg:ml-0">
          <Header />
          <main className="flex-1 p-6 lg:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
