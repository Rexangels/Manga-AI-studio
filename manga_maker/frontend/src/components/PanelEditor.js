// components/PanelEditor.js
import React, { useState } from 'react';

const PanelEditor = ({ panel, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [prompt, setPrompt] = useState(panel.prompt || '');
  const [isRegenerating, setIsRegenerating] = useState(false);
  
  const handleRegenerateImage = async () => {
    setIsRegenerating(true);
    try {
      const response = await fetch(`/api/panels/${panel.id}/regenerate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      
      const data = await response.json();
      onUpdate({
        ...panel,
        imageUrl: data.imageUrl,
        prompt: prompt
      });
    } catch (error) {
      console.error('Error regenerating panel:', error);
    } finally {
      setIsRegenerating(false);
      setIsEditing(false);
    }
  };
  
  return (
    <div className="panel-editor">
      <div className="panel-image">
        {isRegenerating ? (
          <div className="regenerating-overlay">
            <span>Generating...</span>
          </div>
        ) : null}
        <img src={panel.imageUrl} alt={`Panel ${panel.id}`} />
      </div>
      
      <div className="panel-controls">
        {isEditing ? (
          <>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Modify image prompt..."
            />
            <div className="button-group">
              <button onClick={() => setIsEditing(false)}>Cancel</button>
              <button 
                onClick={handleRegenerateImage}
                disabled={isRegenerating}
              >
                Regenerate
              </button>
            </div>
          </>
        ) : (
          <button onClick={() => setIsEditing(true)}>
            Edit Prompt
          </button>
        )}
      </div>
    </div>
  );
};

export default PanelEditor;