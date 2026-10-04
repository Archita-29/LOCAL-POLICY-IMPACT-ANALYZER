import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import './mockData'  // Uncomment only if running frontend standalone without backend
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
