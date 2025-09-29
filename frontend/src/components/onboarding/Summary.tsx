import React from 'react';

interface SummaryProps {
  summary: string;
}

const Summary: React.FC<SummaryProps> = ({ summary }) => {
  return (
    <div>
      <h2>Onboarding Complete: CIA Factbook Summary</h2>
      <pre style={{ whiteSpace: 'pre-wrap', background: '#f4f4f4', padding: '15px', borderRadius: '4px' }}>
        {summary}
      </pre>
    </div>
  );
};

export default Summary;
