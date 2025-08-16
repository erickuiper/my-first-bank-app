module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  rules: {
    'no-unused-vars': ['warn', { 'varsIgnorePattern': '^_', 'argsIgnorePattern': '^_' }],
    'no-console': 'warn',
    'prefer-const': 'warn',
  },
  ignorePatterns: ['**/*.ts', '**/*.tsx', 'dist/**/*', 'node_modules/**/*'], // Ignore TypeScript files, dist, and node_modules
};
