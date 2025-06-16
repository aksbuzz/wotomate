import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  input: './openapi.yaml',
  output: {
    format: 'prettier',
    lint: 'eslint',
    path: 'src/client',
  },
  plugins: ['@hey-api/client-fetch', '@tanstack/react-query'],
})
