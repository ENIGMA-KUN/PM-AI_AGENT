import React, { useState, useEffect } from 'react';

const KanbanBoard = ({ planData }) => {
  const [columns, setColumns] = useState({
    backlog: [],
    doing: [],
    done: []
  });

  useEffect(() => {
    if (planData && planData.stories) {
      // Sort stories into columns based on status
      const newColumns = {
        backlog: [],
        doing: [],
        done: []
      };
      
      planData.stories.forEach(story => {
        const status = story.status.toLowerCase();
        if (status === 'doing' || status === 'in progress') {
          newColumns.doing.push(story);
        } else if (status === 'done' || status === 'completed') {
          newColumns.done.push(story);
        } else {
          newColumns.backlog.push(story);
        }
      });
      
      setColumns(newColumns);
    }
  }, [planData]);

  const handleDragStart = (e, story, sourceColumn) => {
    e.dataTransfer.setData('story', JSON.stringify(story));
    e.dataTransfer.setData('sourceColumn', sourceColumn);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e, targetColumn) => {
    e.preventDefault();
    
    const story = JSON.parse(e.dataTransfer.getData('story'));
    const sourceColumn = e.dataTransfer.getData('sourceColumn');
    
    if (sourceColumn === targetColumn) return;
    
    setColumns(prev => {
      // Remove from source column
      const newSourceColumn = prev[sourceColumn].filter(
        s => s.title !== story.title || s.owner !== story.owner
      );
      
      // Add to target column with updated status
      const updatedStory = {
        ...story,
        status: targetColumn === 'backlog' ? 'Backlog' : 
                targetColumn === 'doing' ? 'In Progress' : 'Done'
      };
      
      return {
        ...prev,
        [sourceColumn]: newSourceColumn,
        [targetColumn]: [...prev[targetColumn], updatedStory]
      };
    });
  };

  const renderColumn = (title, columnKey, bgColor) => (
    <div 
      className={`flex-1 ${bgColor} p-4 rounded-lg shadow`}
      onDragOver={handleDragOver}
      onDrop={(e) => handleDrop(e, columnKey)}
    >
      <h3 className="font-bold text-lg mb-3">{title}</h3>
      <div className="space-y-2">
        {columns[columnKey].map((story, index) => (
          <div
            key={`${story.title}-${story.owner}-${index}`}
            className="bg-white p-3 rounded shadow-sm cursor-move"
            draggable
            onDragStart={(e) => handleDragStart(e, story, columnKey)}
          >
            <div className="font-medium">{story.title}</div>
            <div className="text-sm text-gray-600">Owner: {story.owner}</div>
            <div className="text-sm text-gray-600">Due: {story.due_date}</div>
          </div>
        ))}
        {columns[columnKey].length === 0 && (
          <div className="text-gray-500 text-sm italic">No items</div>
        )}
      </div>
    </div>
  );

  if (!planData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Kanban Board</h2>
        <p className="text-gray-500">No plan data available. Please create a plan using the /plan command in the chat.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Kanban Board</h2>
      <div className="flex gap-4">
        {renderColumn('Backlog', 'backlog', 'bg-gray-100')}
        {renderColumn('Doing', 'doing', 'bg-blue-100')}
        {renderColumn('Done', 'done', 'bg-green-100')}
      </div>
    </div>
  );
};

export default KanbanBoard;
