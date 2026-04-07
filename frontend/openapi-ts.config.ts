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
      asClass: true,
      // operationId: true,
      classNameBuilder: '{{name}}Service',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      methodNameBuilder: (operation: any) => {
        let name: string = operation.id
        const service: string = operation.tags?.[0] ?? ''

        console.log('operation', operation)

        if (service && name.toLowerCase().startsWith(service.toLowerCase())) {
          name = name.slice(service.length)
        }

        return name.charAt(0).toLowerCase() + name.slice(1)
      },
    },
  ],
});
