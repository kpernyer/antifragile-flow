
import { createBrowserRouter } from 'react-router-dom';
import Onboarding from './pages/Onboarding';
import Inbox from './pages/Inbox';
import Workflows from './pages/Workflows';
import Users from './pages/Users';
import Organization from './pages/Organization';
import App from './App';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: 'onboarding',
        element: <Onboarding />,
      },
      {
        path: 'inbox',
        element: <Inbox />,
      },
      {
        path: 'workflows',
        element: <Workflows />,
      },
      {
        path: 'users',
        element: <Users />,
      },
      {
        path: 'organization',
        element: <Organization />,
      },
    ],
  },
]);

export default router;
