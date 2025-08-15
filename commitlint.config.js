module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Enforce conventional commit format
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation changes
        'style',    // Code style changes (formatting, missing semicolons, etc)
        'refactor', // Code refactoring
        'perf',     // Performance improvements
        'test',     // Adding or updating tests
        'chore',    // Maintenance tasks, dependencies, etc
        'ci',       // CI/CD changes
        'build',    // Build system changes
        'revert',   // Revert previous commit
        'wip',      // Work in progress
        'skip'      // Skip checks (emergency overrides)
      ]
    ],
    'type-case': [2, 'always', 'lower'],
    'type-empty': [2, 'never'],
    'subject-case': [2, 'always', 'lower'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'subject-max-length': [2, 'always', 72],
    'body-leading-blank': [2, 'always'],
    'body-max-line-length': [2, 'always', 100],
    'footer-leading-blank': [2, 'always'],
    'footer-max-line-length': [2, 'always', 100]
  }
};
