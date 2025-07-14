import React, { useState, useEffect, useRef, useMemo } from 'react';

const DSMVisualization = () => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const frameRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [viewMode, setViewMode] = useState('3d'); // '3d', 'matrix', 'force'
  const [hoveredCell, setHoveredCell] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

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
    'Graphics Procesing Units',
    'NVIDIA Blackwell B200',
    'Tensor Processing Units',
    'Google Trillium TPU v6',
    'Field Programable Gate Array',
    'AMD Xilinx Versal VP1802',
    'Programming Languages',
    'C++ Programing Language',
    'Python Programing Language',
    'VHDL Programing Language',
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
      'Graphics Procesing Units': ['NVIDIA Blackwell B200'],
      'Tensor Processing Units': ['Google Trillium TPU v6'],
      'Field Programable Gate Array': ['AMD Xilinx Versal VP1802'],

      // AI/ML Models dependencies
      'Large Language Models': [
        'Gemini 2.0 Flash Experimental',
        'Machine Learning Frameworks',
        'Python Programing Language',
      ],

      'Machine Learning Frameworks': [
        'Tensor Processing Units',
        'Graphics Procesing Units',
        'Python Programing Language',
        'C++ Programing Language',
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
        'C++ Programing Language',
        'Python Programing Language',
        'VHDL Programing Language',
      ],

      // Network slicing dependencies
      'Public 5G Network Slicing': [
        'Prosthetics Health Network Slice',
        'Robotic Control Network Slice',
      ],

      // Identity Management
      'Identity Management System': ['Google Identity', 'Neural Management Systems'],

      // Hardware acceleration dependencies
      'Serverless GPU Acceleration': ['Graphics Procesing Units'],
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

  // Category colors based on component types and NeuraScale layers
  const getCategoryColor = (name) => {
    // Neural and Brain interfaces - Cyan (NIIL Layer)
    if (
      name.includes('Neural') ||
      name.includes('Brain') ||
      name.includes('Implantable') ||
      name.includes('Non-Invasive')
    )
      return '#00ffff';
    // Network and communication - Purple
    if (name.includes('Network') || name.includes('5G') || name.includes('Identity'))
      return '#ff00ff';
    // Cloud infrastructure - Green
    if (name.includes('Cloud') || name.includes('Serverless') || name.includes('Fully-Managed'))
      return '#00ff00';
    // Processing units (TPU/GPU/FPGA) - Orange
    if (
      name.includes('TPU') ||
      name.includes('GPU') ||
      name.includes('Processing Units') ||
      name.includes('FPGA')
    )
      return '#ff6600';
    // VR/AR/Interface (NIIL Layer) - Yellow
    if (
      name.includes('VR') ||
      name.includes('Interface') ||
      name.includes('OmniVerse') ||
      name.includes('Vision Pro') ||
      name.includes('Quest')
    )
      return '#ffff00';
    // Database and storage - Pink
    if (
      name.includes('Database') ||
      name.includes('Storage') ||
      name.includes('BigQuery') ||
      name.includes('AlloyDB')
    )
      return '#ff0066';
    // Robotics and prosthetics (PICL Layer) - Red
    if (
      name.includes('Robot') ||
      name.includes('Prosthetic') ||
      name.includes('Kinematic') ||
      name.includes('Limb')
    )
      return '#ff3333';
    // AI/ML Models (ADAM Layer) - Light Blue
    if (
      name.includes('Model') ||
      name.includes('Machine Learning') ||
      name.includes('Language Models') ||
      name.includes('Speech')
    )
      return '#66ccff';
    // Programming and OS - Gray
    if (name.includes('Programming') || name.includes('Operating System') || name.includes('Linux'))
      return '#999999';
    // Default - Blue
    return '#6666ff';
  };

  // 3D Force-Directed Graph
  useEffect(() => {
    if (viewMode !== '3d' || !mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    scene.fog = new THREE.Fog(0x0a0a0a, 100, 400);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 200;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight - 100);
    mountRef.current.appendChild(renderer.domElement);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 0.8);
    pointLight.position.set(50, 50, 50);
    scene.add(pointLight);

    // Create nodes
    const nodes = components.map((name, i) => {
      const geometry = new THREE.SphereGeometry(3, 32, 32);
      const material = new THREE.MeshPhongMaterial({
        color: getCategoryColor(name),
        emissive: getCategoryColor(name),
        emissiveIntensity: 0.3,
        transparent: true,
        opacity: 0.8,
      });
      const sphere = new THREE.Mesh(geometry, material);

      // Position nodes in a sphere
      const phi = Math.acos(1 - (2 * (i + 0.5)) / components.length);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;

      sphere.position.x = 100 * Math.sin(phi) * Math.cos(theta);
      sphere.position.y = 100 * Math.sin(phi) * Math.sin(theta);
      sphere.position.z = 100 * Math.cos(phi);

      sphere.userData = { index: i, name };
      scene.add(sphere);
      return sphere;
    });

    // Create edges
    const edges = [];
    for (let i = 0; i < components.length; i++) {
      for (let j = 0; j < components.length; j++) {
        if (dsmMatrix[i][j] === 1) {
          const geometry = new THREE.BufferGeometry().setFromPoints([
            nodes[i].position,
            nodes[j].position,
          ]);
          const material = new THREE.LineBasicMaterial({
            color: 0x00ff00,
            opacity: 0.3,
            transparent: true,
          });
          const line = new THREE.Line(geometry, material);
          scene.add(line);
          edges.push({ line, start: nodes[i], end: nodes[j] });
        }
      }
    }

    // Mouse interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseMove = (event) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodes);

      nodes.forEach((node) => {
        node.scale.setScalar(1);
        node.material.emissiveIntensity = 0.3;
      });

      if (intersects.length > 0) {
        const intersected = intersects[0].object;
        intersected.scale.setScalar(1.5);
        intersected.material.emissiveIntensity = 0.8;

        // Highlight connected nodes
        const index = intersected.userData.index;
        for (let j = 0; j < components.length; j++) {
          if (dsmMatrix[index][j] === 1 || dsmMatrix[j][index] === 1) {
            nodes[j].material.emissiveIntensity = 0.6;
          }
        }
      }
    };

    window.addEventListener('mousemove', onMouseMove);

    // Animation
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);

      // Rotate the entire scene slowly
      scene.rotation.y += 0.002;

      // Update edge positions
      edges.forEach(({ line, start, end }) => {
        const positions = line.geometry.attributes.position.array;
        positions[0] = start.position.x;
        positions[1] = start.position.y;
        positions[2] = start.position.z;
        positions[3] = end.position.x;
        positions[4] = end.position.y;
        positions[5] = end.position.z;
        line.geometry.attributes.position.needsUpdate = true;
      });

      renderer.render(scene, camera);
    };

    animate();

    // Store refs
    sceneRef.current = scene;
    rendererRef.current = renderer;

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      mountRef.current?.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [viewMode, dsmMatrix]);

  // Filtered components based on search
  const filteredIndices = useMemo(() => {
    if (!searchTerm) return components.map((_, i) => i);
    return components
      .map((name, i) => ({ name, i }))
      .filter(({ name }) => name.toLowerCase().includes(searchTerm.toLowerCase()))
      .map(({ i }) => i);
  }, [searchTerm]);

  const MatrixView = () => (
    <div className="w-full h-full overflow-auto bg-black p-4">
      <div className="inline-block">
        <div className="flex">
          <div className="w-48"></div>
          {filteredIndices.map((j) => (
            <div
              key={j}
              className="w-6 h-32 flex items-end justify-center"
              style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
            >
              <span className="text-xs text-gray-400 truncate max-h-32">{components[j]}</span>
            </div>
          ))}
        </div>
        {filteredIndices.map((i) => (
          <div key={i} className="flex">
            <div className="w-48 h-6 flex items-center pr-2">
              <span className="text-xs text-gray-400 truncate">{components[i]}</span>
            </div>
            {filteredIndices.map((j) => (
              <div
                key={`${i}-${j}`}
                className={`w-6 h-6 border border-gray-800 cursor-pointer transition-all duration-200 ${
                  i === j ? 'bg-gray-800' : ''
                } ${dsmMatrix[i][j] === 1 ? 'bg-green-500' : ''} ${
                  hoveredCell?.i === i || hoveredCell?.j === j ? 'border-cyan-400 border-2' : ''
                }`}
                onMouseEnter={() => setHoveredCell({ i, j })}
                onMouseLeave={() => setHoveredCell(null)}
                onClick={() => {
                  if (dsmMatrix[i][j] === 1) {
                    setSelectedNode({ from: components[i], to: components[j] });
                  }
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );

  const ForceGraphView = () => {
    const svgRef = useRef(null);

    useEffect(() => {
      if (!svgRef.current) return;

      const width = window.innerWidth - 100;
      const height = window.innerHeight - 200;

      const svg = d3.select(svgRef.current).attr('width', width).attr('height', height);

      svg.selectAll('*').remove();

      // Create nodes and links data
      const nodes = components.map((name, i) => ({
        id: i,
        name,
        color: getCategoryColor(name),
      }));

      const links = [];
      for (let i = 0; i < components.length; i++) {
        for (let j = 0; j < components.length; j++) {
          if (dsmMatrix[i][j] === 1) {
            links.push({ source: i, target: j });
          }
        }
      }

      // Create force simulation
      const simulation = d3
        .forceSimulation(nodes)
        .force(
          'link',
          d3
            .forceLink(links)
            .id((d) => d.id)
            .distance(50)
        )
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(20));

      // Add zoom
      const g = svg.append('g');

      svg.call(
        d3
          .zoom()
          .scaleExtent([0.1, 10])
          .on('zoom', (event) => {
            g.attr('transform', event.transform);
          })
      );

      // Draw links
      const link = g
        .append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#00ff00')
        .attr('stroke-opacity', 0.3)
        .attr('stroke-width', 1);

      // Draw nodes
      const node = g
        .append('g')
        .selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('r', 8)
        .attr('fill', (d) => d.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended));

      // Add labels
      const label = g
        .append('g')
        .selectAll('text')
        .data(nodes)
        .enter()
        .append('text')
        .text((d) => d.name)
        .attr('font-size', 10)
        .attr('fill', '#fff')
        .attr('dx', 12)
        .attr('dy', 4);

      // Add hover effects
      node
        .on('mouseover', function (event, d) {
          d3.select(this).attr('r', 12);

          // Highlight connected links
          link.attr('stroke-opacity', (l) =>
            l.source.id === d.id || l.target.id === d.id ? 0.8 : 0.1
          );
        })
        .on('mouseout', function () {
          d3.select(this).attr('r', 8);
          link.attr('stroke-opacity', 0.3);
        });

      // Update positions
      simulation.on('tick', () => {
        link
          .attr('x1', (d) => d.source.x)
          .attr('y1', (d) => d.source.y)
          .attr('x2', (d) => d.target.x)
          .attr('y2', (d) => d.target.y);

        node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);

        label.attr('x', (d) => d.x).attr('y', (d) => d.y);
      });

      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }

      return () => {
        simulation.stop();
      };
    }, []);

    return (
      <div className="w-full h-full bg-black">
        <svg ref={svgRef}></svg>
      </div>
    );
  };

  return (
    <div className="w-full h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            NeuraScale Design Structure Matrix
          </h1>
          <div className="flex items-center gap-4">
            <input
              type="text"
              placeholder="Search components..."
              className="px-4 py-2 bg-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('3d')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  viewMode === '3d' ? 'bg-cyan-500 text-black' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                3D Graph
              </button>
              <button
                onClick={() => setViewMode('matrix')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  viewMode === 'matrix' ? 'bg-cyan-500 text-black' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                Matrix
              </button>
              <button
                onClick={() => setViewMode('force')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  viewMode === 'force' ? 'bg-cyan-500 text-black' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                Force Graph
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Visualization Container */}
      <div className="relative w-full h-full">
        {viewMode === '3d' && <div ref={mountRef} className="w-full h-full" />}
        {viewMode === 'matrix' && <MatrixView />}
        {viewMode === 'force' && <ForceGraphView />}

        {/* Info Panel */}
        {selectedNode && (
          <div className="absolute top-4 right-4 bg-gray-800 p-4 rounded-lg max-w-sm">
            <h3 className="font-bold mb-2">Dependency</h3>
            <p className="text-sm text-gray-300">
              <span className="text-cyan-400">{selectedNode.from}</span>
              {' → '}
              <span className="text-purple-400">{selectedNode.to}</span>
            </p>
            <button
              onClick={() => setSelectedNode(null)}
              className="mt-2 text-xs text-gray-500 hover:text-white"
            >
              Close
            </button>
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-gray-800 p-4 rounded-lg">
          <h3 className="font-bold mb-2 text-sm">NeuraScale Architecture Layers</h3>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
              <span>Neural/Brain Interfaces</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-400 rounded-full"></div>
              <span>PICL - Physical Integration & Control</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <span>NIIL - Neural Interaction & Immersion</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#66ccff' }}></div>
              <span>ADAM - AI Domain Agnostic Models</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span>Cloud Infrastructure</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-400 rounded-full"></div>
              <span>Processing Units (TPU/GPU/FPGA)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
              <span>Network & Identity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-pink-400 rounded-full"></div>
              <span>Database & Storage</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DSMVisualization;
