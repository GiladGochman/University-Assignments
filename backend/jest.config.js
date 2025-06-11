/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  setupFiles: ['dotenv/config'],
  testTimeout: 20000,
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
};
