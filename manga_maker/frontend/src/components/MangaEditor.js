import React, { useState } from 'react';

const MangaEditor = () => {
  const [narrative, setNarrative] = useState('');
  const [panelCount, setPanelCount] = useState(4);
  const [selectedModel, setSelectedModel] = useState('anime-v2');
  const [isGenerating, setIsGenerating] = useState(false);
  const [panels, setPanels] = useState([]);
  
  // Mock models available based on subscription tier
  const availableModels = [
    { id: 'anime-v1', name: 'Anime Basic', tier: 'FREE' },
    { id: 'anime-v2', name: 'Anime Pro v2', tier: 'BASIC' },
    { id: 'manga-realistic', name: 'Manga Realistic', tier: 'PRO' },
    { id: 'custom-finetuned', name: 'Custom Studio Style', tier: 'ENTERPRISE' }
  ];
  
  // Mock user's current tier
  const userTier = 'BASIC';
  
  const filteredModels = availableModels.filter(model => {
    const tierValues = { 'FREE': 0, 'BASIC': 1, 'PRO': 2, 'ENTERPRISE': 3 };
    return tierValues[model.tier] <= tierValues[userTier];
  });
  
  const generateManga = () => {
    setIsGenerating(true);
    
    // Simulate API call delay
    setTimeout(() => {
      const generatedPanels = Array(panelCount).fill().map((_, i) => ({
        id: i,
        imageUrl: `/api/placeholder/240/240`,
        description: `Panel ${i+1}: Generated from narrative`,
        dialogues: []
      }));
      
      setPanels(generatedPanels);
      setIsGenerating(false);
    }, 2000);
  };
  
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gray-800 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">MangaAI Studio</h1>
          <div className="flex items-center space-x-4">
            <span className="px-2 py-1 bg-indigo-600 rounded text-xs">BASIC TIER</span>
            <button className="px-3 py-1 bg-indigo-500 rounded text-sm">Upgrade</button>
            <button className="p-2 rounded-full bg-gray-700">
              <span className="sr-only">User menu</span>
              <div className="h-6 w-6 rounded-full bg-gray-500"></div>
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-grow container mx-auto p-4 flex">
        {/* Sidebar */}
        <div className="w-64 bg-white rounded-lg shadow-sm p-4 mr-4">
          <h2 className="font-medium mb-4">Projects</h2>
          <button className="w-full py-2 bg-indigo-500 text-white rounded mb-4">
            New Project
          </button>
          
          <div className="space-y-2">
            <div className="p-3 border rounded hover:bg-gray-50 cursor-pointer transition">
              <h3 className="font-medium">My Hero Story</h3>
              <p className="text-xs text-gray-500">Last edited: 2 days ago</p>
            </div>
            <div className="p-3 border rounded hover:bg-gray-50 cursor-pointer transition">
              <h3 className="font-medium">School Adventure</h3>
              <p className="text-xs text-gray-500">Last edited: 1 week ago</p>
            </div>
          </div>
        </div>
        
        {/* Editor */}
        <div className="flex-grow bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Create New Manga</h2>
          
          {/* Narrative Input */}
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Your Narrative or Dialogue</label>
            <textarea 
              className="w-full p-3 border rounded-lg h-32"
              placeholder="Enter your story or dialogue here..."
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
            ></textarea>
          </div>
          
          {/* Configuration Options */}
          <div className="flex space-x-4 mb-6">
            <div className="flex-1 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-2">Panel Count</h3>
              <div className="flex items-center">
                <button 
                  className="w-8 h-8 rounded-full border flex items-center justify-center"
                  onClick={() => setPanelCount(Math.max(1, panelCount - 1))}
                >
                  -
                </button>
                <span className="mx-4">{panelCount}</span>
                <button 
                  className="w-8 h-8 rounded-full border flex items-center justify-center"
                  onClick={() => setPanelCount(Math.min(12, panelCount + 1))}
                >
                  +
                </button>
              </div>
            </div>
            
            <div className="flex-1 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-2">AI Model</h3>
              <select 
                className="w-full p-2 border rounded"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {filteredModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Generate Button */}
          <button 
            className={`w-full py-3 rounded-lg text-white font-medium mb-8 ${
              isGenerating ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
            onClick={generateManga}
            disabled={isGenerating || !narrative.trim()}
          >
            {isGenerating ? 'Generating...' : 'Generate Manga'}
          </button>
          
          {/* Preview */}
          {panels.length > 0 && (
            <div>
              <h3 className="font-medium mb-4">Preview</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {panels.map(panel => (
                  <div key={panel.id} className="border rounded-lg overflow-hidden">
                    <img 
                      src={panel.imageUrl} 
                      alt={`Panel ${panel.id + 1}`}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-2">
                      <button className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded">
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 flex justify-end space-x-4">
                <button className="px-4 py-2 border rounded">Save Draft</button>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded">
                  Export Manga
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default MangaEditor;