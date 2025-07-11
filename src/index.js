import React from 'react';
import { createRoot } from 'react-dom/client';
import Example from './Example.tsx';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(React.createElement(Example));