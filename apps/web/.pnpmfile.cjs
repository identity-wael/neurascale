module.exports = {
  hooks: {
    readPackage(pkg) {
      // Force prismjs to version 1.30.0 or higher
      if (pkg.dependencies && pkg.dependencies.prismjs) {
        pkg.dependencies.prismjs = "^1.30.0";
      }
      if (pkg.devDependencies && pkg.devDependencies.prismjs) {
        pkg.devDependencies.prismjs = "^1.30.0";
      }
      return pkg;
    }
  }
};
