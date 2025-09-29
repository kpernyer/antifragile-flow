import React from 'react';

interface Step2Props {
  onComplete: () => void;
}

const Step2: React.FC<Step2Props> = ({ onComplete }) => {
  return (
    <div>
      <h2>Step 2: Website Scraping</h2>
      <p>Enter your company's website URL to begin scraping for terminology.</p>
      <input type="text" placeholder="https://example.com" style={{ width: '300px', padding: '8px' }} />
      <button onClick={onComplete} style={{ marginLeft: '10px', padding: '8px' }}>Start Scraping</button>
    </div>
  );
};

export default Step2;
