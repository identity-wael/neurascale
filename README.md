# **Neurascale: Neural Data Cloud Platform**

## **1. Overview**

Neurascale is a cutting-edge web application built with Next.js and React, designed to provide a robust platform for storing, processing, and analyzing neural data at scale. It offers a scalable cloud infrastructure, advanced neural processing capabilities, and real-time analytics to empower researchers and institutions in the field of neuroscience.

This document provides a comprehensive guide for developers and contributors to the Neurascale project.

## **Project Structure**

This repository is organized as follows:

```
/
├── webapp/              # Next.js web application (Neurascale platform)
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   ├── public/         # Static assets
│   ├── package.json    # Web app dependencies
│   └── ...             # Other Next.js config files
├── README.md           # This file
├── AGENTS.md          # Development guidelines
└── .gitignore         # Git ignore rules
```

**Note:** The main web application is located in the `webapp/` directory. All development commands should be run from within that directory.

-----

## **2. Key Features**

The platform boasts a range of features designed to streamline neural data management:

  * **Advanced Neural Processing:** Utilizes state-of-the-art algorithms for efficient data analysis.
  * **Scalable Cloud Infrastructure:** Capable of storing and managing petabytes of neural data.
  * **Real-time Analytics:** Provides powerful tools to gain immediate insights from neural data.
  * **User Authentication:** Secure sign-up, login, and profile management for users.

-----

## **3. Getting Started**

### **3.1. Prerequisites**

Before you begin, ensure you have the following installed on your local machine:

  * Node.js (version 18.17.0 or higher)
  * A package manager like `npm`, `yarn`, `pnpm`, or `bun`

### **3.2. Installation and Setup**

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd neurascale
    ```

2.  **Navigate to the web application:**

    ```bash
    cd webapp
    ```

3.  **Install dependencies:**
    Choose one of the following commands based on your package manager:

    ```bash
    npm install
    # or
    yarn install
    # or
    pnpm install
    # or
    bun install
    ```

4.  **Run the development server:**

    ```bash
    npm run dev
    # or
    yarn dev
    # or
    pnpm dev
    # or
    bun dev
    ```

5.  **Open the application:**
    Open [http://localhost:3000](http://localhost:3000) in your browser to see the running application.

-----

## **4. Developer Guidelines**

### **4.1. Code Style**

To maintain code consistency and quality, please adhere to the following guidelines as outlined in `AGENTS.md`:

  * **TypeScript:** All components and logic should be written in TypeScript.
  * **React:** Use functional components and React Hooks for building UI elements.
  * **Styling:** Use Tailwind CSS for all styling purposes. The configuration is available in `tailwind.config.ts`.

### **4.2. Linting**

Before committing any changes, navigate to the webapp directory and run the linter to check for code quality and style issues:

```bash
cd webapp
npm run lint
```

This command uses Next.js's built-in ESLint configuration to analyze the codebase.

-----

## **5. Project Structure**

The project follows a standard Next.js `app` directory structure within the `webapp/` folder. Here are some of the key files and directories:

  * **`webapp/app/`**: Contains the core application, with each sub-directory mapping to a URL route.
      * **`layout.tsx`**: The main layout that wraps all pages, including the `AuthProvider`.
      * **`page.tsx`**: The main landing page of the application.
      * **`login/page.tsx`**: The login page component.
      * **`signup/page.tsx`**: The signup page component.
      * **`profile/page.tsx`**: The user profile page, which is a protected route.
  * **`webapp/components/`**: Contains reusable React components.
      * **`AuthProvider.tsx`**: A client-side component that manages user authentication state.
      * **`ui/`**: Directory for reusable UI elements like `Button` and `Card`.
  * **`webapp/public/`**: For static assets like images and fonts.
  * **`webapp/package.json`**: Defines project scripts and dependencies.

-----

## **6. Authentication**

Neurascale uses a client-side authentication system managed by the `AuthProvider` component.

### **6.1. How It Works**

  * The `AuthProvider` uses React's `Context` API to provide authentication state (`user`) and functions (`login`, `signup`, `logout`) to all components wrapped within it.
  * User data is stored in the browser's `localStorage` to persist the session across page reloads.
  * The `useAuth` hook provides a simple way for components to access the authentication context.

### **6.2. Protected Routes**

The `ProfilePage` (`/profile`) is an example of a protected route. It uses a `useEffect` hook to check if a user is logged in. If not, it redirects them to the login page.

-----

## **7. Building and Deployment**

### **7.1. Building for Production**

To create a production-ready build of the application, navigate to the webapp directory and run:

```bash
cd webapp
npm run build
```

This will generate an optimized build in the `webapp/.next` directory.

### **7.2. Deployment**

The `README.md` recommends deploying the application on the [Vercel Platform](https://vercel.com/new), which is designed for seamless Next.js deployments. For more details, refer to the [Next.js deployment documentation](https://nextjs.org/docs/deployment).

-----

This documentation provides a comprehensive starting point for any developer looking to contribute to the Neurascale project. For more specific questions, please refer to the source code and the official Next.js documentation.
