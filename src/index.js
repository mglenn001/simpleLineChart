import React from 'react';
import { createRoot } from 'react-dom/client';
import Example from './Example';
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<Example />);