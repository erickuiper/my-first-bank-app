import { createRoot } from 'react-dom/client';
// eslint-disable-next-line no-unused-vars
import App from './App.web';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
