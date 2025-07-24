function readPackage(pkg) {
  // Override prismjs to fix DOM Clobbering vulnerability
  if (pkg.dependencies && pkg.dependencies.prismjs) {
    pkg.dependencies.prismjs = '^1.30.0';
  }

  if (pkg.devDependencies && pkg.devDependencies.prismjs) {
    pkg.devDependencies.prismjs = '^1.30.0';
  }

  // Also check nested dependencies
  if (pkg.name === 'refractor' && pkg.dependencies && pkg.dependencies.prismjs) {
    pkg.dependencies.prismjs = '^1.30.0';
  }

  return pkg;
}

module.exports = {
  hooks: {
    readPackage
  }
};
