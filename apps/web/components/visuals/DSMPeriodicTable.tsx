import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const DSMPeriodicTable = () => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const objectsRef = useRef([]);
  const targetsRef = useRef({ table: [], sphere: [], helix: [], grid: [] });
  const tweensRef = useRef([]);

  useEffect(() => {
    if (!containerRef.current) return;

    // DSM Elements data
    const table = [
      { code: "1NMS", name: "Neural Management Systems", category: "Core System", col: 1, row: 1 },
      { code: "2NPT", name: "Neuroprosthetics", category: "Main Product", col: 2, row: 1 },
      { code: "2BSI", name: "Brain-Robot Swarm Interface", category: "Main Product", col: 3, row: 1 },
      { code: "2FDV", name: "Full-Dive VR", category: "Main Product", col: 4, row: 1 },
      { code: "2HID", name: "Human Interface Device", category: "Neural Interface", col: 5, row: 1 },
      { code: "2IBC", name: "Implantable Brain Computer Interface", category: "Neural Interface", col: 6, row: 1 },
      { code: "2NBC", name: "Non-Invasive Brain Computer Interface", category: "Neural Interface", col: 7, row: 1 },
      { code: "3CLD", name: "Cloud Infrastructure", category: "Cloud", col: 1, row: 2 },
      { code: "3FSC", name: "Fully-Managed Serverless Compute", category: "Cloud", col: 2, row: 2 },
      { code: "3FDS", name: "Fully-Managed Database Service", category: "Cloud", col: 3, row: 2 },
      { code: "3FAI", name: "Fully-Managed AI Development Platform", category: "Cloud", col: 4, row: 2 },
      { code: "3FAM", name: "Fully-Managed API Management Solution", category: "Cloud", col: 5, row: 2 },
      { code: "3SGA", name: "Serverless GPU Acceleration", category: "Cloud", col: 6, row: 2 },
      { code: "3STA", name: "Serverless TPU Acceleration", category: "Cloud", col: 7, row: 2 },
      { code: "3FLB", name: "Fully-Managed Load Balancer", category: "Cloud", col: 8, row: 2 },
      { code: "3TDP", name: "Threat Detection & Posture Management", category: "Cloud", col: 9, row: 2 },
      { code: "4P5G", name: "Public 5G Network Slicing", category: "Network", col: 1, row: 3 },
      { code: "4PHN", name: "Prosthetics Health Network Slice", category: "Network", col: 2, row: 3 },
      { code: "4RCN", name: "Robotic Control Network Slice", category: "Network", col: 3, row: 3 },
      { code: "4ROS", name: "Robotic Operation System", category: "Robotics", col: 13, row: 4 },
      { code: "5GPU", name: "Graphics Processing Units", category: "Hardware", col: 4, row: 3 },
      { code: "5NVB", name: "NVIDIA Blackwell B200", category: "Hardware", col: 5, row: 3 },
      { code: "5TPU", name: "Tensor Processing Units", category: "Hardware", col: 6, row: 3 },
      { code: "5GTT", name: "Google Trillium TPU v6", category: "Hardware", col: 7, row: 3 },
      { code: "5FPG", name: "Field Programmable Gate Array", category: "Hardware", col: 8, row: 3 },
      { code: "5AXV", name: "AMD Xilinx Versal VP1802", category: "Hardware", col: 9, row: 3 },
      { code: "6PRL", name: "Programming Languages", category: "Software", col: 1, row: 4 },
      { code: "6CPP", name: "C++ Programming Language", category: "Software", col: 2, row: 4 },
      { code: "6PYT", name: "Python Programming Language", category: "Software", col: 3, row: 4 },
      { code: "6VHD", name: "VHDL Programming Language", category: "Software", col: 4, row: 4 },
      { code: "7IMS", name: "Identity Management System", category: "Security", col: 5, row: 4 },
      { code: "7GID", name: "Google Identity", category: "Security", col: 6, row: 4 },
      { code: "7AIG", name: "AWS IoT GreenGrass", category: "Security", col: 7, row: 4 },
      { code: "8OPS", name: "Operating System", category: "OS", col: 8, row: 4 },
      { code: "8LNX", name: "Linux OS", category: "OS", col: 9, row: 4 },
      { code: "9DMS", name: "Database Management System", category: "Database", col: 10, row: 4 },
      { code: "9ADB", name: "AlloyDB PostgreSQL", category: "Database", col: 11, row: 4 },
      { code: "9BQD", name: "BigQuery Data Warehouse", category: "Database", col: 12, row: 4 },
      { code: "9GST", name: "Google Storage", category: "Database", col: 10, row: 3 },
      { code: "ALLM", name: "Large Language Models", category: "AI/ML", col: 1, row: 5 },
      { code: "AMLF", name: "Machine Learning Frameworks", category: "AI/ML", col: 2, row: 5 },
      { code: "AGFE", name: "Gemini 2.0 Flash Experimental", category: "AI/ML", col: 3, row: 5 },
      { code: "BAPI", name: "Application Programmable Interface", category: "Interface", col: 4, row: 5 },
      { code: "BIKM", name: "Inverse Kinematics Models", category: "Robotics", col: 5, row: 5 },
      { code: "BRLI", name: "Robotic Limbs Interface", category: "Robotics", col: 6, row: 5 },
      { code: "BASR", name: "Automatic Speech Recognition", category: "AI/ML", col: 7, row: 5 },
      { code: "CM3P", name: "Modular 3D Platform", category: "VR", col: 11, row: 3 },
      { code: "CNVO", name: "NVIDIA OmniVerse", category: "VR", col: 12, row: 3 },
      { code: "CVID", name: "VR Interface Device", category: "VR", col: 13, row: 3 },
      { code: "CAVP", name: "Apple Vision Pro", category: "VR", col: 14, row: 3 },
      { code: "CMQU", name: "Meta Quest", category: "VR", col: 15, row: 3 }
    ];

    const init = () => {
      const scene = new THREE.Scene();
      const container = containerRef.current;
      const width = container.clientWidth;
      const height = container.clientHeight;
      const camera = new THREE.PerspectiveCamera(40, width / height, 1, 10000);
      camera.position.z = 2500;
      camera.position.y = -200; // Move camera down to center the view

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, height);
      renderer.setClearColor(0x000000, 1);
      container.appendChild(renderer.domElement);

      sceneRef.current = scene;
      cameraRef.current = camera;
      rendererRef.current = renderer;

      const objects = [];
      const targets = { table: [], sphere: [], helix: [], grid: [] };

      // Create HTML elements container
      const elementsContainer = document.createElement('div');
      elementsContainer.style.position = 'absolute';
      elementsContainer.style.top = '0';
      elementsContainer.style.left = '0';
      elementsContainer.style.width = '100%';
      elementsContainer.style.height = '100%';
      elementsContainer.style.transformStyle = 'preserve-3d';
      elementsContainer.style.pointerEvents = 'none';
      elementsContainer.style.perspective = '2000px';
      containerRef.current.appendChild(elementsContainer);

      // Create elements
      table.forEach((element, i) => {
        // Create HTML element
        const elementDiv = document.createElement('div');
        elementDiv.className = 'element';
        elementDiv.style.width = '140px';
        elementDiv.style.height = '180px';
        elementDiv.style.position = 'absolute';
        elementDiv.style.left = '0';
        elementDiv.style.top = '0';
        elementDiv.style.transformOrigin = 'center center';
        elementDiv.style.backgroundColor = 'rgba(0,127,127,0.5)';
        elementDiv.style.border = '1px solid rgba(127,255,255,0.25)';
        elementDiv.style.boxShadow = '0px 0px 12px rgba(0,255,255,0.5)';
        elementDiv.style.textAlign = 'center';
        elementDiv.style.cursor = 'pointer';
        elementDiv.style.pointerEvents = 'auto';
        elementDiv.style.fontFamily = 'Helvetica, sans-serif';
        
        // Add gradient background with more blue
        elementDiv.style.background = `linear-gradient(135deg, 
          rgba(100,200,255,0.2) 0%, 
          rgba(0,100,200,0.6) 50%, 
          rgba(0,50,150,0.8) 100%)`;
        elementDiv.style.backdropFilter = 'blur(5px)';
        elementDiv.style.webkitBackdropFilter = 'blur(5px)';

        const number = document.createElement('div');
        number.className = 'number';
        number.textContent = (i + 1).toString();
        number.style.position = 'absolute';
        number.style.top = '20px';
        number.style.right = '20px';
        number.style.fontSize = '12px';
        number.style.color = 'rgba(127,255,255,0.75)';
        elementDiv.appendChild(number);

        const symbol = document.createElement('div');
        symbol.className = 'symbol';
        symbol.textContent = element.code;
        symbol.style.position = 'absolute';
        symbol.style.top = '40px';
        symbol.style.left = '0px';
        symbol.style.right = '0px';
        symbol.style.fontSize = '36px';
        symbol.style.fontWeight = 'bold';
        symbol.style.color = 'rgba(255,255,255,0.75)';
        symbol.style.textShadow = '0 0 10px rgba(0,255,255,0.95)';
        elementDiv.appendChild(symbol);

        const details = document.createElement('div');
        details.className = 'details';
        details.innerHTML = element.name + '<br>' + element.category;
        details.style.position = 'absolute';
        details.style.bottom = '15px';
        details.style.left = '0px';
        details.style.right = '0px';
        details.style.fontSize = '11px';
        details.style.color = 'rgba(127,255,255,0.75)';
        details.style.padding = '0 5px';
        elementDiv.appendChild(details);

        // Add hover effects
        elementDiv.addEventListener('mouseenter', () => {
          elementDiv.style.background = `linear-gradient(135deg, 
            rgba(150,220,255,0.3) 0%, 
            rgba(0,150,255,0.7) 50%, 
            rgba(0,100,200,0.9) 100%)`;
          elementDiv.style.boxShadow = '0px 0px 20px rgba(0,150,255,0.8)';
          elementDiv.style.border = '1px solid rgba(100,200,255,0.5)';
          elementDiv.style.transform = 'scale(1.05)';
        });

        elementDiv.addEventListener('mouseleave', () => {
          elementDiv.style.background = `linear-gradient(135deg, 
            rgba(100,200,255,0.2) 0%, 
            rgba(0,100,200,0.6) 50%, 
            rgba(0,50,150,0.8) 100%)`;
          elementDiv.style.boxShadow = '0px 0px 12px rgba(0,255,255,0.5)';
          elementDiv.style.border = '1px solid rgba(127,255,255,0.25)';
          elementDiv.style.transform = 'scale(1)';
        });

        elementsContainer.appendChild(elementDiv);

        // Create 3D object wrapper
        const object = new THREE.Object3D();
        object.element = elementDiv;
        object.position.x = Math.random() * 4000 - 2000;
        object.position.y = Math.random() * 4000 - 2000;
        object.position.z = Math.random() * 4000 - 2000;
        scene.add(object);
        objects.push(object);

        // Table position - ensure proper grid spacing
        const tableObject = new THREE.Object3D();
        const spacing = 200;
        const offsetX = -(Math.max(...table.map(e => e.col)) * spacing) / 2;
        const offsetY = (Math.max(...table.map(e => e.row)) * spacing) / 2 - 100; // Shift down for better centering
        
        tableObject.position.x = (element.col - 1) * spacing + offsetX;
        tableObject.position.y = -(element.row - 1) * spacing + offsetY;
        tableObject.position.z = 0;
        targets.table.push(tableObject);

        // Sphere position
        const phi = Math.acos(-1 + (2 * i) / table.length);
        const theta = Math.sqrt(table.length * Math.PI) * phi;
        const sphereObject = new THREE.Object3D();
        sphereObject.position.setFromSphericalCoords(1200, phi, theta);
        sphereObject.position.y -= 100; // Shift sphere down for better centering
        targets.sphere.push(sphereObject);

        // Helix position
        const helixTheta = i * 0.25 + Math.PI;
        const helixY = -(i * 12) + 400; // Shift helix down for better centering
        const helixObject = new THREE.Object3D();
        helixObject.position.setFromCylindricalCoords(1200, helixTheta, helixY);
        targets.helix.push(helixObject);

        // Grid position
        const gridObject = new THREE.Object3D();
        gridObject.position.x = ((i % 5) * 500) - 1000;
        gridObject.position.y = (-(Math.floor(i / 5) % 5) * 500) + 800; // Shift grid down for better centering
        gridObject.position.z = (Math.floor(i / 25)) * 1500 - 2000;
        targets.grid.push(gridObject);
      });

      objectsRef.current = objects;
      targetsRef.current = targets;

      // CSS3D-like rendering
      const render = () => {
        objects.forEach((object) => {
          const element = object.element;
          
          // Get world position
          const vector = new THREE.Vector3();
          vector.setFromMatrixPosition(object.matrixWorld);
          
          // Project to screen coordinates
          const projectedVector = vector.clone();
          projectedVector.project(camera);
          
          // Calculate screen position
          const container = containerRef.current;
          const width = container.clientWidth;
          const height = container.clientHeight;
          const x = (projectedVector.x * width * 0.5) + (width * 0.5);
          const y = (-projectedVector.y * height * 0.5) + (height * 0.5);
          
          // Calculate scale based on distance
          const distance = vector.distanceTo(camera.position);
          const scale = Math.max(0.1, Math.min(1, 2000 / distance));
          
          // Apply transform with proper centering
          element.style.transform = `translate(${x - 70}px, ${y - 90}px) scale(${scale})`;
          
          // Hide elements behind camera
          if (projectedVector.z > 1) {
            element.style.display = 'none';
          } else {
            element.style.display = 'block';
            element.style.opacity = Math.max(0.3, 1 - projectedVector.z * 0.5);
          }
          
          // Set z-index for proper layering
          element.style.zIndex = Math.floor((1 - projectedVector.z) * 1000);
        });
      };

      // Mouse controls
      let mouseX = 0, mouseY = 0;
      let targetRotationX = 0, targetRotationY = 0;
      let isMouseDown = false;
      let mouseXOnMouseDown = 0;
      let mouseYOnMouseDown = 0;
      let targetRotationXOnMouseDown = 0;
      let targetRotationYOnMouseDown = 0;
      let autoRotate = true;

      const onMouseDown = (event) => {
        event.preventDefault();
        isMouseDown = true;
        mouseXOnMouseDown = event.clientX;
        mouseYOnMouseDown = event.clientY;
        targetRotationXOnMouseDown = targetRotationX;
        targetRotationYOnMouseDown = targetRotationY;
        autoRotate = false; // Stop auto-rotation when user interacts
      };

      const onMouseMove = (event) => {
        if (!isMouseDown) return;
        
        mouseX = event.clientX - mouseXOnMouseDown;
        mouseY = event.clientY - mouseYOnMouseDown;
        
        targetRotationY = targetRotationYOnMouseDown + mouseX * 0.002;
        targetRotationX = targetRotationXOnMouseDown + mouseY * 0.002;
      };

      const onMouseUp = () => {
        isMouseDown = false;
      };

      // Toggle auto-rotation
      window.toggleAutoRotate = () => {
        autoRotate = !autoRotate;
        return autoRotate;
      };

      renderer.domElement.addEventListener('mousedown', onMouseDown);
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);

      // Initial transform to helix
      transform(targets.helix, 2000);

      // Animation loop
      const animate = () => {
        requestAnimationFrame(animate);

        // Update tweens
        tweensRef.current = tweensRef.current.filter(tween => tween.update());

        // Smooth rotation
        scene.rotation.y += (targetRotationY - scene.rotation.y) * 0.05;
        scene.rotation.x += (targetRotationX - scene.rotation.x) * 0.05;

        // Auto rotate only if enabled
        if (autoRotate) {
          targetRotationY += 0.001;
        }

        // Update element positions
        scene.updateMatrixWorld();
        render();
        
        renderer.render(scene, camera);
      };

      animate();

      // Window resize
      const onWindowResize = () => {
        const container = containerRef.current;
        if (!container) return;
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
        render();
      };
      window.addEventListener('resize', onWindowResize);

      // Cleanup function
      return () => {
        renderer.domElement.removeEventListener('mousedown', onMouseDown);
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        window.removeEventListener('resize', onWindowResize);
        containerRef.current?.removeChild(renderer.domElement);
        containerRef.current?.removeChild(elementsContainer);
        renderer.dispose();
      };
    };

    const transform = (targets, duration) => {
      // Cancel existing tweens
      tweensRef.current.forEach(tween => {
        if (tween.stop) tween.stop();
      });
      tweensRef.current = [];

      const objects = objectsRef.current;
      const camera = cameraRef.current;
      
      // Adjust camera distance based on formation type
      let targetCameraZ = 2500;
      if (targets === targetsRef.current.table) {
        targetCameraZ = 1800; // Closer for table view
      } else if (targets === targetsRef.current.sphere) {
        targetCameraZ = 2500;
      } else if (targets === targetsRef.current.helix) {
        targetCameraZ = 2500;
      } else if (targets === targetsRef.current.grid) {
        targetCameraZ = 3000;
      }
      
      // Animate camera position
      const cameraStartZ = camera.position.z;
      const cameraStartTime = Date.now();
      
      const cameraAnimation = {
        update: () => {
          const elapsed = Date.now() - cameraStartTime;
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          
          camera.position.z = cameraStartZ + (targetCameraZ - cameraStartZ) * eased;
          
          return progress < 1;
        },
        stop: () => {}
      };
      tweensRef.current.push(cameraAnimation);
      
      objects.forEach((object, i) => {
        const target = targets[i];
        const startPos = {
          x: object.position.x,
          y: object.position.y,
          z: object.position.z,
          rx: object.rotation.x,
          ry: object.rotation.y,
          rz: object.rotation.z
        };

        const startTime = Date.now();
        const randomDelay = Math.random() * duration;

        const tween = {
          update: () => {
            const elapsed = Date.now() - startTime - randomDelay;
            if (elapsed < 0) return true;
            
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // Cubic ease out

            object.position.x = startPos.x + (target.position.x - startPos.x) * eased;
            object.position.y = startPos.y + (target.position.y - startPos.y) * eased;
            object.position.z = startPos.z + (target.position.z - startPos.z) * eased;
            object.rotation.x = startPos.rx + (target.rotation.x - startPos.rx) * eased;
            object.rotation.y = startPos.ry + (target.rotation.y - startPos.ry) * eased;
            object.rotation.z = startPos.rz + (target.rotation.z - startPos.rz) * eased;

            return progress < 1;
          },
          stop: () => {}
        };

        tweensRef.current.push(tween);
      });
    };

    const cleanup = init();

    // Button handlers
    window.transformToTable = () => transform(targetsRef.current.table, 2000);
    window.transformToSphere = () => transform(targetsRef.current.sphere, 2000);
    window.transformToHelix = () => transform(targetsRef.current.helix, 2000);
    window.transformToGrid = () => transform(targetsRef.current.grid, 2000);

    return () => {
      cleanup();
    };
  }, []);

  return (
    <div className="relative w-full h-full bg-black overflow-hidden">
      <style>{`
        .element {
          transition: background-color 0.5s, box-shadow 0.5s, border 0.5s;
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
        }
        
        .element:hover {
          transform: scale(1.02);
        }
      `}</style>
      
      <div ref={containerRef} className="w-full h-full" />
      
    </div>
  );
};

export default DSMPeriodicTable;