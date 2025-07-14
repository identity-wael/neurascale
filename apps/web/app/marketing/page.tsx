'use client';

import React, {
  useState,
  type FC,
  type ReactNode,
  type Dispatch,
  type SetStateAction,
} from 'react';
import {
  BrainCircuit,
  Cpu,
  ShieldCheck,
  Bot,
  Eye,
  Users,
  Scale,
  Brain,
  Dna,
  CloudCog,
} from 'lucide-react';

interface PageProps {
  setCurrentPage: Dispatch<SetStateAction<string>>;
}

interface HeaderProps extends PageProps {
  currentPage: string;
}

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}

interface InfoCardProps {
  title: string;
  description: string;
}

interface LayerCardProps {
  icon: ReactNode;
  title: string;
  description: string;
}

interface ProjectCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  timeline: string;
  milestone: string;
  reverse?: boolean;
}

interface MLPhaseCardProps {
  phase: string;
  title: string;
  description: string;
}

interface EthicsPointProps {
  icon: ReactNode;
  title: string;
  description: string;
}

const App: FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('home');

  const pages: { [key: string]: ReactNode } = {
    home: <HomePage setCurrentPage={setCurrentPage} />,
    platform: <PlatformPage />,
    applications: <ApplicationsPage />,
    technology: <TechnologyPage />,
    ethics: <EthicsPage />,
    about: <AboutPage />,
  };

  return (
    <div className="bg-gray-900 text-gray-200 font-sans">
      <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="pt-20">{pages[currentPage]}</main>
      <Footer setCurrentPage={setCurrentPage} />
    </div>
  );
};

