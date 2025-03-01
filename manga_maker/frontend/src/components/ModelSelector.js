// components/ModelSelector.js
import React, { useState, useEffect } from 'react';

const ModelSelector = ({ onModelSelected, userTier }) => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchAvailableModels();
  }, [userTier]);
  
  const fetchAvailableModels = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/models?tier=${userTier}`);
      const data = await response.json();
      setModels(data.models);
      
      // Select first available model as default
      if (data.models.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0].id);
        onModelSelected(data.models[0].id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching models:', error);
      setLoading(false);
    }
  };
  
  const handleModelChange = (e) => {
    const modelId = e.target.value;
    setSelectedModel(modelId);
    onModelSelected(modelId);
  };
  
  return (
    <div className="model-selector">
      <h3>Select AI Model</h3>
      {loading ? (
        <p>Loading available models...</p>
      ) : (
        <>
          <select value={selectedModel || ''} onChange={handleModelChange}>
            <option value="" disabled>Select a model</option>
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} {model.premium && '⭐'}
              </option>
            ))}
          </select>
          {selectedModel && models.find(m => m.id === selectedModel)?.description && (
            <p className="model-description">
              {models.find(m => m.id === selectedModel).description}
            </p>
          )}
        </>
      )}
    </div>
  );
};

export default ModelSelector;