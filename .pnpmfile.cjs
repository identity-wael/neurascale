function readPackage(pkg, context) {
  // Override prismjs to fix DOM Clobbering vulnerability
  if (pkg.dependencies && pkg.dependencies.prismjs) {
    pkg.dependencies.prismjs = '^1.30.0';
    context.log(`Overriding prismjs version for ${pkg.name} from ${pkg.dependencies.prismjs} to ^1.30.0`);
  }

  if (pkg.devDependencies && pkg.devDependencies.prismjs) {
    pkg.devDependencies.prismjs = '^1.30.0';
    context.log(`Overriding prismjs devDependency version for ${pkg.name} from ${pkg.devDependencies.prismjs} to ^1.30.0`);
  }

  // Also check nested dependencies
  if (pkg.name === 'refractor' && pkg.dependencies && pkg.dependencies.prismjs) {
    pkg.dependencies.prismjs = '^1.30.0';
    context.log(`Overriding prismjs version in refractor dependency to ^1.30.0`);
  }

  return pkg;
}

module.exports = {
  hooks: {
    readPackage
  }
};