const Header: FC<HeaderProps> = ({ currentPage, setCurrentPage }) => {
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  const navLinks = [
    { id: 'home', title: 'Home' },
    { id: 'platform', title: 'Platform' },
    { id: 'applications', title: 'Applications' },
    { id: 'technology', title: 'Technology' },
    { id: 'ethics', title: 'Ethics & Security' },
    { id: 'about', title: 'About Us' },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 bg-gray-900 bg-opacity-80 backdrop-blur-md z-50 shadow-lg">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div
          className="flex items-center space-x-2 cursor-pointer"
          onClick={() => setCurrentPage('home')}
        >
          {/* keep logo consistent with existing site */}
          <span
            className="font-extrabold text-2xl tracking-wider"
            style={{ fontFamily: 'Proxima Nova, sans-serif' }}
          >
            <span className="text-[#eeeeee]">NEURA</span>
            <span className="text-[#4185f4]">SCALE</span>
          </span>
        </div>
        <nav className="hidden md:flex space-x-8">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => setCurrentPage(link.id)}
              className={`text-lg font-medium transition-colors duration-300 ${
                currentPage === link.id ? 'text-cyan-400' : 'text-gray-300 hover:text-cyan-400'
              }`}
            >
              {link.title}
            </button>
          ))}
        </nav>
        <div className="md:hidden">
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="text-white focus:outline-none"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d={isMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16m-7 6h7'}
              />
            </svg>
          </button>
        </div>
      </div>
      {isMenuOpen && (
        <div className="md:hidden bg-gray-800">
          <nav className="flex flex-col items-center px-4 pt-2 pb-4 space-y-2">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => {
                  setCurrentPage(link.id);
                  setIsMenuOpen(false);
                }}
                className={`w-full text-center py-2 rounded-md text-lg font-medium transition-colors duration-300 ${
                  currentPage === link.id
                    ? 'bg-cyan-500 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                {link.title}
              </button>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
};

const HomePage: FC<PageProps> = ({ setCurrentPage }) => {
  return (
    <div>
      {/* Hero Section */}
      <section
        className="relative h-screen flex items-center justify-center text-center bg-cover bg-center"
        style={{
          backgroundImage:
            "url('https://placehold.co/1920x1080/0a0a0a/ffffff?text=Neural+Network')",
        }}
      >
        <div className="absolute inset-0 bg-black opacity-60"></div>
        <div className="relative z-10 px-4">
          <h2 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-4">
            Bridging Mind and World
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto mb-8">
            Pioneering advanced neural cloud technology to revolutionize human-computer interaction,
            restore mobility, and unlock truly immersive virtual experiences.
          </p>
          <button
            onClick={() => setCurrentPage('platform')}
            className="bg-cyan-500 text-white font-bold py-3 px-8 rounded-full text-lg hover:bg-cyan-600 transition-transform duration-300 transform hover:scale-105"
          >
            Explore The Platform
          </button>
        </div>
      </section>

      {/* Vision Section */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6 text-center">
          <h3 className="text-4xl font-bold mb-4 text-white">
            Our Vision: The Future of Interaction
          </h3>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto">
            Our goal is to blur the boundaries between the human mind and the real world, enabling
            communication at the speed of thought. We are building the infrastructure to make this a
            reality.
          </p>
        </div>
      </section>

      {/* Core Applications Section */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <h3 className="text-4xl font-bold text-center mb-12 text-white">
            Groundbreaking Applications
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Bot className="h-12 w-12 text-cyan-400" />}
              title="NeuroProsthetics"
              description="Restoring mobility and function with robotic limbs controlled directly by the mind, offering new hope and possibilities."
              onClick={() => setCurrentPage('applications')}
            />
            <FeatureCard
              icon={<Users className="h-12 w-12 text-cyan-400" />}
              title="Brain Swarm Interface"
              description="Commanding swarms of autonomous robots with neural intent for complex automation tasks in the physical world."
              onClick={() => setCurrentPage('applications')}
            />
            <FeatureCard
              icon={<Eye className="h-12 w-12 text-cyan-400" />}
              title="Full Dive VR"
              description="Achieving true immersion in virtual realities, where experiences are encoded and decoded in real-time."
              onClick={() => setCurrentPage('applications')}
            />
          </div>
        </div>
      </section>

      {/* Platform Highlight Section */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <h3 className="text-4xl font-bold text-center mb-12 text-white">
            A Specialized Neural Cloud
          </h3>
          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-10 items-center">
            <div className="text-center md:text-left">
              <p className="text-lg text-gray-400 mb-6">
                General-purpose clouds can&apos;t handle the unique demands of neural data.
                NeuraScale provides a purpose-built platform with tailored infrastructure for
                real-time signal processing, advanced machine learning, and robust security.
              </p>
              <button
                onClick={() => setCurrentPage('platform')}
                className="border-2 border-cyan-400 text-cyan-400 font-bold py-3 px-8 rounded-full text-lg hover:bg-cyan-400 hover:text-gray-900 transition-colors duration-300"
              >
                Learn More
              </button>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gray-800 p-6 rounded-lg text-center">
                <Cpu className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
                <h4 className="font-semibold text-white">Real-Time Processing</h4>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg text-center">
                <BrainCircuit className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
                <h4 className="font-semibold text-white">ML Integration</h4>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg text-center">
                <ShieldCheck className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
                <h4 className="font-semibold text-white">Unmatched Security</h4>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg text-center">
                <Scale className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
                <h4 className="font-semibold text-white">FAIR Data Principles</h4>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

const PlatformPage: FC = () => {
  return (
    <div className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-center mb-4 text-white">
          The NeuraScale Platform
        </h2>
        <p className="text-xl text-center text-gray-400 max-w-4xl mx-auto mb-16">
          A specialized cloud platform purpose-built for the unique challenges of processing,
          curating, and analyzing large-scale neural data.
        </p>

        {/* System Components */}
        <section className="mb-20">
          <h3 className="text-4xl font-bold text-center mb-12 text-white">
            Core System Components
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <InfoCard
              title="Neural Management System"
              description="The central nervous system of our platform, orchestrating data flow and processing."
            />
            <InfoCard
              title="Neural Ledger"
              description="Ensures data integrity and provides a secure, auditable record of neural data transactions."
            />
            <InfoCard
              title="Extended Reality Engine"
              description="Powers immersive VR/XR experiences, rendering virtual worlds from neural intent."
            />
            <InfoCard
              title="Neural Applications"
              description="The suite of tools and services that translate neural signals into real-world action."
            />
          </div>
        </section>

        {/* Layered Architecture */}
        <section className="mb-20">
          <h3 className="text-4xl font-bold text-center mb-12 text-white">
            A Full-Stack Architecture
          </h3>
          <div className="max-w-4xl mx-auto space-y-8">
            <LayerCard
              title="Neural Interaction & Immersion Layer (NIIL)"
              description="The user-facing layer for advanced engagement. Includes analytics, neural identity, mixed reality interfaces, and cognitive biometric authentication."
              icon={<Brain className="h-10 w-10 text-cyan-400" />}
            />
            <LayerCard
              title="Emulation Layer"
              description="A crucial intermediary that handles the simulation and translation of neural signals, ensuring seamless interaction between mind and machine."
              icon={<Users className="h-10 w-10 text-cyan-400" />}
            />
            <LayerCard
              title="Physical Integration & Control Layer (PICL)"
              description="Directly interfaces with physical devices like robotic limbs and sensor arrays. Manages device telemetry, identity, and fleet control."
              icon={<Bot className="h-10 w-10 text-cyan-400" />}
            />
          </div>
        </section>

        {/* Technology Backbone */}
        <section>
          <h3 className="text-4xl font-bold text-center mb-12 text-white">Technology Backbone</h3>
          <div className="grid md:grid-cols-2 gap-12">
            <div className="bg-gray-800 p-8 rounded-lg">
              <h4 className="text-3xl font-bold mb-4 text-white">Built on AWS</h4>
              <p className="text-gray-400 mb-6">
                We leverage a suite of AWS services for robust, scalable, and secure edge and cloud
                computing, ensuring real-time data processing and device management at scale.
              </p>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-center">
                  <CloudCog className="h-5 w-5 mr-3 text-cyan-400" /> AWS IoT GreenGrass & Core
                </li>
                <li className="flex items-center">
                  <CloudCog className="h-5 w-5 mr-3 text-cyan-400" /> AWS IoT Device Management
                </li>
                <li className="flex items-center">
                  <CloudCog className="h-5 w-5 mr-3 text-cyan-400" /> AWS IoT RoboRunner & FleetWise
                </li>
              </ul>
            </div>
            <div className="bg-gray-800 p-8 rounded-lg">
              <h4 className="text-3xl font-bold mb-4 text-white">Powered by Nvidia</h4>
              <p className="text-gray-400 mb-6">
                Nvidia&apos;s advanced AI and XR platforms provide the computational horsepower for
                our most demanding tasks, from AI model training to real-time virtual world
                rendering.
              </p>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-center">
                  <Cpu className="h-5 w-5 mr-3 text-cyan-400" /> Nvidia OmniVerse & XR
                </li>
                <li className="flex items-center">
                  <Cpu className="h-5 w-5 mr-3 text-cyan-400" /> Nvidia Holoscan & DGX Cloud
                </li>
                <li className="flex items-center">
                  <Cpu className="h-5 w-5 mr-3 text-cyan-400" /> Nvidia AI Enterprise Stack
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

const ApplicationsPage: FC = () => {
  return (
    <div className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-center mb-4 text-white">Powering Innovation</h2>
        <p className="text-xl text-center text-gray-400 max-w-4xl mx-auto mb-16">
          Our Neural Platform as a Service is the foundation for three ambitious R&D projects, each
          targeting a distinct frontier in neurotechnology.
        </p>

        <div className="space-y-16">
          <ProjectCard
            title="NeuroProsthetics: Restoring Mobility"
            description="This project aims to create a direct connection between the mind and robotic limbs. By calculating the precise angles and torques for each joint in real-time, we enable adaptive control of complex multi-joint systems, allowing for smooth, intended motion."
            timeline="5 Years"
            milestone="FDA Approval"
            icon={<Bot className="h-16 w-16 text-cyan-400" />}
          />
          <ProjectCard
            title="Brain Swarm Interface: Command at the Speed of Thought"
            description="Focused on instantaneous control of agentic robotic swarms. We are developing a SaaS layer that extends the Robotic Operating System (ROS) to support a user's neural intent, enabling complex automation tasks in the physical world."
            timeline="2 Years"
            milestone="Product Release (2028)"
            icon={<Users className="h-16 w-16 text-cyan-400" />}
            reverse={true}
          />
          <ProjectCard
            title="Full Dive VR: Unlocking Immersive Realities"
            description="Our most ambitious long-term goal: full immersion into virtual worlds. This involves real-time encoding and decoding of experiences, creating a seamless link between neural intent, virtual action, and visual rendering."
            timeline="10 Years"
            milestone="Product Release (2028)"
            icon={<Eye className="h-16 w-16 text-cyan-400" />}
          />
        </div>
      </div>
    </div>
  );
};

const TechnologyPage: FC = () => {
  return (
    <div className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-center mb-4 text-white">
          Intelligence at the Core
        </h2>
        <p className="text-xl text-center text-gray-400 max-w-4xl mx-auto mb-16">
          Our platform integrates machine learning across four distinct phases to turn complex
          neural data into actionable intelligence.
        </p>

        <div className="grid md:grid-cols-2 gap-8">
          <MLPhaseCard
            phase="1"
            title="Understanding the Data"
            description="We process intricate, multi-channel neural data, combining it with motion data and patient metadata. Preprocessing techniques and feature extraction like PCA are used to uncover hidden correlations between brain activity and outcomes."
          />
          <MLPhaseCard
            phase="2"
            title="Making Predictions"
            description="Using algorithms like RNNs, Kalman Filters, and Transformers, we predict intended movements from neural signals. This allows assistive devices to match a user's intent, not their physical limitation."
          />
          <MLPhaseCard
            phase="3"
            title="Making Decisions"
            description="In a dynamic environment, our models translate predictions into control. Using supervised and reinforcement learning, the system adapts and improves over time, while keeping human experts, like physicians, in the loop for critical decisions."
          />
          <MLPhaseCard
            phase="4"
            title="Making Causal Inferences"
            description="We go beyond correlation to understand causation. Through randomized control trials and time-series analysis like Granger Causality, we evaluate the true causal effect of BCI interventions on functional improvements."
          />
        </div>
      </div>
    </div>
  );
};

const EthicsPage: FC = () => {
  return (
    <div className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-center mb-4 text-white">
          Safeguarding the Future
        </h2>
        <p className="text-xl text-center text-gray-400 max-w-4xl mx-auto mb-16">
          Neural data is incredibly sensitive. We recognize that ensuring its protection and ethical
          use is paramount to our mission and the future of neurotechnology.
        </p>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <EthicsPoint
              icon={<ShieldCheck className="h-8 w-8 text-cyan-400" />}
              title="Data Security & Privacy"
              description="We implement robust encryption, stringent access controls, and continuous monitoring to protect data from breaches and misuse. Our platform is designed for compatibility with HIPAA and GDPR."
            />
            <EthicsPoint
              icon={<Dna className="h-8 w-8 text-cyan-400" />}
              title="Informed Consent"
              description="Transparency is key. We establish clear policies on how data is collected, used, and shared. Users are always fully aware of the implications and must provide informed consent."
            />
            <EthicsPoint
              icon={<Scale className="h-8 w-8 text-cyan-400" />}
              title="Bias Mitigation"
              description="We actively work to identify and mitigate potential biases in neural data to ensure that our technology does not reinforce harmful stereotypes or lead to unfair treatment."
            />
          </div>
          <div className="bg-gray-800 p-10 rounded-lg shadow-lg">
            <h3 className="text-3xl font-bold text-white mb-4">Our Ethical Commitment</h3>
            <p className="text-gray-300 text-lg">
              We are harnessing the power of neural data for the betterment of society. This
              requires navigating the complexities of a rapidly evolving field with a proactive and
              ethical stance. By embedding privacy and security into our design from the ground up,
              we build trust and position ourselves as a responsible leader in neurotechnology.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const AboutPage: FC = () => {
  return (
    <div className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <h2 className="text-5xl font-extrabold text-center mb-4 text-white">About NeuraScale.io</h2>
        <p className="text-xl text-center text-gray-400 max-w-4xl mx-auto mb-16">
          We are a deep tech venture committed to architecting the future of human-machine
          interaction through sustained investment and meticulous planning.
        </p>

        {/* Mission Section */}
        <section className="mb-20 text-center">
          <h3 className="text-4xl font-bold mb-4 text-white">Our Mission</h3>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            To seamlessly integrate the human mind with physical and virtual realms, unlocking
            unprecedented possibilities in mobility, automation, and immersive experiences, all
            while upholding the highest standards of data integrity and ethical practice.
          </p>
        </section>

        {/* R&D Investment Section */}
        <section className="mb-20">
          <h3 className="text-4xl font-bold text-center mb-12 text-white">
            Roadmap to Reality: R&D Investment
          </h3>
          <div className="bg-gray-800 rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <p className="text-6xl font-extrabold text-cyan-400">$23.74M</p>
              <p className="text-xl text-gray-400">Total R&D Budget (2025-2028)</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div>
                <p className="text-2xl font-bold text-white">$12.05M</p>
                <p className="text-gray-400">Staffing</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">$7M</p>
                <p className="text-gray-400">R&D</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">$3.95M</p>
                <p className="text-gray-400">Proof of Concept</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">$660K</p>
                <p className="text-gray-400">Research & Tech</p>
              </div>
            </div>
            <p className="text-center text-gray-500 mt-8">
              This sustained, multi-year investment demonstrates our serious commitment to deep
              technology and the long-term execution of our ambitious vision.
            </p>
          </div>
        </section>

        {/* Future Outlook */}
        <section className="text-center">
          <h3 className="text-4xl font-bold mb-4 text-white">Future Outlook</h3>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            Our journey is just beginning. Future research will focus on real-world datasets,
            exploring the limitations of machine learning, and developing even more sophisticated
            models to tackle the complexities of neural data. We are building a platform not just
            for today, but for the future of neuroscience and AI.
          </p>
        </section>
      </div>
    </div>
  );
};

const Footer: FC<PageProps> = ({ setCurrentPage }) => {
  return (
    <footer className="bg-gray-800 text-gray-400">
      <div className="container mx-auto px-6 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <BrainCircuit className="text-cyan-400 h-7 w-7" />
              <h2 className="text-xl font-bold text-white">NeuraScale.io</h2>
            </div>
            <p>Bridging Mind and World.</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Quick Links</h3>
            <ul>
              <li className="mb-2">
                <button
                  onClick={() => setCurrentPage('platform')}
                  className="hover:text-cyan-400 transition-colors"
                >
                  Platform
                </button>
              </li>
              <li className="mb-2">
                <button
                  onClick={() => setCurrentPage('applications')}
                  className="hover:text-cyan-400 transition-colors"
                >
                  Applications
                </button>
              </li>
              <li className="mb-2">
                <button
                  onClick={() => setCurrentPage('ethics')}
                  className="hover:text-cyan-400 transition-colors"
                >
                  Ethics & Security
                </button>
              </li>
              <li className="mb-2">
                <button
                  onClick={() => setCurrentPage('about')}
                  className="hover:text-cyan-400 transition-colors"
                >
                  About Us
                </button>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Contact</h3>
            <p>Based in the United States.</p>
            <p>contact@neurascaledummy.io</p>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-700 pt-6 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} NeuraScale.io. All Rights Reserved.</p>
        </div>
      </div>
    </footer>
  );
};

// Reusable Components
const FeatureCard: FC<FeatureCardProps> = ({ icon, title, description, onClick }) => (
  <div
    className="bg-gray-900 p-8 rounded-lg shadow-lg text-center transform hover:-translate-y-2 transition-transform duration-300 cursor-pointer"
    onClick={onClick}
  >
    <div className="mb-4 inline-block">{icon}</div>
    <h4 className="text-2xl font-bold mb-3 text-white">{title}</h4>
    <p className="text-gray-400">{description}</p>
  </div>
);

const InfoCard: FC<InfoCardProps> = ({ title, description }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-md">
    <h4 className="text-xl font-bold mb-2 text-white">{title}</h4>
    <p className="text-gray-400">{description}</p>
  </div>
);

const LayerCard: FC<LayerCardProps> = ({ title, description, icon }) => (
  <div className="flex items-start space-x-6 bg-gray-800 p-8 rounded-lg shadow-lg">
    <div className="flex-shrink-0 bg-gray-700 p-4 rounded-full">{icon}</div>
    <div>
      <h4 className="text-2xl font-bold text-white mb-2">{title}</h4>
      <p className="text-gray-400">{description}</p>
    </div>
  </div>
);

const ProjectCard: FC<ProjectCardProps> = ({
  title,
  description,
  timeline,
  milestone,
  icon,
  reverse = false,
}) => (
  <div
    className={`flex flex-col md:flex-row items-center gap-12 ${
      reverse ? 'md:flex-row-reverse' : ''
    }`}
  >
    <div className="md:w-1/2 text-center md:text-left">
      <div
        className={`inline-block p-6 bg-gray-800 rounded-full mb-6 ${
          reverse ? 'md:ml-auto' : 'md:mr-auto'
        }`}
      >
        {icon}
      </div>
      <h3 className="text-4xl font-bold text-white mb-4">{title}</h3>
      <p className="text-gray-400 text-lg mb-6">{description}</p>
      <div className="flex flex-col sm:flex-row gap-6">
        <div className="bg-gray-800 p-4 rounded-lg flex-1 text-center">
          <p className="text-cyan-400 text-2xl font-bold">{timeline}</p>
          <p className="text-gray-500">Project Timeline</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg flex-1 text-center">
          <p className="text-cyan-400 text-2xl font-bold">{milestone}</p>
          <p className="text-gray-500">Key Milestone</p>
        </div>
      </div>
    </div>
    <div className="md:w-1/2">
      <img
        src={`https://placehold.co/600x400/1f2937/38bdf8?text=${title.split(':')[0]}`}
        alt={title}
        className="rounded-lg shadow-2xl w-full h-auto"
      />
    </div>
  </div>
);

const MLPhaseCard: FC<MLPhaseCardProps> = ({ phase, title, description }) => (
  <div className="bg-gray-800 p-8 rounded-lg shadow-lg relative">
    <div className="absolute -top-5 -left-5 bg-cyan-500 h-16 w-16 rounded-full flex items-center justify-center text-gray-900 text-3xl font-bold">
      {phase}
    </div>
    <h3 className="text-2xl font-bold text-white mt-8 mb-3">{title}</h3>
    <p className="text-gray-400">{description}</p>
  </div>
);

const EthicsPoint: FC<EthicsPointProps> = ({ icon, title, description }) => (
  <div className="flex items-start space-x-4">
    <div className="flex-shrink-0">{icon}</div>
    <div>
      <h4 className="text-xl font-bold text-white">{title}</h4>
      <p className="text-gray-400">{description}</p>
    </div>
  </div>
);

export default App;
