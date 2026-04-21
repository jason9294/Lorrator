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
      // operationId: true,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      methodNameBuilder: (operation: any) => {
        let name: string = operation.id
        const service: string = operation.tags?.[0] ?? ''

        console.log('operation', operation, typeof operation)
        console.log('service', service, typeof service)
        console.log('name', name, typeof name)

        if (service && name.toLowerCase().startsWith(service.toLowerCase())) {
          name = name.slice(service.length)
        }

        return name.charAt(0).toLowerCase() + name.slice(1)
      },
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
