import React, { useState, useMemo } from 'react';

const DSMMatrix = () => {
  const [hoveredCell, setHoveredCell] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  // DSM Data
  const components = [
    'Neural Management Systems',
    'Neuroprosthetics',
    'Brain–Robot Swarm Interface',
    'Full-Dive VR',
    'Human Interface Device',
    'Implantable Brain Computer Interface',
    'Non-Invasive Brain Computer Interface',
    'Cloud Infrastructure',
    'Fully-Managed Serverless Compute',
    'Fully-Managed Database Service',
    'Fully-Managed AI Development Platform',
    'Fully-Managed API Management Solution',
    'Serverless GPU Acceleration',
    'Serverless TPU Acceleration',
    'Fully-Managed Load Balancer',
    'Threat Detection & Posture Management',
    'Public 5G Network Slicing',
    'Prosthetics Health Network Slice',
    'Robotic Control Network Slice',
    'Graphics Processing Units',
    'NVIDIA Blackwell B200',
    'Tensor Processing Units',
    'Google Trillium TPU v6',
    'Field Programmable Gate Array',
    'AMD Xilinx Versal VP1802',
    'Programming Languages',
    'C++ Programming Language',
    'Python Programming Language',
    'VHDL Programming Language',
    'Identity Management System',
    'Google Identity',
    'AWS IoT GreenGrass',
    'Operating System',
    'Linux OS',
    'Robotic Operation System',
    'Database Management System',
    'AlloyDB PostgreSQL',
    'BigQuery Data Warehouse',
    'Google Storage',
    'Large Language Models',
    'Machine Learning Frameworks',
    'Gemini 2.0 Flash Experimental',
    'Application Programmable Interface',
    'Inverse Kinematics Models',
    'Robotic Limbs Interface',
    'Automatic Speech Recognition',
    'Modular 3D Platform',
    'NVIDIA OmniVerse',
    'VR Interface Device',
    'Apple Vision Pro',
    'Meta Quest',
  ];

  // DSM matrix based on NeuraScale project architecture
  const generateDSMMatrix = () => {
    const matrix = Array(components.length)
      .fill(null)
      .map(() => Array(components.length).fill(0));

    // Dependencies extracted from the NeuraScale project document
    const dependencies = {
      // Neural Management System (NMS) is the central orchestrator
      'Neural Management Systems': [
        'Neuroprosthetics',
        'Brain–Robot Swarm Interface',
        'Full-Dive VR',
        'Implantable Brain Computer Interface',
        'Non-Invasive Brain Computer Interface',
        'Cloud Infrastructure',
        'Machine Learning Frameworks',
      ],

      // Neural Interaction & Immersion Layer (NIIL) components
      'Full-Dive VR': [
        'VR Interface Device',
        'Apple Vision Pro',
        'Meta Quest',
        'NVIDIA OmniVerse',
        'Modular 3D Platform',
      ],

      // Neuroprosthetics dependencies (3IKM project)
      Neuroprosthetics: [
        'Inverse Kinematics Models',
        'Robotic Limbs Interface',
        'Implantable Brain Computer Interface',
        'Non-Invasive Brain Computer Interface',
      ],

      // Brain-Robot Swarm Interface (4ROS project)
      'Brain–Robot Swarm Interface': [
        'Robotic Operation System',
        'AWS IoT GreenGrass',
        'Robotic Control Network Slice',
        'Machine Learning Frameworks',
      ],

      // Cloud Infrastructure dependencies
      'Cloud Infrastructure': [
        'Fully-Managed Serverless Compute',
        'Fully-Managed Database Service',
        'Fully-Managed AI Development Platform',
        'Fully-Managed API Management Solution',
        'Fully-Managed Load Balancer',
        'Threat Detection & Posture Management',
      ],

      // Processing units dependencies
      'Graphics Processing Units': ['NVIDIA Blackwell B200'],
      'Tensor Processing Units': ['Google Trillium TPU v6'],
      'Field Programmable Gate Array': ['AMD Xilinx Versal VP1802'],

      // AI/ML Models dependencies
      'Large Language Models': [
        'Gemini 2.0 Flash Experimental',
        'Machine Learning Frameworks',
        'Python Programming Language',
      ],

      'Machine Learning Frameworks': [
        'Tensor Processing Units',
        'Graphics Processing Units',
        'Python Programming Language',
        'C++ Programming Language',
        'Large Language Models',
        'Application Programmable Interface',
      ],

      // Database dependencies
      'Database Management System': [
        'AlloyDB PostgreSQL',
        'BigQuery Data Warehouse',
        'Google Storage',
      ],

      // Operating System dependencies
      'Operating System': ['Linux OS', 'Robotic Operation System'],

      // Programming Language dependencies
      'Programming Languages': [
        'C++ Programming Language',
        'Python Programming Language',
        'VHDL Programming Language',
      ],

      // Network slicing dependencies
      'Public 5G Network Slicing': [
        'Prosthetics Health Network Slice',
        'Robotic Control Network Slice',
      ],

      // Identity Management
      'Identity Management System': ['Google Identity', 'Neural Management Systems'],

      // Hardware acceleration dependencies
      'Serverless GPU Acceleration': ['Graphics Processing Units'],
      'Serverless TPU Acceleration': ['Tensor Processing Units'],

      // Interface dependencies
      'Human Interface Device': [
        'Implantable Brain Computer Interface',
        'Non-Invasive Brain Computer Interface',
      ],

      // API dependencies
      'Application Programmable Interface': ['Fully-Managed API Management Solution'],

      // Voice/Speech dependencies
      'Automatic Speech Recognition': ['Machine Learning Frameworks', 'Large Language Models'],

      // Additional layer dependencies
      'Implantable Brain Computer Interface': ['Neural Management Systems'],
      'Non-Invasive Brain Computer Interface': ['Neural Management Systems'],

      // Compute dependencies
      'Fully-Managed Serverless Compute': [
        'Serverless GPU Acceleration',
        'Serverless TPU Acceleration',
      ],

      // Additional bidirectional relationships
      'Cloud Infrastructure': ['Neural Management Systems'],
      'Database Management System': ['Cloud Infrastructure'],
      'Operating System': ['Cloud Infrastructure'],
    };

    // Create component index mapping
    const componentIndex = {};
    components.forEach((name, idx) => {
      componentIndex[name] = idx;
    });

    // Fill in the dependencies
    for (const [source, targets] of Object.entries(dependencies)) {
      const sourceIdx = componentIndex[source];
      if (sourceIdx !== undefined) {
        targets.forEach((target) => {
          const targetIdx = componentIndex[target];
          if (targetIdx !== undefined) {
            matrix[sourceIdx][targetIdx] = 1;
          }
        });
      }
    }

    // Add some bidirectional relationships based on the architecture
    const bidirectionalPairs = [
      ['Cloud Infrastructure', 'Database Management System'],
      ['Machine Learning Frameworks', 'Application Programmable Interface'],
      ['Programming Languages', 'Machine Learning Frameworks'],
      ['Implantable Brain Computer Interface', 'Neuroprosthetics'],
      ['Non-Invasive Brain Computer Interface', 'Neuroprosthetics'],
    ];

    bidirectionalPairs.forEach(([a, b]) => {
      const aIdx = componentIndex[a];
      const bIdx = componentIndex[b];
      if (aIdx !== undefined && bIdx !== undefined) {
        matrix[aIdx][bIdx] = 1;
        matrix[bIdx][aIdx] = 1;
      }
    });

    return matrix;
  };

  const dsmMatrix = useMemo(() => generateDSMMatrix(), []);

  // Show more components to better fill the available space
  const displayComponents = components.slice(0, 35);
  const displayMatrix = dsmMatrix.slice(0, 35).map((row) => row.slice(0, 35));

  return (
    <div className="w-full h-full overflow-auto bg-black p-2">
      <div className="inline-block">
        <div className="flex">
          <div className="w-24"></div>
          {displayComponents.map((component, j) => (
            <div
              key={j}
              className="w-3 h-20 flex items-end justify-center"
              style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
            >
              <span className="text-[9px] text-gray-400 truncate max-h-20">
                {component.split(' ').slice(0, 2).join(' ')}
              </span>
            </div>
          ))}
        </div>
        {displayComponents.map((component, i) => (
          <div key={i} className="flex">
            <div className="w-24 h-3 flex items-center pr-1">
              <span className="text-[9px] text-gray-400 truncate">
                {component.split(' ').slice(0, 2).join(' ')}
              </span>
            </div>
            {displayComponents.map((_, j) => (
              <div
                key={`${i}-${j}`}
                className={`w-3 h-3 border border-gray-800 cursor-pointer transition-all duration-200 ${
                  i === j ? 'bg-gray-600' : ''
                } ${displayMatrix[i][j] === 1 ? 'bg-green-400' : ''} ${
                  hoveredCell?.i === i || hoveredCell?.j === j ? 'border-cyan-400 border-2' : ''
                }`}
                onMouseEnter={() => setHoveredCell({ i, j })}
                onMouseLeave={() => setHoveredCell(null)}
                onClick={() => {
                  if (displayMatrix[i][j] === 1) {
                    setSelectedNode({ from: displayComponents[i], to: displayComponents[j] });
                  }
                }}
              />
            ))}
          </div>
        ))}
      </div>

      {/* Info tooltip */}
      {selectedNode && (
        <div className="absolute top-2 right-2 bg-gray-800 p-2 rounded text-xs max-w-48">
          <div className="text-cyan-400 font-semibold mb-1">Dependency</div>
          <div className="text-gray-300">
            <div className="text-cyan-300">
              {selectedNode.from.split(' ').slice(0, 2).join(' ')}
            </div>
            <div className="text-center">↓</div>
            <div className="text-purple-300">
              {selectedNode.to.split(' ').slice(0, 2).join(' ')}
            </div>
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="mt-1 text-[10px] text-gray-500 hover:text-white"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};

export default DSMMatrix;
