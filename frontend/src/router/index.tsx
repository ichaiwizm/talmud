import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '../components/layout';
import { Dashboard } from '../pages/Dashboard';
import { BooksPage, BookDetail, ChapterView } from '../pages/books';
import { NamesPage, NameDetail } from '../pages/names';
import { SearchPage } from '../pages/SearchPage';
import { GematriaPage } from '../pages/GematriaPage';
import { StatsPage } from '../pages/StatsPage';
import { GraphPage } from '../pages/GraphPage';
import { AdminPage } from '../pages/AdminPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'books', element: <BooksPage /> },
      { path: 'books/:book', element: <BookDetail /> },
      { path: 'books/:book/:chapter', element: <ChapterView /> },
      { path: 'names', element: <NamesPage /> },
      { path: 'names/:name', element: <NameDetail /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'gematria', element: <GematriaPage /> },
      { path: 'stats', element: <StatsPage /> },
      { path: 'graph', element: <GraphPage /> },
      { path: 'admin', element: <AdminPage /> },
    ],
  },
]);
