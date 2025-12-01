// BookForge AI - WritingStudio Component
// Extracted from book-writing-creative-ideas.pdf
// AUTHOR-CONTROLLED WRITING INTERFACE

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  FiSave, FiDownload, FiUsers, FiMap, FiImage,
  FiMic, FiTrendingUp, FiArrowLeft, FiLightbulb,
  FiEdit3, FiBookOpen, FiZap, FiCheckCircle
} from 'react-icons/fi';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

const WritingStudio: React.FC = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<any>(null);
  const [currentChapter, setCurrentChapter] = useState<any>(null);
  const [content, setContent] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [showAssistPanel, setShowAssistPanel] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const editorRef = useRef<any>(null);

  // Calculate word count
  useEffect(() => {
    const text = content.replace(/<[^>]*>/g, '');
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    setWordCount(words.length);
  }, [content]);

  // Auto-save every 30 seconds
  useEffect(() => {
    if (!autoSaveEnabled) return;

    const interval = setInterval(() => {
      saveContent(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [content, autoSaveEnabled]);

  const saveContent = async (silent: boolean = false) => {
    if (!currentChapter || !project) return;

    try {
      const updatedChapter = {
        ...currentChapter,
        content,
        word_count: wordCount,
        updated_at: new Date().toISOString()
      };

      await axios.put(`http://localhost:8000/api/project/${projectId}`, {
        chapters: [
          ...(project.chapters || []).filter((c: any) => c.id !== currentChapter.id),
          updatedChapter
        ],
        current_word_count: (project.chapters || [])
          .filter((c: any) => c.id !== currentChapter.id)
          .reduce((sum: number, c: any) => sum + c.word_count, 0) + wordCount
      });

      if (!silent) {
        alert('✓ Saved successfully!');
      }
    } catch (error) {
      console.error('Error saving:', error);
      if (!silent) {
        alert('Failed to save');
      }
    }
  };

  return (
    <div className="writing-studio min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <FiArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-bold">{project?.title || 'Loading...'}</h1>
              <p className="text-sm text-gray-400">
                {currentChapter?.title || 'Select a chapter'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <span className="text-gray-400">Words:</span>
              <span className="ml-2 font-bold">{wordCount.toLocaleString()}</span>
            </div>

            <button
              onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
              className={`px-3 py-1 rounded text-sm ${
                autoSaveEnabled ? 'bg-green-600' : 'bg-gray-600'
              }`}
            >
              Auto-save: {autoSaveEnabled ? 'ON' : 'OFF'}
            </button>

            <button
              onClick={() => saveContent(false)}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
            >
              <FiSave />
              <span>Save</span>
            </button>

            <button
              onClick={() => setShowAssistPanel(!showAssistPanel)}
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded"
            >
              <FiLightbulb />
              <span>Assist</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor */}
        <div className="flex-1 p-6 overflow-auto">
          <ReactQuill
            ref={editorRef}
            value={content}
            onChange={setContent}
            theme="snow"
            className="h-full"
            modules={{
              toolbar: [
                [{ 'header': [1, 2, 3, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                ['blockquote', 'code-block'],
                ['link'],
                ['clean']
              ]
            }}
          />
        </div>

        {/* Assistance Panel */}
        {showAssistPanel && (
          <div className="w-96 bg-gray-800 border-l border-gray-700 p-6 overflow-auto">
            <h2 className="text-lg font-bold mb-4 flex items-center">
              <FiLightbulb className="mr-2" />
              Writing Assistance
            </h2>

            <div className="space-y-4">
              <button className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded">
                <div className="flex items-center justify-between">
                  <span>Suggest Next Scene</span>
                  <FiZap size={16} />
                </div>
              </button>

              <button className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded">
                <div className="flex items-center justify-between">
                  <span>Character Development</span>
                  <FiUsers size={16} />
                </div>
              </button>

              <button className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded">
                <div className="flex items-center justify-between">
                  <span>Plot Analysis</span>
                  <FiTrendingUp size={16} />
                </div>
              </button>

              <button className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded">
                <div className="flex items-center justify-between">
                  <span>World Building</span>
                  <FiMap size={16} />
                </div>
              </button>
            </div>

            <div className="mt-6 p-4 bg-gray-700 rounded">
              <p className="text-sm text-gray-300">
                <strong>Remember:</strong> You're in control. These are suggestions only.
                Accept, modify, or ignore as you see fit.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WritingStudio;