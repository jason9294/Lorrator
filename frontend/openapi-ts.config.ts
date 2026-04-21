import { defineConfig } from '@hey-api/openapi-ts';

import 'dotenv/config';

const baseUrl = process.env.VITE_API_URL;

export default defineConfig({
  input: `${baseUrl}/openapi.json`,
  output: { path: 'src/services' },
  plugins: [
    { name: '@hey-api/typescript' },
    { name: '@hey-api/client-axios', throwOnError: true, baseUrl: baseUrl },
    {
      name: '@hey-api/sdk',
      operations: {
        strategy: 'byTags',
        containerName: '{{name}}Service',
        methodName: (name) => {
          // find "-" and return the word after it
          const index = name.indexOf('-')
          if (index !== -1) {
            return name.slice(index + 1)
          }
          return name
        },
      },
    },
  ],
});
